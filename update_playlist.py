import urllib.request
import os
import json
import re

# 1. الـ GIST ID الخاص بك
gist_id = "e39d470ae0b80c4bde495ec54476a927"

# 2. روابط السيرفرات الستة
SERVERS = [
    "http://maven@uq3uya.2m2h.im:80/get.php?username=Neserrn202334&password=hGTXB2CzTg4Y&type=m3u_plus",
    "http://core.itsall.pro:80/get.php?username=Allgoodlotfi&password=hhDZSxCpeD&type=m3u&output=mpegts",
    "http://marveliptv.life:80/get.php?username=RLVKClECTD&password=PGr4peyP5U&type=m3u_plus",
    "http://desyra.co:80/get.php?username=dipak_25&password=429502&type=m3u_plus&output=ts",
    "http://live.lynxiptv.xyz:80/get.php?username=206923845871&password=mI45UxamwN&type=m3u_plus",
    "http://1.fu4-pro.cfd:8080/get.php?username=eageapfsat795&password=0d8ie0jv8o&type=m3u_plus"
]

latest_channels = {}

def get_channel_id(extinf_line):
    # استخراج الاسم من نهاية السطر
    name = extinf_line.split(',')[-1].strip()
    
    # القاعدة 1: قنوات TOD والشبيهة (حذف أي شيء بعد علامة |)
    if '|' in name:
        name = name.split('|')[0]
        
    # القاعدة 2: حذف أي نصوص داخل أقواس (غالباً تحتوي على تواريخ مثل (2026-06-06))
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'\[.*?\]', '', name)
    
    # القاعدة 3: حذف التواريخ المكشوفة بصيغة YYYY-MM-DD أو DD-MM-YYYY
    name = re.sub(r'\d{4}-\d{2}-\d{2}.*', '', name)
    name = re.sub(r'\d{2}-\d{2}-\d{4}.*', '', name)
    
    # القاعدة 4: حذف الأوقات بصيغة HH:MM:SS
    name = re.sub(r'\d{2}:\d{2}:\d{2}.*', '', name)

    return name.strip()

# جلب الروابط والأسماء المحدثة من السيرفرات
for url in SERVERS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8').splitlines()
        
        for i in range(len(content)):
            if content[i].startswith('#EXTINF'):
                extinf = content[i].strip()
                channel_url = content[i+1].strip()
                
                uid = get_channel_id(extinf)
                if uid:
                    latest_channels[uid] = {
                        'extinf': extinf,
                        'url': channel_url
                    }
    except:
        continue

# تحديث ملف القنوات (الاسم والرابط معاً)
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
                    file.write(latest_channels[uid]['extinf'] + "\n")
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

# إرسال التحديث إلى الرابط السري (Gist)
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
