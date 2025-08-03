from flask import Flask, render_template, request, redirect, url_for
import csv
import json

app = Flask(__name__)

# Öğrenci listesini CSV'den oku
def load_students():
    ogrenciler = {}
    with open('student_codes.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                kod, ad = row
                ogrenciler[kod.strip()] = ad.strip()
    return ogrenciler

# Cevap anahtarlarını JSON'dan yükle
def load_answer_keys():
    with open('answer_keys.json', 'r', encoding='utf-8') as f:
        return json.load(f)

ogrenciler = load_students()
cevap_anahtarlari = load_answer_keys()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        girilen_kod = request.form['kod'].strip()
        deneme_kodu = request.form['deneme_kodu'].strip()

        if girilen_kod not in ogrenciler:
            return render_template('index.html', hata="Geçersiz öğrenci kodu.")

        if deneme_kodu not in cevap_anahtarlari:
            return render_template('index.html', hata="Geçersiz deneme kodu.")

        cevap_anahtari = cevap_anahtarlari[deneme_kodu]

        dersler = ['Turkce', 'Matematik', 'Fen', 'Inkilap', 'Din', 'Ingilizce']
        yanitlar = {}
        sonuc = {}

        for ders in dersler:
            yanitlar[ders] = []
            sonuc[ders] = []
            for i in range(len(cevap_anahtari[ders])):
                cevap = request.form.get(f'{ders}_{i+1}', '').strip().upper()
                yanitlar[ders].append(cevap if cevap else '-')
                dogru_cevap = cevap_anahtari[ders][i].upper()
                if not cevap:
                    sonuc[ders].append('-')  # Boş bırakılmış
                elif cevap == dogru_cevap:
                    sonuc[ders].append('✔')
                else:
                    sonuc[ders].append('✘')

        return render_template('result.html',
                               kod=girilen_kod,
                               ad=ogrenciler[girilen_kod],
                               yanitlar=yanitlar,
                               sonuc=sonuc,
                               deneme_kodu=deneme_kodu)

    return render_template('index.html', hata=None)

if __name__ == '__main__':
    app.run(debug=True)
