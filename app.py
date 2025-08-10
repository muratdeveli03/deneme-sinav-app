from flask import Flask, render_template, request
import json
import os
import csv

app = Flask(__name__)

ANSWER_KEY_FILE = "answer_keys.json"
STUDENT_ANSWERS_FILE = "student_answers.json"
KATSAYILAR_FILE = "katsayilar.json"
STUDENT_CODES_FILE = "student_codes.csv"

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

# Katsayıları yükle
def load_katsayilar():
    if os.path.exists(KATSAYILAR_FILE):
        with open(KATSAYILAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Öğrenci kodlarını CSV'den yükle ve set olarak döndür
def load_student_codes():
    if os.path.exists(STUDENT_CODES_FILE):
        codes = set()
        with open(STUDENT_CODES_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                codes.add(row["ogrenci_kodu"].strip())
        return codes
    return set()

# Puan hesaplama (3 yanlış 1 doğru götürür, net = doğru - yanlış/3)
def calculate_score(student_answers, answer_key, katsayilar):
    toplam_puan = 0.0
    for ders, cevaplar in student_answers.items():
        if ders in answer_key and ders in katsayilar:
            dogru_cevaplar = answer_key[ders]
            dogru_sayisi = 0
            yanlis_sayisi = 0
            for ogr_cevap, dogru_cevap in zip(cevaplar, dogru_cevaplar):
                if ogr_cevap == "":
                    continue  # boş soru
                elif ogr_cevap == dogru_cevap:
                    dogru_sayisi += 1
                else:
                    yanlis_sayisi += 1
            net = dogru_sayisi - (yanlis_sayisi / 3)
            katsayi = katsayilar[ders]
            toplam_puan += net * katsayi
    temel_puan = katsayilar.get("temel_puan", 0)
    toplam_puan += temel_puan
    return toplam_puan

@app.route("/", methods=["GET", "POST"])
def index():
    cevap_anahtarlari = load_answer_keys()
    katsayilar = load_katsayilar()
    student_codes = load_student_codes()
    deneme_listesi = list(cevap_anahtarlari.keys())

    if request.method == "POST":
        ogrenci_kodu = request.form.get("ogrenci_kodu", "").strip()
        deneme_kodu = request.form.get("deneme_kodu", "").strip()

        # Öğrenci kodu kontrolü
        if ogrenci_kodu not in student_codes:
            return render_template(
                "index.html",
                hata="Geçersiz öğrenci kodu.",
                deneme_listesi=deneme_listesi,
                cevap_anahtarlari=cevap_anahtarlari
            )

        if not deneme_kodu or deneme_kodu not in cevap_anahtarlari:
            return render_template(
                "index.html",
                hata="Lütfen geçerli bir deneme seçin.",
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
        ogrenci_puan = calculate_score(ogrenci_cevaplari, dersler, katsayilar)

        # Tüm öğrenciler için puan sıralaması
        siralama_listesi = []
        for ogr_kod, cevaplar in tum_cevaplar[deneme_kodu].items():
            puan = calculate_score(cevaplar, dersler, katsayilar)
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
