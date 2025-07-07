import requests
from collections import defaultdict
import re
from datetime import datetime

playlist_urls = [
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLive.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewAll.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/JapanTV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DrewLiveVOD.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/UDPTV.m3u8",  # DÜZELTİLDİ
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/Drew247TV.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/DaddyLiveEvents.m3u8",
    "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/StreamEast.m3u8",
]

UDPTV_URL = "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/UDPTV.m3u8"  # DÜZELTİLDİ
EPG_URL = "https://tinyurl.com/merged2423-epg"
OUTPUT_FILE = "AbuzerPlaylist.m3u8"

def fetch_playlist(url):
    print(f"📡 Fetching: {url}")
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.content.decode('utf-8', errors='ignore').strip().splitlines()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
    return []

def extract_timestamp_from_udptv(lines):
    for line in lines:
        if line.strip().startswith("# Last forced update:"):
            print(f"🕒 Found timestamp: {line.strip()}")
            return line.strip()
    print("⚠️ No update timestamp found in UDPTV.")
    return None

def parse_playlist(lines, source_url="Unknown"):
    parsed = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            extinf = line
            headers = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith("#") and not lines[i].strip().startswith("#EXTINF:"):
                headers.append(lines[i].strip())
                i += 1
            if i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("#"):
                url = lines[i].strip()
                parsed.append((extinf, tuple(headers), url))
                i += 1
            else:
                print(f"⚠️ Malformed entry in {source_url} at line {i}: Missing URL.")
        else:
            i += 1
    print(f"✅ Parsed {len(parsed)} channels from {source_url}")
    return parsed

def write_merged_playlist(channels, timestamp):
    lines = [f'#EXTM3U url-tvg="{EPG_URL}"']
    if timestamp:
        lines.append(timestamp)
    lines.append("")

    sortable = []
    for extinf, headers, url in channels:
        group_match = re.search(r'group-title="([^"]+)"', extinf)
        group = group_match.group(1) if group_match else "Other"
        title_match = re.search(r',([^,]+)$', extinf)
        title = title_match.group(1).strip() if title_match else ""
        sortable.append((group.lower(), title.lower(), extinf, headers, url))

    sortable.sort()
    current_group = None
    total = 0

    for group_l, title_l, extinf, headers, url in sortable:
        group_match = re.search(r'group-title="([^"]+)"', extinf)
        group_name = group_match.group(1) if group_match else "Other"
        if group_name != current_group:
            if current_group is not None:
                lines.append("")
            lines.append(f"#EXTGRP:{group_name}")
            current_group = group_name
        lines.append(extinf)
        lines.extend(headers)
        lines.append(url)
        total += 1

    output = "\n".join(lines).strip() + "\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n✅ Merged {total} unique channels into: {OUTPUT_FILE}")
    print(f"🧾 Total lines written: {len(output.splitlines())}")

if __name__ == "__main__":
    print(f"🚀 Starting merge at {datetime.now()}\n")

    all_channels = set()
    print(f"--- Processing UDPTV ---")
    udptv_lines = fetch_playlist(UDPTV_URL)
    timestamp = extract_timestamp_from_udptv(udptv_lines)
    all_channels.update(parse_playlist(udptv_lines, UDPTV_URL))

    print(f"\n--- Processing other playlists ---")
    for url in playlist_urls:
        if url == UDPTV_URL:
            continue
        lines = fetch_playlist(url)
        parsed = parse_playlist(lines, url)
        all_channels.update(parsed)

    write_merged_playlist(list(all_channels), timestamp)
    print(f"✅ Merge completed at {datetime.now()}")
