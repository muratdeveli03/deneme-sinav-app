from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Cevap anahtarlarını JSON dosyasından yükle
with open("answer_keys.json", "r") as f:
    ANSWER_KEYS = json.load(f)

DERSLER = {
    "Turkce": 20,
    "Matematik": 20,
    "Fen": 20,
    "Inkilap": 10,
    "Din": 10,
    "Ingilizce": 10
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        deneme_kodu = request.form.get("deneme_kodu")
        ogrenci_kodu = request.form.get("ogrenci_kodu")

        # Deneme kodu geçerli mi kontrol et
        if deneme_kodu not in ANSWER_KEYS:
            return "Geçersiz deneme kodu!", 400

        # Doğru cevap anahtarını al
        answer_key = ANSWER_KEYS[deneme_kodu]

        student_answers = {}
        results = {}

        for ders, soru_sayisi in DERSLER.items():
            cevaplar = []
            for i in range(soru_sayisi):
                key = f"{ders}_{i+1}"
                cevap = request.form.get(key, "").strip().upper()
                cevaplar.append(cevap)

            student_answers[ders] = cevaplar

            # Doğru cevapla karşılaştır
            dogru = 0
            yanlis = 0
            bos = 0
            for i, ogr_cevap in enumerate(cevaplar):
                if ogr_cevap == "":
                    bos += 1
                elif ogr_cevap == answer_key[ders][i]:
                    dogru += 1
                else:
                    yanlis += 1

            results[ders] = {
                "dogru": dogru,
                "yanlis": yanlis,
                "bos": bos
            }

        return render_template("result.html", ogrenci_kodu=ogrenci_kodu, deneme_kodu=deneme_kodu, results=results, answers=student_answers)

    return render_template("index.html", dersler=DERSLER)

if __name__ == "__main__":
    app.run(debug=True)
