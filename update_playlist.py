import urllib.request

# ضع روابط السيرفرات الستة الخاصة بك بين علامات التنصيص
SERVERS = [
    "http://maven@uq3uya.2m2h.im:80/get.php?username=Neserrn202334&password=hGTXB2CzTg4Y&type=m3u_plus",
    "http://core.itsall.pro:80/get.php?username=Allgoodlotfi&password=hhDZSxCpeD&type=m3u&output=mpegts",
    "http://marveliptv.life:80/get.php?username=RLVKClECTD&password=PGr4peyP5U&type=m3u_plus",
    "http://desyra.co:80/get.php?username=dipak_25&password=429502&type=m3u_plus&output=ts",
    "http://live.lynxiptv.xyz:80/get.php?username=206923845871&password=mI45UxamwN&type=m3u_plus",
    "http://1.fu4-pro.cfd:8080/get.php?username=eageapfsat795&password=0d8ie0jv8o&type=m3u_plus"
]

latest_links = {}

# جلب الروابط المحدثة من السيرفرات
for url in SERVERS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8').splitlines()
        
        for i in range(len(content)):
            if content[i].startswith('#EXTINF'):
                channel_name = content[i].split(',')[-1].strip()
                channel_url = content[i+1].strip()
                latest_links[channel_name] = channel_url
    except:
        continue

# تحديث ملفك الخاص
with open('tv_channels_max_servers.m3u', 'r', encoding='utf-8') as file:
    lines = file.readlines()

with open('tv_channels_max_servers.m3u', 'w', encoding='utf-8') as file:
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#EXTINF'):
            file.write(line)
            channel_name = line.split(',')[-1].strip()
            old_url = lines[i+1].strip()
            
            # وضع الرابط الجديد إذا توفر، أو إبقاء القديم
            new_url = latest_links.get(channel_name, old_url)
            file.write(f"{new_url}\n")
            i += 2
        else:
            if line.strip() and not line.startswith('http'):
                file.write(line)
            i += 1
import os
import json

# --- تحديث الرابط السري للتلفاز ---
gist_id = "e39d470ae0b80c4bde495ec54476a927"
token = os.environ.get("GIST_TOKEN")

if token:
    with open('tv_channels_max_servers.m3u', 'r', encoding='utf-8') as f:
        updated_content = f.read()
    
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"files": {"playlist.m3u": {"content": updated_content}}}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='PATCH')
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        pass
