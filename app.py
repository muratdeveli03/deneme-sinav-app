from flask import Flask, render_template, request
import csv
import json

app = Flask(__name__)

# Öğrenci listesini CSV'den oku
def load_students():
    students = {}
    with open('student_codes.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            students[row['ogrenci_kodu']] = row['ogrenci_adi']
    return students

ogrenciler = load_students()

# Cevap anahtarlarını JSON'dan yükle
def load_answer_keys():
    with open('answer_keys.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    ogrenciler = load_students()
    cevap_anahtarlari = load_answer_keys()

    if request.method == 'POST':
        ogrenci_kodu = request.form.get('ogrenci_kodu', '').strip()
        deneme_kodu = request.form.get('deneme_kodu', '').strip()

        if ogrenci_kodu not in ogrenciler:
            return render_template('index.html', hata="Geçersiz öğrenci kodu.", dersler=get_dersler())

        if deneme_kodu not in cevap_anahtarlari:
            return render_template('index.html', hata="Geçersiz deneme kodu.", dersler=get_dersler())

        cevap_anahtari = cevap_anahtarlari[deneme_kodu]
        dersler = cevap_anahtari.keys()

        yanitlar = {}
        sonuc = {}

        for ders in dersler:
            yanitlar[ders] = []
            sonuc[ders] = []

            for i, dogru_cevap in enumerate(cevap_anahtari[ders]):
                kullanici_cevap = request.form.get(f'{ders}_{i+1}', '').strip().upper()
                yanitlar[ders].append(kullanici_cevap if kullanici_cevap else '-')

                if not kullanici_cevap:
                    sonuc[ders].append('-')
                elif kullanici_cevap == dogru_cevap.upper():
                    sonuc[ders].append('✔')
                else:
                    sonuc[ders].append('✘')
                    
                # Net hesaplama
            istatistik = {}
            for ders in dersler:
                dogru = sonuc[ders].count('✔')
                yanlis = sonuc[ders].count('✘')
                bos = sonuc[ders].count('-')
                net = dogru - (yanlis / 3)
                istatistik[ders] = {
                'dogru': dogru,
                'yanlis': yanlis,
                'bos': bos,
                'net': round(net, 2)
                    }

        return render_template('result.html',
                               kod=ogrenci_kodu,
                               ad=ogrenciler[ogrenci_kodu],
                               yanitlar=yanitlar,
                               sonuc=sonuc,
                               deneme_kodu=deneme_kodu,
                              istatistik=istatistik)

    return render_template('index.html', hata=None, dersler=get_dersler())

# Cevap anahtarlarından ders ve soru sayılarını al
def get_dersler():
    cevap_anahtarlari = load_answer_keys()
    if not cevap_anahtarlari:
        return {}
    # İlk deneme setinden ders ve soru sayılarını çıkar
    first_key = next(iter(cevap_anahtarlari))
    return {ders: len(sorular) for ders, sorular in cevap_anahtarlari[first_key].items()}

if __name__ == '__main__':
    app.run(debug=True)
