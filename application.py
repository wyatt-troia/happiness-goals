from flask import Flask, jsonify, render_template, request, session, flash, redirect, url_for
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, time, timedelta
import plotly.plotly as py
import plotly.graph_objs as go

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure CS50 library to use SQLite database
db = SQL("sqlite:///goals.db")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/checkin", methods=["POST"])
@login_required
def checkin():
    print(request.form)

    now = datetime.now()
    east_coast_now = now - timedelta(hours=4)
    current_week = east_coast_now - timedelta(days=(east_coast_now.weekday() + 1) % 7, hours=east_coast_now.hour, minutes=east_coast_now.minute, seconds=east_coast_now.second, microseconds=east_coast_now.microsecond)
    current_week = current_week.strftime('%Y-%m-%d 00:00:00')


    for k, v in request.form.items():
        if k == "week_starting":
            continue

        # grab goal id
        rows = db.execute("SELECT * FROM goals WHERE name = :name", name=k)
        goal_id = rows[0]["goal_id"]

        week_starting = datetime.strptime(request.form["week_starting"], '%m/%d/%Y')

        # update actual for goal for selected week
        db.execute("UPDATE goal_history SET actual = :actual WHERE user_id = :user_id AND goal_id = :goal_id AND week_starting = :week_starting", actual=v, user_id=session['user_id'], goal_id=goal_id, week_starting=week_starting)
        print (k, v)
    errors = []

    return redirect("/track")

@app.route("/login", methods=["GET", "POST"])
def login():

    # forget any user_id
    session.clear()

    errors = []

    # user reached route via "POST" method (as by submitting a form)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form["username"]:
            errors.append("Username required!")

        # ensure password was submitted
        if not request.form["password"]:
            errors.append["Password required!"]

        # ensure username exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form["username"])
        if not rows:
            errors.append["Username not registered"]
            return render_template("login.html", errors=errors)

        # ensure password is correct for username
        if not check_password_hash(rows[0]["hash"], request.form["password"]):
            errors.append["Incorrect password!"]
            return render_template("login.html", errors=errors)

        # log user in if username exists and password is correct
        session["user_id"] = rows[0]["user_id"]

        # redirect user to home page
        return redirect("/")

    # user reached route via "GET" method (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/")
@login_required
def index():
    return render_template("set.html")

@app.route("/goals")
@login_required
def goals():
    """ Look up goals, to populate goal selection form """

    # grab category GET argument to know which goals to fetch
    category = request.args.get("category")

    # check for missing category argument
    if not category:
        raise RuntimeError("Category argument missing!")

    # grab goals from database that match category
    goals = db.execute("SELECT * FROM goals WHERE category = :category", category=category)

    # return jsonified goals list
    return jsonify(goals)

@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """

    # user reached route via "GET" request (as by clicking a link or via redirect)
    if request.method == "GET":

        # render register form
        return render_template("register.html")

    # user reached route via "POST" request (as by submitting a form)
    else:
        errors = []

        # ensure username was submitted
        if not request.form["username"]:
            errors.append("Username required!")

        # ensure password was submitted
        if not request.form["password"]:
            errors.append("Password required!")

        # ensure password confirmation was submitted
        if not request.form["pw_confirmation"]:
            errors.append("Password confirmation required!")

        # ensure password and password confirmation match
        if not request.form["password"] == request.form["pw_confirmation"]:
            errors.append("Password and password confirmation must match!")

        # if there were errors, re-render register template with error warnings
        if errors:
            return render_template("register.html", errors=errors)

        # hash password
        hash = generate_password_hash(request.form["password"], method='pbkdf2:sha256', salt_length=8)

        # try to add user to database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form["username"], hash=hash)

        # ask user to try another username if desired username is already taken
        if not result:
            errors.append("Username already exists. Please choose another.")
            return render_template("register.html", errors=errors)

        # log user in if successfully added to database
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form["username"])
        session["user_id"] = rows[0]["id"]

        # redirect to home page after registration
        return redirect("/")

@app.route("/add_goal", methods=['GET', 'POST'])
@login_required
def add_goal():

    # user reached route via "GET" request (as by clicking a link or via redirect)
    if request.method == "GET":

        # redirect to goal setting route
        return redirect("/set")

    # user reached route via "POST" request (as by submitting a form)
    else:
        print("request: {}".format(request.form))

        errors = []

        # if custom goal, add goal to goals table
        if request.form["custom"] == 'true':
            db.execute("INSERT INTO goals (category, name) VALUES (:category, :name)", category='other', name=request.form["name"])

        # get goal_id from goals table
        rows = db.execute("SELECT * FROM goals WHERE name = :name", name=request.form["name"])
        goal_id = rows[0]["goal_id"]

        print(request.form["week_starting"])

        # check for whether user already has goal
        user_goals_rows = db.execute("SELECT * FROM user_goals WHERE user_id = :user_id AND goal_id = :goal_id", user_id=session["user_id"], goal_id=goal_id)

        # if user already has goal
        if user_goals_rows:

            # remember old target for use in any missing past goal_history weeks we need to create
            old_target = user_goals_rows[0]['frequency']

            # update user_goals table with new target
            db.execute("UPDATE user_goals SET frequency = :frequency WHERE user_id = :user_id AND goal_id = :goal_id", user_id=session["user_id"], goal_id=goal_id, frequency=request.form["frequency"])

            # ensure tracking period has started (using Eastern Standard Time NEED TO ACCOUNT FOR DAYLIGHT SAVINGS TIME)
            start_tracking = user_goals_rows[0]["start_tracking"]
            start_tracking = datetime.strptime(start_tracking, '%Y-%m-%d 00:00:00')
            now = datetime.now()
            east_coast_now = now - timedelta(hours=4)

            # if tracking period has started, check for whether goal history rows have been created up to current week and create any missing ones
            if east_coast_now >= start_tracking:

                print("tracking period has started")

                # check if goal_history row exists for current week
                goal_history_rows = db.execute("SELECT * FROM goal_history WHERE user_id = :user_id AND goal_id = :goal_id ORDER BY week_starting DESC LIMIT 1", user_id=session["user_id"], goal_id=goal_id)
                current_week = east_coast_now - timedelta(days=(east_coast_now.weekday() + 1) % 7, hours=east_coast_now.hour, minutes=east_coast_now.minute, seconds=east_coast_now.second, microseconds=east_coast_now.microsecond)
                current_week = current_week.strftime('%Y-%m/%d 00:00:00')

                # if goal row for this week exists (if user has already accessed TRACK in the current week or created goal this week), update it (all needed past rows should already exist)
                most_recent_week_starting = goal_history_rows[0]["week_starting"]
                if most_recent_week_starting == current_week:
                    print("229")
                    db.execute("UPDATE goal_history SET target = :target WHERE user_id = :user_id AND goal_id = :goal_id AND week_starting = :week_starting", user_id=session["user_id"], goal_id=goal_id, week_starting=current_week, target=int(request.form["frequency"]));

                # if goal_history row for this week doesn't exist, create rows for all weeks from most recent row to current week
                else:
                    print("234")
                    most_recent_week_starting_datetime = datetime.strptime(most_recent_week_starting,'%Y-%m/%d 00:00:00')
                    most_recent_week_starting_datetime += timedelta(days=7)
                    while (most_recent_week_starting_datetime.strftime('%Y-%m-%d 00:00:00') != current_week):
                        week_starting_to_add = most_recent_week_starting_datetime.strftime('%Y-%m-%d 00:00:00')
                        db.execute("INSERT INTO goal_history (user_id, goal_id, week_starting, target) VALUES (:user_id, :goal_id, :week_starting, :target)", user_id=session["user_id"], goal_id=goal_id, week_starting=week_starting_to_add, target=old_target)
                        most_recent_week_starting_datetime += timedelta(days=7)
                    db.execute("INSERT INTO goal_history (user_id, goal_id, week_starting, target) VALUES (:user_id, :goal_id, :week_starting, :target)", user_id=session["user_id"], goal_id=goal_id, week_starting=current_week, target=int(request.form["frequency"]))

                errors.append("You've tried to set a goal that you've already set, so we've updated your target frequency starting this week with the value you selected.")
                # return redirect('/track', errors=errors)
                return redirect(url_for('track', errors=errors))

            # if tracking period hasn't started, simply update the one goal_history row that was created for the first week of the tracking period when the goal was created
            else:
                print("248")
                db.execute("UPDATE goal_history SET target = :target WHERE user_id = :user_id AND goal_id = :goal_id", user_id=session["user_id"], goal_id=goal_id, target=int(request.form["frequency"]))
                errors.append("You've tried to set a goal that you've already set and whose tracking period hasn't started yet. We've updated your target frequency with the value you selected.")
                return render_template('track.html', errors=errors)

        # if user does not have goal
        else:
            week_starting = datetime.strptime(request.form["week_starting"], '%m/%d/%Y')



            # if user doesn't have goal, add goal to user_goals table
            db.execute("INSERT INTO user_goals (user_id, goal_id, frequency, start_tracking) VALUES (:user_id, :goal_id, :frequency, :start_tracking)", user_id=session["user_id"], goal_id=goal_id, frequency=request.form["frequency"], start_tracking=week_starting)

            # and add goal to goal_history table
            db.execute("INSERT INTO goal_history (user_id, goal_id, week_starting, target) VALUES (:user_id, :goal_id, :week_starting, :target)", user_id=session["user_id"], goal_id=goal_id, week_starting=week_starting, target=int(request.form["frequency"]))

        return redirect("/track")

@app.route("/track")
@login_required
def track():

    # grab user goals from database
    user_goals = db.execute("SELECT * FROM user_goals INNER JOIN goals ON user_goals.goal_id=goals.goal_id WHERE user_id = :user_id", user_id=session["user_id"])

    # for each goal in tracking period, add any missing goal_history rows to make table current to current week
    now = datetime.now()
    east_coast_now = now - timedelta(hours=4)
    for user_goal in user_goals:
        start_tracking = user_goal["start_tracking"]
        start_tracking = datetime.strptime(start_tracking, '%Y-%m-%d 00:00:00')

        if east_coast_now >= start_tracking:

            goal_history_rows = db.execute("SELECT * FROM goal_history WHERE user_id = :user_id AND goal_id = :goal_id ORDER BY week_starting DESC LIMIT 1", user_id=session["user_id"], goal_id=user_goal["goal_id"])
            most_recent_week_starting = goal_history_rows[0]["week_starting"]
            print(east_coast_now)
            print(east_coast_now.weekday())
            current_week = east_coast_now - timedelta(days=(east_coast_now.weekday() + 1) % 7, hours=east_coast_now.hour, minutes=east_coast_now.minute, seconds=east_coast_now.second, microseconds=east_coast_now.microsecond)
            print(current_week)
            current_week = current_week.strftime('%Y-%m-%d 00:00:00')
            print(most_recent_week_starting)
            print(current_week)

            # if most recent week in goal_history is not current week, add missing rows with 0's for actuals
            if most_recent_week_starting != current_week:
                most_recent_week_starting_datetime = datetime.strptime(most_recent_week_starting,'%Y-%m-%d 00:00:00')
                most_recent_week_starting_datetime += timedelta(days=7)
                while (most_recent_week_starting_datetime.strftime('%Y-%m-%d 00:00:00') != current_week):
                    week_starting_to_add = most_recent_week_starting_datetime.strftime('%Y-%m-%d 00:00:00')
                    db.execute("INSERT INTO goal_history (user_id, goal_id, week_starting, target) VALUES (:user_id, :goal_id, :week_starting, :target)", user_id=session["user_id"], goal_id=user_goal["goal_id"], week_starting=week_starting_to_add, target=user_goal["frequency"])
                    most_recent_week_starting_datetime += timedelta(days=7)
                week_starting_to_add = most_recent_week_starting_datetime.strftime('%Y-%m-%d 00:00:00')
                db.execute("INSERT INTO goal_history (user_id, goal_id, week_starting, target) VALUES (:user_id, :goal_id, :week_starting, :target)", user_id=session["user_id"], goal_id=user_goal["goal_id"], week_starting=week_starting_to_add, target=user_goal["frequency"])

    # grab user's goal_history rows
    goals = db.execute("SELECT DISTINCT name, goal_history.goal_id FROM goal_history INNER JOIN goals ON goal_history.goal_id=goals.goal_id WHERE user_id=:user_id", user_id=session['user_id'])
    print('goals 305')
    print(goals)

    if len(goals) == 0:
        return render_template("track.html", errors=["Once you set a goal, you will track it here!"])

    achievement_rate_by_goal = {}
    tracking = {};
    for goal in goals:
        #print(goal)
        tracking[goal['name']] = []
        goal_history_rows = db.execute("SELECT week_starting, target, actual, goal_history.goal_id from goal_history INNER JOIN goals on goal_history.goal_id=goals.goal_id WHERE name=:name AND user_id=:user_id ORDER BY week_starting ASC", name=goal['name'], user_id=session['user_id'])
        #print(goal_history_rows)
        for row in goal_history_rows:
            achievement = 0
            if row['actual'] >= row['target']:
                achievement = 1
            else:
                achievement = 0
            print("actual: {} target: {} achievement {}".format(row['actual'], row['target'], achievement))


            db.execute("UPDATE goal_history SET achievement = :achievement WHERE goal_id=:goal_id AND user_id=:user_id AND week_starting=:week_starting", achievement=achievement, goal_id=row['goal_id'], user_id=session['user_id'], week_starting=row['week_starting'])
        #print(tracking)

    # calculate average target achievement rate for each goal
    for goal in goals:
        achievement_rate_by_goal[goal['name']] = db.execute("SELECT AVG(achievement) FROM goal_history WHERE user_id=:user_id AND goal_id=:goal_id", user_id=session['user_id'], goal_id=goal['goal_id'])[0]["AVG(achievement)"]
    print("achievement_rate_by_goal: {}".format(achievement_rate_by_goal))

    # calculate average % of targets achieved
    goal_rates = []
    for goal, value in achievement_rate_by_goal.items():
        goal_rates.append(value)
    print('goal_rates: {}'.format(goal_rates))
    overall_achievement = sum(goal_rates) / len(goal_rates)

    print(achievement_rate_by_goal)
    print(overall_achievement)

    # generate chart
    goal_names = list(achievement_rate_by_goal.keys());
    data = [go.Bar(
            x=goal_names,
            y=goal_rates
    )]

    layout = go.Layout(yaxis=dict(tickformat="%", range=[0, 1]))

    fig = go.Figure(data=data, layout=layout)

    graph_url = py.plot(fig, filename='tracking_chart', auto_open=False)
    print(graph_url)

    return render_template("track.html", goals=achievement_rate_by_goal, overall_achievement=overall_achievement, graph_url=graph_url)

@app.route("/user_goals")
@login_required
def user_goals():
    """ Look up user goals, to populate checkin form """

    # grab user_id from session to know which goals to fetch
    user_id = session["user_id"]

    # grab current week
    now = datetime.now()
    east_coast_now = now - timedelta(hours=4)
    current_week = east_coast_now - timedelta(days=(east_coast_now.weekday() + 1) % 7, hours=east_coast_now.hour, minutes=east_coast_now.minute, seconds=east_coast_now.second, microseconds=east_coast_now.microsecond)
    current_week = current_week.strftime('%Y-%m/%d 00:00:00')

    # grab goals from database that match category
    user_goals = db.execute("SELECT * FROM user_goals INNER JOIN goals ON user_goals.goal_id=goals.goal_id WHERE user_id = :user_id AND :current_week >= start_tracking", user_id=user_id, current_week=current_week)

    print(user_goals);
    return jsonify({ 'data': render_template("checkin.html", user_goals=user_goals) })

@app.route("/goal_history")
@login_required
def goal_history():
    """ given a goal by AJAX request on track.html, look up goal history, generate HTML table of goal history, and return HTML """

    user_id = session["user_id"]

    goal_name = request.args.get("goal_name")
    rows = db.execute("SELECT * FROM goals WHERE name=:name LIMIT 1", name=goal_name)
    goal_id = rows[0]['goal_id']

    # grab goal_history rows for user and goal
    goal_history_rows = db.execute("SELECT * FROM goal_history WHERE user_id=:user_id AND goal_id=:goal_id ORDER BY week_starting ASC", user_id=user_id, goal_id=goal_id)
    for row in goal_history_rows:
        row['achievement'] = "Yes" if row['achievement'] == 1.0 else "No"
        row['week_starting'] = datetime.strptime(row['week_starting'], '%Y-%m-%d 00:00:00').strftime('%m/%d/%Y')


    # calculate goal achievement rate
    goal_achievement_rate = db.execute("SELECT AVG(achievement) FROM goal_history WHERE user_id=:user_id AND goal_id=:goal_id", user_id=session['user_id'], goal_id=goal_id)[0]["AVG(achievement)"]

    return jsonify({ 'html': render_template("goal_history.html", goal_history_rows=goal_history_rows, goal_achievement_rate=goal_achievement_rate, goal_name=goal_name) })


@app.route("/set")
@login_required
def set():
    return render_template("set.html")

app.secret_key= "b'N\xd9e\xd7\x1c\xdf\x0eu\xaf\x84\xb3\x07\xf1\xf3`\xb3\xea\xf5\x063\xc1\xe2T\x15'"

