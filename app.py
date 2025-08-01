from flask import Flask, render_template, request

app = Flask(__name__)

# Her dersin soru sayısı
DERSLER = {
    "turkce": 20,
    "matematik": 20,
    "fen": 20,
    "sosyal": 10,
    "din": 10,
    "ingilizce": 10
}

# Örnek doğru cevaplar
DOGRU_CEVAPLAR = {
    "turkce": list("ABCDABCDABCDABCDABCD"),
    "matematik": list("DCBADCBDACBDACBDACBD"),
    "fen": list("ABBACDDCABABCDCABBDC"),
    "sosyal": list("ABCDABCDAB"),
    "din": list("DCDABADBDC"),
    "ingilizce": list("CCABBDDCBA")
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ad = request.form["ad"]
        sinif = request.form["sinif"]
        okul = request.form["okul"]

        sonuc = {}

        for ders, adet in DERSLER.items():
            cevaplar = []
            for i in range(1, adet+1):
                key = f"{ders}_{i}"
                girilen = request.form.get(key, "").upper()
                cevaplar.append(girilen)

            dogru_sayisi = sum(1 for i in range(adet) if i < len(DOGRU_CEVAPLAR[ders]) and cevaplar[i] == DOGRU_CEVAPLAR[ders][i])
            sonuc[ders] = {"dogru": dogru_sayisi, "yanlis": adet - dogru_sayisi}

        return render_template("result.html", ad=ad, sinif=sinif, okul=okul, sonuc=sonuc)

    return render_template("index.html", dersler=DERSLER)
