from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

# Öğrenci giriş kodları ve adları
ogrenciler = {
    '1234': 'Ali',
    '5678': 'Ayşe',
    '9012': 'Mehmet',
}

# Deneme kodlarına göre cevap anahtarları
cevap_anahtarlari = {
    'deneme1': {
        'Turkce':    ['A', 'B', 'C'],
        'Matematik': ['B', 'C', 'D'],
        'Fen':       ['D', 'A', 'C'],
        'Inkilap':   ['C', 'D', 'A'],
        'Din':       ['A', 'A', 'B'],
        'Ingilizce': ['B', 'C', 'D'],
    },
    'deneme2': {
        'Turkce':    ['C', 'C', 'A'],
        'Matematik': ['D', 'D', 'B'],
        'Fen':       ['A', 'B', 'C'],
        'Inkilap':   ['A', 'B', 'C'],
        'Din':       ['C', 'D', 'A'],
        'Ingilizce': ['D', 'C', 'B'],
    }
}

# Anasayfa (giriş ve cevap formu)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ogrenci_kodu = request.form.get('ogrenci_kodu')
        deneme_kodu = request.form.get('deneme_kodu')

        if ogrenci_kodu not in ogrenciler:
            return render_template('index.html', hata="Geçersiz öğrenci kodu")

        if deneme_kodu not in cevap_anahtarlari:
            return render_template('index.html', hata="Geçersiz deneme kodu")

        # Cevapları topla
        dersler = ['Turkce', 'Matematik', 'Fen', 'Inkilap', 'Din', 'Ingilizce']
        ogrenci_cevaplari = {}
        for ders in dersler:
            ogrenci_cevaplari[ders] = []
            for i in range(1, 4):
                cevap = request.form.get(f"{ders}_{i}")
                ogrenci_cevaplari[ders].append(cevap.strip().upper() if cevap else '')

        # Cevapları kontrol et
        sonuc = {}
        anahtar = cevap_anahtarlari[deneme_kodu]
        for ders in dersler:
            ders_sonuclari = []
            for i, ogr_cevap in enumerate(ogrenci_cevaplari[ders]):
                dogru_cevap = anahtar[ders][i]
                if ogr_cevap == '':
                    durum = 'bos'
                elif ogr_cevap == dogru_cevap:
                    durum = 'dogru'
                else:
                    durum = 'yanlis'
                ders_sonuclari.append((ogr_cevap or '-', durum))
            sonuc[ders] = ders_sonuclari

        return render_template('result.html',
                               ogrenci_kodu=ogrenci_kodu,
                               deneme_kodu=deneme_kodu,
                               sonuc=sonuc)
    return render_template('index.html', hata=None)

if __name__ == '__main__':
    app.run(debug=True)
