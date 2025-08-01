from flask import Flask, render_template, request

app = Flask(__name__)

DOGRU_CEVAPLAR = {
    "turkce": list("ABCDABCDABCDABCDABCD"),
    "matematik": list("ABCDABCDABCDABCDABCD"),
    "fen": list("ABCDABCDABCDABCDABCD"),
    "ingilizce": list("ABCDABCDABCDABCDABCD"),
    "sosyal": list("ABCDABCDABCDABCDABCD"),
    "din": list("ABCDABCDABCDABCDABCD"),
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ad = request.form["ad"]
        sinif = request.form["sinif"]
        okul = request.form["okul"]

        sonuc = {}
        for ders, dogru_cevaplar in DOGRU_CEVAPLAR.items():
            cevap = request.form.get(ders, "").upper().strip()
            cevaplar = list(cevap)
            dogru = sum(1 for i, c in enumerate(cevaplar) if i < len(dogru_cevaplar) and c == dogru_cevaplar[i])
            sonuc[ders] = {"dogru": dogru, "yanlis": len(dogru_cevaplar) - dogru}

        return render_template("result.html", ad=ad, sinif=sinif, okul=okul, sonuc=sonuc)

    return render_template("index.html")
