from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = "gizli_kelime"

with open("students.json") as f:
    STUDENT_CODES = json.load(f)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("code")
        if code in STUDENT_CODES:
            session["student_code"] = code
            return redirect(url_for("form"))
        else:
            return render_template("login.html", error="Geçersiz giriş kodu!")
    return render_template("login.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    if "student_code" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        answers = request.form.to_dict()
        return render_template("result.html", answers=answers)

    return render_template("form.html", student_name=STUDENT_CODES[session["student_code"]])

if __name__ == "__main__":
    app.run(debug=True)
