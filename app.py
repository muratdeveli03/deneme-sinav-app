from flask import Flask, render_template, request
app = Flask(__name__)

# Öğrenci girişine izin verilen kodlar
gecerli_kodlar = ["1234", "5678", "9012"]

# Her dersin soru sayısı
soru_sayilari = {
    "turkce": 20,
    "matematik": 20,
    "fen": 20,
    "inkilap": 10,
    "din": 10,
    "ingilizce": 10
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if code not in gecerli_kodlar:
            return "Geçersiz öğrenci kodu!"

        results = {}
        for ders, adet in soru_sayilari.items():
            cevaplar = []
            for i in range(1, adet + 1):
                cevap = request.form.get(f"{ders}{i}", "").strip().upper()
                cevaplar.append(cevap if cevap else "-")
            results[ders] = cevaplar

        return render_template("result.html", code=code, results=results)

    return render_template("index.html", dersler=soru_sayilari.keys(), soru_sayilari=soru_sayilari)

if __name__ == "__main__":
    app.run(debug=True)
