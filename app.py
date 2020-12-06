from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import datetime

class RegForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Submit")

class LogForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Submit")

class GoalForm(FlaskForm):
    header = StringField("Goal", validators = [DataRequired()], render_kw={"placeholder": "Goal"})
    summary = StringField("Summary", validators = [DataRequired()], render_kw={"placeholder": "Summary"})
    submit = SubmitField('Set Goal')

class TaskForm(FlaskForm):
    task = StringField("Task", validators = [DataRequired()], render_kw={"placeholder": "Task"})
    submit = SubmitField('Set Task')

class SessionForm(FlaskForm):
    submit = SubmitField("Start Session")

class EndSessionForm(FlaskForm):
    submit = SubmitField("End Session")

class ReflectSessionForm(FlaskForm):
    completion = SelectField("Completion", choices = ["yes", "no"],validators = [DataRequired()])
    reflection = TextAreaField("Reflection")
    submit = SubmitField("Submit")

def register_user(form_data):
    def email_taken(email):
        if User.query.filter_by(email = email).count() > 0:
            return True
        else:
            return False
    if email_taken(form_data.email.data):
        return False
    hash_password = bcrypt.generate_password_hash(form_data.data["password"])
    new_user = User(username = form_data.data["username"],
                    email = form_data.data["email"],
                    password = hash_password,
                    date_registered = datetime.date.today())
    db.session.add(new_user)
    db.session.commit()
    return True

def validate_login(form_data):
    email = form_data.email.data
    password = form_data.password.data
    user = User.query.filter_by(email = email).first()
    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return True
    return False

app = Flask(__name__)
app.config["SECRET_KEY"] = ". . ."
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)
    def get_id(self):
        return (self.user_id)

class Goal(db.Model, UserMixin):
    goal_id = db.Column(db.Integer, primary_key = True)
    header = db.Column(db.String, nullable = False)
    summary = db.Column(db.String, nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)

class Task(db.Model, UserMixin):
    task_id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable = False)

class Session(db.Model, UserMixin):
    session_id = db.Column(db.Integer, primary_key = True)
    start = db.Column(db.DateTime, nullable = False)
    end = db.Column(db.DateTime, nullable = True)
    completion = db.Column(db.String, nullable = True)
    reflection = db.Column(db.String, nullable = True)
    task = db.Column(db.String, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable = False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.task_id"), nullable = False)

class Schedule(db.Model, UserMixin):
    schedule_id = db.Column(db.Integer, primary_key = True)
    from_date = db.Column(db.DateTime, nullable = False)
    to_date = db.Column(db.DateTime, nullable = False)
    item = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("workspace"))
    return render_template("1_index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("workspace"))
    form = RegForm()
    if form.validate_on_submit():
        valid_reg = register_user(form)
        if valid_reg:
            return redirect(url_for("login"))
    return render_template("2_register.html", form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("workspace"))
    form = LogForm()
    if form.validate_on_submit():
        email = form.email.data
        if User.query.filter_by(email = email).count():
            if validate_login(form):
                return redirect(url_for("workspace"))
        else:
            return redirect(url_for("register"))
    return render_template("3_login.html", form = form)

@app.route("/workspace", methods = ["GET", "POST"])
@login_required
def workspace():
    date = datetime.date.today()
    schedule = [item for item in Schedule.query.filter_by(user_id = current_user.user_id)]
    schedule_items = [item.item for item in Schedule.query.filter_by(user_id = current_user.user_id) if item.to_date.date() >= date]
    class ScheduleForm(FlaskForm):
        item = SelectField("Goal", 
                           choices = sorted([x.header for x in Goal.query.filter_by(user_id = current_user.user_id) 
                                             if x.header not in schedule_items]),
                           validators = [DataRequired()])
        deadline = DateField("Deadline", format = "%Y-%m-%d", render_kw={"placeholder": "YYYY-MM-DD"})
        submit = SubmitField("Set Reminder")
    form = ScheduleForm()
    if form.validate_on_submit():
        new_item = Schedule(item = form.data["item"],
                            from_date = date,
                            to_date = form.data["deadline"],
                            user_id = current_user.user_id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("workspace"))
    schedule = [item for item in Schedule.query.filter_by(user_id = current_user.user_id)]
    return render_template("4_workspace.html", date = date, form = form, schedule = schedule)

@app.route("/goals", methods = ["GET", "POST"])
@login_required
def goals():
    goals = Goal.query.filter_by(user_id = current_user.user_id)
    form = GoalForm()
    if form.validate_on_submit():
        new_goal = Goal(header = form.data["header"],
                        summary = form.data["summary"],
                        user_id = current_user.user_id)
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for("goals"))
    return render_template("5_goals.html", form = form, goals = goals)

@app.route("/<goal_name>/tasks", methods = ["GET", "POST"])
@login_required
def tasks(goal_name):
    form = TaskForm()
    current_user_goals = Goal.query.filter_by(user_id = current_user.user_id)
    current_goal_id = current_user_goals.filter_by(header = goal_name).first().goal_id
    tasks = Task.query.filter_by(goal_id=current_goal_id)
    if form.validate_on_submit():
        new_task = Task(task = form.data["task"],
                        user_id = current_user.user_id,
                        goal_id = current_goal_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("tasks", goal_name = goal_name))
    return render_template("6_tasks.html", form = form, tasks = tasks, goal_name = goal_name)

@app.route("/profile", methods = ["GET", "POST"])
@login_required
def profile():
    username = User.query.filter_by(user_id = current_user.user_id).first().username
    current_user_sessions = Session.query.filter_by(user_id = current_user.user_id)
    dates = sorted(set([session.start.date() for session in current_user_sessions]))
    sessions_by_date = []
    day_list = []
    time_by_date = []
    day_time = datetime.timedelta(0)
    total_time = datetime.timedelta(0)
    i = 0
    for session in [x for x in current_user_sessions]:
        if session.start.date() == dates[i]:
            day_list.append(session)
            day_time += session.end - session.start
            total_time += session.end - session.start
        else:
            i += 1
            sessions_by_date.append(day_list)
            day_list = [session]
            time_by_date.append(day_time)
            day_time = session.end - session.start
            total_time += session.end - session.start
    sessions_by_date.append(day_list)
    time_by_date.append(day_time)
    return render_template("7_profile.html", username = username,
                           dates = dates, sessions_by_date = sessions_by_date,
                           range = range, len = len,
                           time_by_date = time_by_date,
                           total_time = total_time)

@app.route("/day_<day>/sessions", methods = ["GET", "POST"])
@login_required
def sessions_by_date(day):
    current_user_sessions = Session.query.filter_by(user_id = current_user.user_id)
    dates = sorted(set([session.start.date() for session in current_user_sessions]))
    sessions_by_date = []
    day_list = []
    time_by_date = []
    day_time = datetime.timedelta(0)
    i = 0
    for session in [x for x in current_user_sessions]:
        if session.start.date() == dates[i]:
            day_list.append(session)
            day_time += session.end - session.start
        else:
            i += 1
            sessions_by_date.append(day_list)
            day_list = [session]
            time_by_date.append(day_time)
            day_time = session.end - session.start
    sessions_by_date.append(day_list)
    time_by_date.append(day_time)
    return render_template("8_sessions_by_date.html", dates = dates, 
                           sessions_by_date = sessions_by_date,
                           range = range, len = len, day = int(day),
                           time_by_date = time_by_date)

@app.route("/session/select_goal", methods = ["GET", "POST"])
@login_required
def select_goal():
    goals = Goal.query.filter_by(user_id = current_user.user_id)
    return render_template("9_session_goal.html", goals = goals)

@app.route("/session/<goal_name>/select_task", methods = ["GET", "POST"])
@login_required
def select_task(goal_name):
    current_user_goals = Goal.query.filter_by(user_id = current_user.user_id)
    current_goal_id = current_user_goals.filter_by(header = goal_name).first().goal_id
    tasks = Task.query.filter_by(goal_id=current_goal_id)
    return render_template("10_session_task.html", tasks = tasks, goal_name = goal_name)

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

@app.route("/session/<goal_name>/<task_name>/<current_session_id>/focus", methods = ["GET", "POST"])
@login_required
def session(goal_name, task_name, current_session_id):
    form = EndSessionForm()
    current_session = Session.query.filter_by(session_id = current_session_id).first()
    if form.validate_on_submit():
        current_session.end = datetime.datetime.now()
        db.session.commit()
        return redirect(url_for("session_reflect", goal_name = goal_name, task_name = task_name, 
                                current_session_id = current_session_id))
    return render_template("12_session.html", form = form)

@app.route("/session/<goal_name>/<task_name>/<current_session_id>/reflect", methods = ["GET", "POST"])
@login_required
def session_reflect(goal_name, task_name, current_session_id):
    form = ReflectSessionForm()
    if form.validate_on_submit():
        current_session = Session.query.filter_by(session_id = current_session_id).first()
        current_session.completion = form.data["completion"]
        if form.data["completion"] == "yes":
            current_user_goals = Goal.query.filter_by(user_id = current_user.user_id)
            current_goal_id = current_user_goals.filter_by(header = goal_name).first().goal_id
            current_user_tasks = Task.query.filter_by(goal_id = current_goal_id)
            current_user_tasks.filter_by(task = task_name).delete()
        current_session.reflection = form.data["reflection"]
        db.session.commit()
        return redirect(url_for("workspace"))
    return render_template("13_session_reflect.html", form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug = False, host = "0.0.0.0", port = 80)
