# PropelPrompt

1. Overview
1. Setup
1. User Guide
1. Technical Implementation
1. Challenges and Solutions 

## Overview

PropelPrompt is a web application that allows users to set goals, plan tasks, and better manage their time through analytics, so that they develop productive working habits and stay motivated. PropelPrompt is designed to function as a companion app while a user focuses on their work. The app helps the user track how much time they spend on various tasks and prompts the user to reflect on their work sessions. The aim is that users are more cognisant of their time management skills, and deliberate about how they plan and achieve their goals.

The index, register and login page feature open source illustrations from <a href=“unDraw.co”>unDraw</a>.

## Setup

To run the app locally, download all the files above. Make sure that the file structure is preserved.

(1) Navigate to the application through your terminal.

(2) Run ```console pip3 install -r requirements.txt``` to install all necessary python requirements.

(3) Open and run setup_sql.py to create the sql database. This should create a new file called site.db.

(4) Launch the Flask application from your terminal by running ```console python3 app.py```.

(5) If any packages are still missing at this point, run ```console pip3 install <package_name>``` and repeat (4) until the app launches.

(6) Launch your browser (chrome recommended) and type 0.0.0.0. You can now register a new account and get started.

## User Guide

From the landing page, you can navigate to register a new account or log in. Once you have logged in, you are redirected to your workspace. From your workspace, you can start a new session, schedule reminders, and navigate to your goals or profile. To get started as a new user, navigate to your goals and set a new goal by specifying the goal and adding a short description. Each goal links to a separate page where you can set tasks. Set a new task and navigate back to your workspace. You can schedule reminders to work on certain goals on right hand side of the screen, or start a session. A session helps you track how much time you spend working on your tasks. After starting a session, select a goal and a task. When you are done working, end your session. After you end a session, specify whether you have completed your task, and, if you wish, attach a note for yourself. Completing a task will delete it from your task tab. Your profile tab displays a summary of your working habits and logs all your sessions by day.

## Technical Implementation

The application uses the Flask web framework, the Jinja template engine to pass variables from python to HTML, the flask_sqlalchemy package to setup a database, and Bootstrap to create a responsive web interface. Bcrypt is used to encrypt user passwords.

First, required packages are imported, then Flask form classes and login/registration functions are defined before the app is instantiated. Afterwards, several classes are defined for each database table. Finally, each web route is defined. Most routes include a flask form which allows users to post information, which is then displayed and stored for later use. Each return statement either renders an HTML page, located in the templates folder, or redirects the user to an HTML page. Each route that the user is required to be logged in for, includes an @login_required statement. This is important because data is often queried by the current user id (e.g, ``` Goal.query.filter_by(user_id = current_user.user_id)```), which requires a user to be logged in.

## Challenges and Solutions

To preserve a consistent design across the index, register and login page, I wanted to implement custom svg buttons. However, I needed these buttons to trigger the validate_on_submit functions to submit the flask forms that I had setup. The workaround that I found to disguise the bare ``` {{  form.submit() }} ``` as an svg image, was to wrap both the svg image and the submit button in html button tags, and hide the {{  form.submit() }} field by writing a CSS class that hid the button, and giving it zero width.

Example:
``` <button type="submit" class="bt-hidden" style="padding: 0px; height: 50px; width: 205px">
<img src="/static/login_bt.svg" style="width: 100%">
{{ form.submit(class="bt-hidden", style="width: 0px") }}
</button>
```

For the main application, I decided to only apply a simple CSS styling, since I considered it important that the design was simple and unobtrusive to promote focus and productivity.

I wanted to display a timer during sessions, so that users would be informed in real time about how much time they have spent working. An easy solutions that I found, was to modify a countdown timer from <a href=“https://www.w3schools.com/howto/howto_js_countdown.asp”>w3schools</a>, so that it counted up from the current time, instead of counting down to a later date.

```
<script>
var countFromDate = new Date().getTime();

var x = setInterval(function() {

  var now = new Date().getTime();

  var distance = now - countFromDate;

  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  document.getElementById("timer").innerHTML = hours + "h "
  + minutes + "m " + seconds + "s ";

  if (distance < 0) {
    clearInterval(x);
  }
});
</script>
```

On the workspace page, I wanted users to be able to schedule reminders, so that they knew where to focus their attention. Therefore, I needed to implement a dynamic form field from which the user could select all the goals they had set. To do so, the relevant Flask form is defined inside the route, so that it is updated every time the user makes any changes. All the choices are directly queried from the database. Additionally, the choices are restricted by the goals that have not been scheduled yet. This is compactly done using list comprehension and adding an if statement that checks whether the goal has already been scheduled.

First, the current date is defined using the datetime package. Next, using list comprehension, a list of scheduled items is generated by querying the Schedule table for schedules made by the current user that are scheduled for today or a later date. If items have not been scheduled yet, they are then included as choices in the Flask form.

```
date = datetime.date.today()
schedule_items = [item.item for item in Schedule.query.filter_by(user_id = current_user.user_id) if item.to_date.date() >= date]
class ScheduleForm(FlaskForm):
	item = SelectField("Goal", choices = sorted([x.header for x in Goal.query.filter_by(user_id = current_user.user_id) if x.header not in schedule_items]),
	                   validators = [DataRequired()])
        deadline = DateField("Deadline", format = "%Y-%m-%d", render_kw={"placeholder": "YYYY-MM-DD"})
        submit = SubmitField("Set Reminder")
```

A similar problem with a different solution arose when programming the session feature. Users would have to be able to select from their set goals and tasks to start a session. However, rather than using a dynamic form, a better solution was to program several routes that the user went through, during which the user chose a goal, a task, and finally started the session. Each route temporarily stores information, such as the goal name and task, before this information is submitted when the user starts the timer. The added benefit over using a dynamic form is that users have a better overview of their goals and tasks when selecting them, and can navigate in and out of goals before committing to a task that they want to focus on.

As described above, the goal name and task name are temporarily stored in the route and then finally inserted into the sessions table when a session is started.

``` 
@app.route("/session/<goal_name>/<task_name>/start", methods = ["GET", "POST"])
@login_required
def session_start(goal_name, task_name):
    form = SessionForm()
    if form.validate_on_submit():
        current_user_goals = Goal.query.filter_by(user_id = current_user.user_id)
        current_goal_id = current_user_goals.filter_by(header = goal_name).first().goal_id
        current_user_tasks = Task.query.filter_by(goal_id = current_goal_id)
        new_session = Session(start = datetime.datetime.now(),
                                               task = task_name,
                                               user_id = current_user.user_id,
                                               goal_id = current_goal_id,
                                               task_id = current_user_tasks.filter_by(task = task_name).first().task_id)
        db.session.add(new_session)
        db.session.commit()
        current_session_id = new_session.session_id
        return redirect(url_for("session", goal_name = goal_name, task_name = task_name, 
                                 current_session_id = current_session_id))
    return render_template("11_session_start.html", form = form)
``` 
