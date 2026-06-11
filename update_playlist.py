import urllib.request
import os
import json
import re

# 1. الـ GIST ID الخاص بك
gist_id = "e39d470ae0b80c4bde495ec54476a927"

# 2. روابط السيرفرات (ضع روابطك الحالية هنا كما هي في ملفك لتجنب أي أخطاء)
SERVERS = [
    "http://maven@uq3uya.2m2h.im:80/get.php?username=Neserrn202334&password=hGTXB2CzTg4Y&type=m3u_plus",
    "http://core.itsall.pro:80/get.php?username=Allgoodlotfi&password=hhDZSxCpeD&type=m3u&output=mpegts",
    "http://marveliptv.life:80/get.php?username=RLVKClECTD&password=PGr4peyP5U&type=m3u_plus",
    "http://desyra.co:80/get.php?username=dipak_25&password=429502&type=m3u_plus&output=ts",
    "http://live.lynxiptv.xyz:80/get.php?username=206923845871&password=mI45UxamwN&type=m3u_plus",
    "https://xtream-api.org/get.php?username=3V921HB98qU&password=2DQJdcu2N&type=m3u_plus"
]

latest_channels = {}

def get_channel_id(extinf_line):
    tod_match = re.search(r'TOD EV \d+', extinf_line, re.IGNORECASE)
    if tod_match:
        return tod_match.group(0).upper().strip()
        
    tvg_match = re.search(r'tvg-name="([^"]+)"', extinf_line)
    if tvg_match:
        name = tvg_match.group(1).strip()
    else:
        name = extinf_line.split(',')[-1].strip()
        
    name = re.sub(r'\s*\(?\[?\d{1,2}[-/]\d{1,2}[-/]?\d*.*', '', name)
    name = re.sub(r'\s*\(?\[?\d{2}:\d{2}.*', '', name)
    return name.strip()

# جلب البيانات من السيرفرات
for url in SERVERS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'VLC/3.0.16 LibVLC/3.0.16'})
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8').splitlines()
        
        for i in range(len(content)):
            if content[i].startswith('#EXTINF'):
                extinf = content[i].strip()
                channel_url = content[i+1].strip()
                
                uid = get_channel_id(extinf)
                if uid:
                    latest_channels[uid] = {
                        'server_name': extinf.split(',')[-1].strip(), # نأخذ الاسم فقط
                        'url': channel_url
                    }
    except Exception as e:
        continue

# تحديث الملف المحلي مع الحفاظ على المجموعات
try:
    with open('tv_channels_max_servers.m3u', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open('tv_channels_max_servers.m3u', 'w', encoding='utf-8') as file:
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('#EXTINF'):
                uid = get_channel_id(line)
                old_url = lines[i+1].strip()
                
                if uid in latest_channels:
                    # فصل إعداداتك المحلية (بما فيها المجموعات)
                    local_prefix = line.rsplit(',', 1)[0]
                    server_name = latest_channels[uid]['server_name']
                    
                    # دمج إعداداتك مع الاسم المحدث
                    file.write(f"{local_prefix},{server_name}\n")
                    file.write(latest_channels[uid]['url'] + "\n")
                else:
                    file.write(line)
                    file.write(old_url + "\n")
                i += 2
            else:
                if line.strip() and not line.startswith('http'):
                    file.write(line)
                i += 1
except Exception as e:
    pass

# تحديث الـ Gist
token = os.environ.get("GIST_TOKEN")
if token and gist_id != "ضع_الـID_هنا":
    try:
        with open('tv_channels_max_servers.m3u', 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        url = f"https://api.github.com/gists/{gist_id}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {"files": {"playlist.m3u": {"content": updated_content}}}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='PATCH')
        urllib.request.urlopen(req)
    except Exception as e:
        pass
