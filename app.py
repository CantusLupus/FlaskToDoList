from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from datetime import datetime

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

if __name__ == "__main__":
    app.run(debug=True)
