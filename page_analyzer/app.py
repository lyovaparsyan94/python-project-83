import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer import checker, database, validator
from page_analyzer.checker import CheckerError

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls", methods=["GET", "POST"])
def urls():
    if request.method == "POST":
        url_input = request.form.get("url")

        if not validator.is_valid_url(url_input):
            msg = "Заполните это поле" if not url_input else "Некорректный URL"
            flash(msg, "danger")
            return render_template("index.html"), 422

        parsed_url = validator.normalize_url(url_input)
        url_id, error = database.add_url(parsed_url)

        if error:
            flash(error, "warning")
            return redirect(url_for("url_detail", id=url_id))

        flash("Страница успешно добавлена", "success")
        return redirect(url_for("url_detail", id=url_id))

    urls_list = database.get_all_urls()
    return render_template("urls.html", urls=urls_list)


@app.route("/urls/<int:id>", methods=["GET", "POST"])
def url_detail(id):
    url = database.get_url_by_id(id)
    if not url:
        flash("URL не найден", "danger")
        return redirect(url_for("urls"))

    if request.method == "POST":
        try:
            target = url["name"]
            status_code, h1, title, description = checker.check_url(target)
        except CheckerError:
            flash("Произошла ошибка при проверке", "danger")
        else:
            database.add_check(id, status_code, h1, title, description)
            flash("Страница успешно проверена", "success")
        return redirect(url_for("url_detail", id=id))

    return render_template("url_detail.html", url=url)
