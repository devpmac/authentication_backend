import os
from flask import Flask, render_template

Articles = [
    {
        "id": 1,
        "title": "Article one",
        "body": "A lot of stuff going here",
        "author": "Miguel Condesso",
        "date": "26-06-2020",
    },
    {
        "id": 2,
        "title": "Article two",
        "body": "A lot of stuff going here",
        "author": "Miguel Condesso",
        "date": "26-06-2020",
    },
    {
        "id": 3,
        "title": "Article three",
        "body": "A lot of stuff going here",
        "author": "Miguel Condesso",
        "date": "26-06-2020",
    },
]

template_dir = os.path.abspath("src/templates")
static_dir = os.path.abspath("src/static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/articles/")
def articles():
    return render_template("articles.html", articles=Articles)


@app.route("/articles/<string:id>/")
def article(id):
    return render_template("article.html", id=id)


if __name__ == "__main__":
    app.run(debug=True)
