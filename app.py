from enum import unique
from flask import Flask, render_template, url_for, request, redirect, session, logging, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_manager, login_user, login_required, logout_user, current_user
from wtforms import Form, SelectField, TextAreaField, PasswordField, form, validators, BooleanField, StringField
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://Cantus:2345@localhost/ToDo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

class ToDo(db.Model):
  __tablename__ = "ToDoTable"
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(200), nullable = False)
  date_created = db.Column(db.DateTime, default=datetime.now)
  user_id = db.Column(db.String(30))

class User(UserMixin, db.Model):
  __tablename__ = "Users"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user = db.Column(db.String(30), unique=True)
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(50))
  date_created = db.Column(db.DateTime, default=datetime.now)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class RegisterForm(Form):
  username = StringField("Username", [validators.length(min=1, max=30)])
  email = StringField("Email", [validators.length(min=6, max=50)])
  password = PasswordField("Password", [validators.DataRequired()])
  confirm = PasswordField("Confirm Password", [validators.EqualTo("password", message="Passwords don't match")])

class LoginForm(Form):
  username = StringField("Username", [validators.length(min=1, max=30)])
  password = PasswordField("Password", [validators.DataRequired()])

@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method == "POST":
      task_content = request.form["content"]
      new_task = ToDo(content = task_content, user_id = current_user.user)

      try:
        db.session.add(new_task)
        db.session.commit()
        return redirect("/")
      except:
        return "The task has not been added"

    tasks = ToDo.query.filter(ToDo.user_id.like(current_user.user)).all()
    return render_template("index.html", tasks=tasks, name = current_user.user )

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    task_to_delete = ToDo.query.get_or_404(id)

    try:
      db.session.delete(task_to_delete)
      db.session.commit()
      return redirect("/")
    except:
      return "There was a problem deleting that task"

@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
  task = ToDo.query.get_or_404(id)

  if request.method == "POST":
    task.content = request.form["content"]

    try:
      db.session.commit()
      return redirect("/")
    except:
      return "Cannot update this task"

  else:
    return render_template("update.html", task=task)

@app.route("/register", methods=["GET","POST"])
def register():
  form = RegisterForm(request.form)

  if request.method == 'POST' and form.validate():
    new_user = User(user = form.username.data, email = form.email.data, password = form.password.data)
    db.session.add(new_user)
    try:
      db.session.commit()
      login_user(new_user)
      return redirect(url_for("index"))
    except:
      return "username or email is already in use"
  return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
  form = LoginForm(request.form)

  if request.method == 'POST':
    user = User.query.filter_by(user = form.username.data).first()
    if user:
      if user.password == form.password.data:
        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html", form=form, invalid = "Invalid password or username")
  return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
