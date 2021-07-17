from flask import Flask, render_template, url_for, request, redirect, session, logging, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, SelectField, TextAreaField, PasswordField, validators
# from passlib.hash import sha256_crypt
from datetime import datetime

from wtforms.fields.core import StringField

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://Cantus:2345@localhost/ToDo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class ToDo(db.Model):
  __tablename__ = "ToDoTable"
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(200), nullable = False)
  date_created = db.Column(db.DateTime, default=datetime.now)

  def __repr__(self):
      return "<Task %r>" % self.id

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
      task_content = request.form["content"]
      new_task = ToDo(content = task_content)

      try:
        db.session.add(new_task)
        db.session.commit()
        return redirect("/")
      except:
        return "The task has not been added"

    else:
      tasks = ToDo.query.order_by(ToDo.date_created).all()
      return render_template("index.html", tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = ToDo.query.get_or_404(id)

    try:
      db.session.delete(task_to_delete)
      db.session.commit()
      return redirect("/")
    except:
      return "There was a problem deleting that task"

@app.route("/update/<int:id>", methods=["GET", "POST"])
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

class RegisterForm(Form):
  username = StringField("Name", [validators.length(min=1, max=30)])
  email = StringField("Email", [validators.length(min=6, max=50)])
  password = PasswordField("Password", [
    validators.DataRequired(),
    validators.EqualTo("confirm", message="Password is incorrect")
  ])
  confirm = PasswordField("Confirm Password")

@app.route("/register", methods=["GET","POST"])
def register():
  form = RegisterForm(request.form)
  if request.method == "POST" and form.validate():
    user = User(form.username.data, form.email.data,
                    form.password.data)
    db_session.add(user)
    flash('Thanks for registering')
    return redirect(url_for('login'))
  return render_template("register.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
