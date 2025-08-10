from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

# Cevap anahtarları JSON dosyası
ANSWER_KEY_FILE = "answer_keys.json"
# Öğrenci cevaplarını saklamak için JSON dosyası
STUDENT_ANSWERS_FILE = "student_answers.json"

# Cevap anahtarlarını yükle
def load_answer_keys():
    if os.path.exists(ANSWER_KEY_FILE):
        with open(ANSWER_KEY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Öğrenci cevaplarını yükle
def load_student_answers():
    if os.path.exists(STUDENT_ANSWERS_FILE):
        with open(STUDENT_ANSWERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Öğrenci cevaplarını kaydet
def save_student_answers(data):
    with open(STUDENT_ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Puan hesaplama (doğru = 4, yanlış = -1, boş = 0)
def calculate_score(student_answers, answer_key):
    score = 0
    for ders, cevaplar in student_answers.items():
        if ders in answer_key:
            for ogr_cevap, dogru_cevap in zip(cevaplar, answer_key[ders]):
                if ogr_cevap == dogru_cevap:
                    score += 4
                elif ogr_cevap.strip() != "":
                    score -= 1
    return score

@app.route("/", methods=["GET", "POST"])
def index():
    cevap_anahtarlari = load_answer_keys()
    deneme_listesi = list(cevap_anahtarlari.keys())

    if request.method == "POST":
        ogrenci_kodu = request.form.get("ogrenci_kodu", "").strip()
        deneme_kodu = request.form.get("deneme_kodu", "").strip()

        if not ogrenci_kodu or not deneme_kodu:
            return render_template(
                "index.html",
                hata="Lütfen tüm alanları doldurun.",
                deneme_listesi=deneme_listesi,
                cevap_anahtarlari=cevap_anahtarlari
            )

        # Formdan cevapları oku
        dersler = cevap_anahtarlari[deneme_kodu]
        ogrenci_cevaplari = {}
        for ders, dogru_cevaplar in dersler.items():
            cevaplar = []
            for i in range(len(dogru_cevaplar)):
                cevaplar.append(request.form.get(f"{ders}_{i+1}", "").strip().upper())
            ogrenci_cevaplari[ders] = cevaplar

        # Öğrenci cevaplarını dosyaya kaydet
        tum_cevaplar = load_student_answers()
        if deneme_kodu not in tum_cevaplar:
            tum_cevaplar[deneme_kodu] = {}
        tum_cevaplar[deneme_kodu][ogrenci_kodu] = ogrenci_cevaplari
        save_student_answers(tum_cevaplar)

        # Puan hesapla
        ogrenci_puan = calculate_score(ogrenci_cevaplari, dersler)

        # Tüm öğrenciler için puan sıralaması
        siralama_listesi = []
        for ogr_kod, cevaplar in tum_cevaplar[deneme_kodu].items():
            puan = calculate_score(cevaplar, dersler)
            siralama_listesi.append({"ogrenci_kodu": ogr_kod, "puan": puan})
        siralama_listesi.sort(key=lambda x: x["puan"], reverse=True)

        return render_template(
            "result.html",
            ogrenci_kodu=ogrenci_kodu,
            deneme_kodu=deneme_kodu,
            cevaplar=ogrenci_cevaplari,
            cevap_anahtarlari=dersler,
            siralama=siralama_listesi
        )

    return render_template(
        "index.html",
        deneme_listesi=deneme_listesi,
        cevap_anahtarlari=cevap_anahtarlari
    )

if __name__ == "__main__":
    app.run(debug=True)
