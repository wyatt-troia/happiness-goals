$( document ).ready(function() {

    // handler to slide up category cards on index.html when a button is clicked and generate goal selection screen based on AJAX response from /goals
    $( ".category_btn" ).click(function () {

        // clear buttons
        $( ".row" ).slideUp();

        // retrieve value of button clicked
        var category = $(this).attr( "value" );

        parameters = {
            category: category
        };

        content = ""

        $.getJSON("/goals", parameters, function(data, textStatus, jqXHR) {
            console.log(data);
            var card_array = [];
            var cards_per_row = 3;
            if (data.length === 0) {
                content += `<div class="row pb-4"> <div class="card-deck"><div class="card" style="width: 18rem;">

                      <div class="card-body d-flex flex-column">
                            <ul class="list-group list-group-flush mb-4">
                                <li class="list-group-item">
                                <h5 class="card-title">Custom Goal</h5>
                            </li>
                        <form action="/add_goal" method="post" class="mt-auto needs-validation" novalidate>
                            <div class="form-group pb-3">
                                <input class="form-control" type="text" name="name" placeholder="Title">
                                <input type="hidden" name="custom" value="true"">
                            </div>
                            <div class="form-group pb-3">

                                <select class="form-control freq_select form-control-md" name="frequency" id="frequency" data-width="50%" required>
                                  <option disabled value="" selected>Select weekly frequency</option>
                                  <option value=1>1 time a week</option>
                                  <option value=2>2 times a week</option>
                                  <option value=3>3 times a week</option>
                                  <option value=4>4 times a week</option>
                                  <option value=5>5 times a week</option>
                                  <option value=6>6 times a week</option>
                                  <option value=7>7 times a week</option>
                                </select>
                                <div class="invalid-feedback">
                                    Please select a target frequency.
                                </div>
                            </div>
                            <div class="form-group pb-3 mt-auto align-bottom">
                                    <input class="week-picker form-control" type="text" name="week_starting" placeholder="Select week to start tracking">
                            </div>
                            <div class="mb-2"><label><b>Week : </b></label> <span id="startDate"></span> - <span id="endDate"></span></div>
                            <button type="submit" class="btn btn-primary btn-block mt-auto">Set Goal</button>
                        </form>


                      </div>

                    </div><div class="card filler" style="width: 18rem;">
                          <div class="card-body d-flex flex-column">
                            <h5 class="card-title">FILLER</h5>
                            <p class="card-text">FILLER</p>
                            <a href="#" value="FILLER" class="btn btn-primary mt-auto">Set a Goal</a>
                          </div>
                        </div><div class="card filler" style="width: 18rem;">
                          <div class="card-body d-flex flex-column">
                            <h5 class="card-title">FILLER</h5>
                            <p class="card-text">FILLER</p>
                            <a href="#" value="FILLER" class="btn btn-primary mt-auto">Set a Goal</a>
                          </div>
                        </div>`
            } else {
                                // break up array of goals into subarrays of the length the rows of goal cards should be
                while (data.length) {
                    card_array.push(data.splice(0, cards_per_row));
                }
                console.log(card_array);

                // loop over each array of goals, building a row of cards for each
                for (let i = 0; i < card_array.length; i++) {
                    content += `<div class="row pb-4"> <div class="card-deck">`;
                    // loop over each goal, building a card for each
                    for (let j = 0; j < card_array[i].length; j++) {
                        content += `<div class="card" style="width: 18rem;">

                          <div class="card-body d-flex flex-column">
                            <ul class="list-group list-group-flush mb-4">
                            <li class="list-group-item">
                            <h5 class="card-title">${card_array[i][j].name}</h5>
                            <p class="card-text">${card_array[i][j].description}</p>
                            </li>
                            </ul>
                            <form action="/add_goal" method="post" class="mt-auto needs-validation" novalidate>
                                <div class="form-group pb-3">
                                    <input type="hidden" name="name" value="${card_array[i][j].name}">
                                    <input type="hidden" name="custom" value="false"">

                                    <select class="form-control freq_select form-control-md" name="frequency" id="frequency" data-width="50%" required>
                                      <option disabled value="" selected>Select weekly frequency</option>
                                      <option value=1>1 time a week</option>
                                      <option value=2>2 times a week</option>
                                      <option value=3>3 times a week</option>
                                      <option value=4>4 times a week</option>
                                      <option value=5>5 times a week</option>
                                      <option value=6>6 times a week</option>
                                      <option value=7>7 times a week</option>
                                    </select>
                                    <div class="invalid-feedback">
                                        Please select a target frequency.
                                    </div>
                                </div>
                                <div class="form-group pb-3 mt-auto align-bottom">
                                        <input class="week-picker form-control" type="text" name="week_starting" placeholder="Select week to start tracking">
                                </div>
                                <div class="mb-2"><label><b>Week : </b></label> <span id="startDate"></span> - <span id="endDate"></span></div>
                                <button type="submit" class="btn btn-primary btn-block mt-auto">Set Goal</button>
                            </form>


                          </div>

                        </div>`
                    }
                    if (card_array[i].length < 3) {
                        for (let k = 0; k < 3 - card_array[i].length; k++) {
                          content += `<div class="card filler" style="width: 18rem;">
                          <div class="card-body d-flex flex-column">
                            <h5 class="card-title">FILLER</h5>
                            <p class="card-text">FILLER</p>
                            <a href="#" value="FILLER" class="btn btn-primary mt-auto">Set a Goal</a>
                          </div>
                        </div>`
                        }
                    }
                    content += `</div> </div>`;


                }
            }


            //console.log(content);
            $( "#goal_cards").html(content);
            $( ".filler" ).css('visibility','hidden');

            // weekpicker for weekly checkin

            var startDate;
            var endDate;

            var selectCurrentWeek = function() {
                window.setTimeout(function () {
                    $('.week-picker').find('.ui-datepicker-current-day a').addClass('ui-state-active')
                }, 1);
            }

            $('.week-picker').datepicker( {
                showOtherMonths: true,
                selectOtherMonths: true,
                onSelect: function(dateText, inst) {
                    var date = $(this).datepicker('getDate');
                    startDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay());
                    endDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay() + 6);
                    var dateFormat = inst.settings.dateFormat || $.datepicker._defaults.dateFormat;
                    console.log(this);
                    $(this).closest( 'form' ).find('#startDate').text($.datepicker.formatDate( dateFormat, startDate, inst.settings ));
                    $(this).closest( 'form' ).find('#endDate').text($.datepicker.formatDate( dateFormat, endDate, inst.settings ));
                    //$('.week-picker').val(startDate);
                    selectCurrentWeek();
                },
                beforeShowDay: function(date) {
                    var cssClass = '';
                    if(date >= startDate && date <= endDate)
                        cssClass = 'ui-datepicker-current-day';
                    return [true, cssClass];
                },
                onChangeMonthYear: function(year, month, inst) {
                    selectCurrentWeek();
                }
            });

            $(document).on( 'mousemove','.week-picker .ui-datepicker-calendar tr',function() {$(this).find('td a').addClass('ui-state-hover'); });
            $(document).on('mouseleave','.week-picker .ui-datepicker-calendar tr',function() {$(this).find('td a').removeClass('ui-state-hover'); });

            $("form").submit( function(event) {
                $(this).closest('form').find('.week-picker').datepicker( "setDate", startDate );
                return;
            });

            // Fetch all the forms we want to apply custom Bootstrap validation styles to
            var forms = document.getElementsByClassName('needs-validation');
            // Loop over them and prevent submission
            var validation = Array.prototype.filter.call(forms, function(form) {
              form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                  event.preventDefault();
                  event.stopPropagation();
                }
                form.classList.add('was-validated');
              }, false);
            });
        });

    });

    var timesClicked = 0;

    $( "#checkin_btn" ).click(function() {

        timesClicked++;

        if (timesClicked > 1) {
            $('#checkin_form_div').toggle()
        }
        else {

            parameters = {};

            // get user's goals via AJAX request
            $.getJSON("/user_goals", parameters, function(data, textStatus, jqXHR) {

                console.log(data);

                $( "#checkin_form_div").html(data.data);

                var startDate;
                var endDate;

                var selectCurrentWeek = function() {
                    window.setTimeout(function () {
                        $('.week-picker').find('.ui-datepicker-current-day a').addClass('ui-state-active')
                    }, 1);
                }

                $('.week-picker').datepicker( {
                    showOtherMonths: true,
                    selectOtherMonths: true,
                    onSelect: function(dateText, inst) {
                        var date = $(this).datepicker('getDate');
                        startDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay());
                        endDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay() + 6);
                        var dateFormat = inst.settings.dateFormat || $.datepicker._defaults.dateFormat;
                        $('#startDate').text($.datepicker.formatDate( dateFormat, startDate, inst.settings ));
                        $('#endDate').text($.datepicker.formatDate( dateFormat, endDate, inst.settings ));
                        $('#startDate').css("font-weight", "Bold");
                        $('#endDate').css("font-weight", "Bold");
                        selectCurrentWeek();
                    },
                    beforeShowDay: function(date) {
                        var cssClass = '';
                        if(date >= startDate && date <= endDate)
                            cssClass = 'ui-datepicker-current-day';
                        return [true, cssClass];
                    },
                    onChangeMonthYear: function(year, month, inst) {
                        selectCurrentWeek();
                    }
                });

                $('.week-picker').datepicker( 'setDate', new Date());
                var date = $('.week-picker').datepicker('getDate');
                startDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay());
                endDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay() + 6);
                $('#startDate').text($.datepicker.formatDate( 'mm/dd/yy', startDate ));
                $('#endDate').text($.datepicker.formatDate( 'mm/dd/yy', endDate ));
                $('#startDate').css("font-weight", "Bold");
                $('#endDate').css("font-weight", "Bold");

                $(document).on( 'mousemove','.week-picker .ui-datepicker-calendar tr',function() {$(this).find('td a').addClass('ui-state-hover'); });
                $(document).on('mouseleave','.week-picker .ui-datepicker-calendar tr',function() {$(this).find('td a').removeClass('ui-state-hover'); });

                $("form").submit( function(event) {
                    $(this).closest('form').find('.week-picker').datepicker( "setDate", startDate );
                    return;
                });

                'use strict';

                // Fetch all the forms we want to apply custom Bootstrap validation styles to
                var forms = document.getElementsByClassName('needs-validation');
                // Loop over them and prevent submission
                var validation = Array.prototype.filter.call(forms, function(form) {
                  form.addEventListener('submit', function(event) {
                    if (form.checkValidity() === false) {
                      event.preventDefault();
                      event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                  }, false);
                });
            });
        }

    });

    $('#back_to_track_div').hide();

    // generate history for each goal via AJAX request

    $('.goal_history').click(function() {
        parameters = {
            goal_name: $(this).text()
        }
        $.getJSON("/goal_history", parameters, function(data, textStatus, jqXHR) {
            $( "#goal_history_div").html(data.html);
            $( "#goal_history_div").show();
            $( ".goal_history_hide").hide();

            // apply conditional formatting to "achieved" column
            $( "#goal_history_table td:nth-child(4)" ).each(function() {
                console.log($(this).html().trim());
                if ($(this).html().trim() === "Yes") {
                    $(this).css('backgroundColor','#77DD77');
                }
                else {
                    $(this).css('backgroundColor','#F7786B');
                }
            });

            // return to track home screen when back button is clicked
            $( "#back_to_track_btn").click(function() {
                $( "#goal_history_div").hide();
                $( ".goal_history_hide").show();
            });
        })
    });

});

