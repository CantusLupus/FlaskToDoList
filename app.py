from enum import unique
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Cantus:2345@localhost/ToDo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ToDo(db.Model):
  # __tablename__ = "ToDo"
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True)
  email = db.Column(db.String(50), unique=True)

  def __init__(self, username, email):
      self.username = username
      self.email = email


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
