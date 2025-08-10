from flask import Flask, render_template, request
import csv
import json
from pathlib import Path

app = Flask(__name__)

RESULTS_FILE = Path("results.json")

# Öğrenci listesini CSV'den oku
def load_students():
    students = {}
    with open('student_codes.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            students[row['ogrenci_kodu']] = row['ogrenci_adi']
    return students

# Cevap anahtarlarını JSON'dan yükle
def load_answer_keys():
    with open('answer_keys.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Katsayıları yükle ve puan hesapla
def puan_hesapla(netler):
    with open('katsayilar.json', 'r', encoding='utf-8') as f:
        katsayilar = json.load(f)

    temel_puan = katsayilar.pop("temel_puan", 200)
    puan = temel_puan + sum(net * katsayilar.get(ders, 0) for ders, net in netler.items())
    return round(puan, 2)

def load_results():
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_results(data):
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    ogrenciler = load_students()
    cevap_anahtarlari = load_answer_keys()
    deneme_listesi = list(cevap_anahtarlari.keys())

    hata = None

    if request.method == 'POST':
        ogrenci_kodu = request.form.get('ogrenci_kodu', '').strip()
        deneme_kodu = request.form.get('deneme_kodu', '').strip()

        if ogrenci_kodu not in ogrenciler:
            return render_template(
                'index.html',
                hata="Geçersiz öğrenci kodu.",
                deneme_listesi=deneme_listesi,
                cevap_anahtarlari=cevap_anahtarlari
            )

        if deneme_kodu not in cevap_anahtarlari:
            return render_template(
                'index.html',
                hata="Geçersiz deneme kodu.",
                deneme_listesi=deneme_listesi,
                cevap_anahtarlari=cevap_anahtarlari
            )

        cevap_anahtari = cevap_anahtarlari[deneme_kodu]
        yanitlar = {}
        sonuc = {}
        netler = {}

        dogru_sayisi_genel = 0
        yanlis_sayisi_genel = 0
        bos_sayisi_genel = 0

        for ders, cevaplar in cevap_anahtari.items():
            yanitlar[ders] = []
            sonuc[ders] = []

            dogru_sayisi = 0
            yanlis_sayisi = 0
            bos_sayisi = 0

            for i, dogru_cevap in enumerate(cevaplar):
                kullanici_cevap = request.form.get(f'{ders}_{i+1}', '').strip().upper()
                yanitlar[ders].append(kullanici_cevap if kullanici_cevap else '-')

                if not kullanici_cevap:
                    sonuc[ders].append({
                        "durum": "boş",
                        "dogru": dogru_cevap,
                        "verilen": "-"
                    })
                    bos_sayisi += 1
                elif kullanici_cevap == dogru_cevap.upper():
                    sonuc[ders].append({
                        "durum": "doğru",
                        "dogru": dogru_cevap,
                        "verilen": kullanici_cevap
                    })
                    dogru_sayisi += 1
                else:
                    sonuc[ders].append({
                        "durum": "yanlış",
                        "dogru": dogru_cevap,
                        "verilen": kullanici_cevap
                    })
                    yanlis_sayisi += 1

            net = round(dogru_sayisi - (yanlis_sayisi / 3), 2)
            netler[ders] = net

            dogru_sayisi_genel += dogru_sayisi
            yanlis_sayisi_genel += yanlis_sayisi
            bos_sayisi_genel += bos_sayisi

        puan = puan_hesapla(netler)

        # Sonucu kayıt listesine ekle
        all_results = load_results()
        all_results.append({
            "ogrenci_kodu": ogrenci_kodu,
            "ogrenci_adi": ogrenciler[ogrenci_kodu],
            "deneme_kodu": deneme_kodu,
            "netler": netler,
            "puan": puan
        })
        save_results(all_results)

        # Puan üstünlüğüne göre sıralı liste
        sirali_sonuc = sorted(all_results, key=lambda x: x["puan"], reverse=True)

        return render_template(
            'result.html',
            kod=ogrenci_kodu,
            ad=ogrenciler[ogrenci_kodu],
            yanitlar=yanitlar,
            sonuc=sonuc,
            netler=netler,
            puan=puan,
            deneme_kodu=deneme_kodu,
            sirali_sonuc=sirali_sonuc
        )

    return render_template(
        'index.html',
        hata=None,
        deneme_listesi=deneme_listesi,
        cevap_anahtarlari=cevap_anahtarlari
    )
def index():
    with open("answer_keys.json", "r", encoding="utf-8") as f:
        cevap_anahtarlari = json.load(f)

    if request.method == "POST":
        ogrenci_kodu = request.form["ogrenci_kodu"]
        deneme_kodu = request.form["deneme_kodu"]

        # Öğrenci cevaplarını al
        ogrenci_cevaplari = {}
        for ders, cevaplar in cevap_anahtarlari[deneme_kodu].items():
            ogrenci_cevaplari[ders] = []
            for i in range(len(cevaplar)):
                key = f"{ders}_{i+1}"
                ogrenci_cevaplari[ders].append(request.form.get(key, "").strip().upper())

        # Sonuç hesaplama
        sonuc = {}
        for ders, dogru_cevaplar in cevap_anahtarlari[deneme_kodu].items():
            dogru = sum(1 for i, c in enumerate(ogrenci_cevaplari[ders]) if c == dogru_cevaplar[i])
            bos = sum(1 for c in ogrenci_cevaplari[ders] if c == "")
            yanlis = len(dogru_cevaplar) - dogru - bos
            sonuc[ders] = {"dogru": dogru, "yanlis": yanlis, "bos": bos}

        return render_template(
            "result.html",
            ogrenci_kodu=ogrenci_kodu,
            deneme_kodu=deneme_kodu,
            cevaplar=ogrenci_cevaplari,
            cevap_anahtarlari=cevap_anahtarlari[deneme_kodu],
            sonuc=sonuc
        )

    return render_template("index.html", cevap_anahtarlari=cevap_anahtarlari, deneme_listesi=list(cevap_anahtarlari.keys()))
if __name__ == '__main__':
    app.run(debug=True)
