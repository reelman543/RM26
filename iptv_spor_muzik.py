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

def kategori_filtrele(kanallar, kategoriler):
    return [k for k in kanallar if any(kat.lower() in k['grup'].lower() or kat.lower() in k['kanal'].lower() for kat in kategoriler)]

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
    print(f"[💾] {dosya_adi} kaydedildi. ({len(kanallar)} kanal)")

def main():
    playlist_urls = [
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLive.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewAll.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/JapanTV.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/PlexTV.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/PlutoTV.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/SamsungTVPlus.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/TubiTV.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewLiveVOD.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Drew247TV.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/TVPass.m3u",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Radio.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/PPVLand.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/StreamEast.m3u8",
        "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/FSTV24.m3u8",
    ]

    print("[📡] Tüm IPTV listeleri indiriliyor...")
    kanallar = []

    for url in playlist_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                yeni_kanallar = m3u8_coz(response.text)
                print(f"→ {url.split('/')[-1]}: {len(yeni_kanallar)} kanal bulundu.")
                kanallar.extend(yeni_kanallar)
            else:
                print(f"[!] {url} alınamadı: {response.status_code}")
        except Exception as e:
            print(f"[!] {url} hata verdi: {e}")

    print(f"\n🔢 Toplam {len(kanallar)} kanal toplandı.\n")

    # Sadece Spor ve Müzik kategorilerini filtrele
    kategoriler = ["Sport", "Spor", "Music", "Müzik"]
    filtreli = kategori_filtrele(kanallar, kategoriler)

    print(f"[🔍] Spor ve Müzik kategorilerinde {len(filtreli)} kanal bulundu.\n")

    aktif_kanallar = []
    for i, kanal in enumerate(filtreli, start=1):
        if baglanti_kontrol(kanal):
            aktif_kanallar.append(kanal)
            print(f"{i:02d}. ✅ {kanal['kanal']} ({kanal['grup']})")
        else:
            print(f"{i:02d}. ❌ {kanal['kanal']} ({kanal['grup']})")

    # Sadece aktif kanallar spor.m3u8 olarak kaydedilecek
    m3u_kaydet(aktif_kanallar, "spor.m3u8")

    print(f"\n✅ Toplam {len(aktif_kanallar)} aktif kanal kaydedildi.")

if __name__ == "__main__":
    main()
