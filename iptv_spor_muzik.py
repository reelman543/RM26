import requests
import re

def m3u8_coz(icerik):
    kanallar = []
    bloklar = icerik.split('#EXTINF')

    for blok in bloklar[1:]:
        satirlar = blok.strip().split('\n')
        if len(satirlar) < 2:
            continue

        bilgi = satirlar[0]
        url = satirlar[1]

        ad = re.search(r',(.+)', bilgi)
        grup = re.search(r'group-title="([^"]+)"', bilgi)

        kanallar.append({
            'kanal': ad.group(1).strip() if ad else "Bilinmiyor",
            'grup': grup.group(1).strip() if grup else "Genel",
            'url': url
        })

    return kanallar

def sadece_spor_aktif(kanallar):
    return [
        k for k in kanallar
        if "spor" in k['grup'].lower() and baglanti_kontrol(k)
    ]

def baglanti_kontrol(kanal):
    try:
        response = requests.head(kanal['url'], timeout=5, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    except:
        return False

def m3u_kaydet(kanallar, dosya_adi):
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for kanal in kanallar:
            f.write(f'#EXTINF:-1 group-title="{kanal["grup"]}",{kanal["kanal"]}\n')
            f.write(f'{kanal["url"]}\n')
    print(f"[💾] {dosya_adi} kaydedildi. ({len(kanallar)} aktif spor kanalı)")

def main():
    playlist_urls = [
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLive.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewAll.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/StreamEast.m3u8",
        # Diğer URL'ler eklenebilir
    ]

    print("[📡] IPTV listeleri indiriliyor...")
    tum_kanallar = []

    for url in playlist_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                yeni = m3u8_coz(response.text)
                print(f"→ {url.split('/')[-1]}: {len(yeni)} kanal")
                tum_kanallar.extend(yeni)
        except Exception as e:
            print(f"[!] {url} hata verdi: {e}")

    print(f"\n🔍 Spor kategorisi filtreleniyor ve bağlantılar test ediliyor...\n")
    aktif_spor_kanallar = sadece_spor_aktif(tum_kanallar)

    m3u_kaydet(aktif_spor_kanallar, "spor.m3u8")

if __name__ == "__main__":
    main()
