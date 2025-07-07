import requests
import re
import unicodedata

def m3u8_coz(icerik):
    kanallar = []
    bloklar = icerik.split('#EXTINF')

    for blok in bloklar[1:]:
        satirlar = blok.strip().split('\n')
        if len(satirlar) < 2:
            continue

        bilgi = satirlar[0]
        url = satirlar[1].strip()

        if not url.startswith("http"):
            continue

        ad = re.search(r',(.+)', bilgi)
        grup = re.search(r'group-title="([^"]+)"', bilgi)

        kanallar.append({
            'kanal': ad.group(1).strip() if ad else "Bilinmiyor",
            'grup': grup.group(1).strip() if grup else "Genel",
            'url': url
        })

    return kanallar

def kategori_filtrele(kanallar, kategori_adi="spor"):
    return [k for k in kanallar if kategori_adi.lower() in k['grup'].lower()]

def baglanti_kontrol(kanal):
    try:
        response = requests.head(kanal['url'], timeout=5, allow_redirects=True)
        if response.status_code in [405, 403]:
            response = requests.
