from flask import Flask, render_template, request, redirect
import csv

app = Flask(__name__)

# Öğrenci giriş kodları
def load_student_codes():
    with open('student_codes.csv', newline='') as f:
        return set(row[0] for row in csv.reader(f))

student_codes = load_student_codes()

# Cevap anahtarı (örnek)
ANSWER_KEY = {
    "turkce": list("ABCDEABCDEABCDEABCDE"),
    "matematik": list("ABCDEABCDEABCDEABCDE"),
    "fen": list("ABCDEABCDEABCDEABCDE"),
    "inkilap": list("ABCDEABCDE"),
    "din": list("ABCDEABCDE"),
    "ingilizce": list("ABCDEABCDE")
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form.get("code")
        if code not in student_codes:
            return render_template("index.html", error="Geçersiz öğrenci kodu!", show_form=False)

        answers = {
            "turkce": [request.form.get(f"turkce{i+1}", "").strip().upper() for i in range(20)],
            "matematik": [request.form.get(f"matematik{i+1}", "").strip().upper() for i in range(20)],
            "fen": [request.form.get(f"fen{i+1}", "").strip().upper() for i in range(20)],
            "inkilap": [request.form.get(f"inkilap{i+1}", "").strip().upper() for i in range(10)],
            "din": [request.form.get(f"din{i+1}", "").strip().upper() for i in range(10)],
            "ingilizce": [request.form.get(f"ingilizce{i+1}", "").strip().upper() for i in range(10)],
        }

        results = {}
        for ders, cevaplar in answers.items():
            dogru = sum(1 for i, cvp in enumerate(cevaplar) if cvp == ANSWER_KEY[ders][i])
            bos = sum(1 for c in cevaplar if c == "")
            yanlis = len(cevaplar) - dogru - bos
            results[ders] = {"dogru": dogru, "yanlis": yanlis, "bos": bos}

        return render_template("result.html", code=code, results=results)

    return render_template("index.html", show_form=True)

if __name__ == "__main__":
    app.run(debug=True)
