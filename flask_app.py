# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="jimmyjbling",
    password="cs348project",
    hostname="jimmyjbling.mysql.pythonanywhere-services.com",
    databasename="baseball",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299  # pythonanywhere times out at 300 sec, so close anything just before to aviod a crash
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # the internet tells me setting this to true mess shit up

db = SQLAlchemy(app)

@app.route('/edit/', methods=["GET", "POST"])
def edit_index():
    if request.method == "GET":
        return render_template("edit_page.html", comments=comments)

    if request.method == "POST":
        comments.append(request.form["contents"])
        return redirect(url_for('edit_index'))

@app.route('/', methods=["GET"])
def main_index():
    if request.method == "GET":
        return render_template("main_page.html", comments=comments)

    if request.method == "POST":
        comments.append(request.form["contents"])
        return redirect(url_for('main_index'))

