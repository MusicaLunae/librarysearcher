import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, )

@app.route("/")
def index():
    return render_template("index.html")




@app.route("/results", methods =["GET", "POST"])
def form_retriever():
    finalQuery = ""
    # grabbing the variables from the form
    category_list = request.form.get("category-list")
    ultraHD = request.form.get("uhdToggle")
    threeD = request.form.get("3dToggle")
    searchTerm = request.form.get("searchTerm")

    # Build the query
    searchTermQuery = searchTermParser(searchTerm)
    catQuery = categorySelector(category_list, ultraHD, threeD)
    finalQuery = queryBuilder(searchTermQuery, catQuery)

    # Query the database and write out to results
    query_db(finalQuery)



# Functions for determining how to build the query
def categorySelector(__cat__, __uhdStat__, __threeDstat__):
    __catQueryString__ = categoryParser(__cat__) + uh3dParser(__cat__, __uhdStat__, __threeDstat__)


def categoryParser(__cat__):
    match __cat__:
        case "all":
            return "group <> ''"
        case "moviesAll":
            return "group like movies%"
        case "moviesBR":
            return "group like movies_bd%"
        case "moviesX264":
            return "group like movies_x2%"
        case "moviesXVID":
            return "group like movies_xvid%"
        case "showsAll":
            return "group like tv%"
        case "showsHD":
            return "group like tv% and group != tv_sd"


def uh3dParser(__cat__, __uhdStat__, __threeDstat__):
    if __cat__ != "moviesX264" | (__uhdStat__ == True & __threeDstat__ == True):
        return ""
    
    if __uhdStat__ == False & __threeDstat__ == False:
        return " and group not like ('movies_x264_3d' and 'movies_x264_4k' and 'movies_x265_4k' and 'movies_x265_4k_hdr')"
    elif __uhdStat__ == True & __threeDstat__ == False:
        return " and group not like 'movies_x264_3d'"
    elif __uhdStat__ == False & __threeDstat__ == True:
        return " and group not like ('movies_x264_4k' and 'movies_x265_4k' and 'movies_x265_4k_hdr')"


def searchTermParser(__term__):
    __new_term__ = "%" + __term__.replace(" ", "%") + "%"

def queryBuilder(__searchTerm__, __cat__):
    __query__ = "select title, cat, size, magnetLink from magnet_links where title like " + __searchTerm__ + " and " + __cat__ + ";"


def query_db(__query__):
    connect = sqlite3.connect("assets/rarbg_db.sqlite")
    cursor = connect.cursor()
    cursor.execute(__query__)

    data = cursor.fetchall()
    return render_template("results.html", data=data)

if __name__ == "__main__":
    app.run(debug=False)