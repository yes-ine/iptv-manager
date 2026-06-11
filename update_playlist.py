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
    # 1. تخصيص قنوات TOD EV لأنها تتغير بالكامل (نستخرج فقط المعرف مثل TOD EV 019)
    tod_match = re.search(r'TOD EV \d+', extinf_line, re.IGNORECASE)
    if tod_match:
        return tod_match.group(0).upper().strip()
        
    # 2. القنوات الأخرى: جلب الاسم من tvg-name أو من بعد الفاصلة الأخيرة
    tvg_match = re.search(r'tvg-name="([^"]+)"', extinf_line)
    if tvg_match:
        name = tvg_match.group(1).strip()
    else:
        name = extinf_line.split(',')[-1].strip()
        
    # تنظيف التواريخ والأوقات لتبقى هوية القنوات ثابتة للمطابقة
    name = re.sub(r'\s*\(?\[?\d{1,2}[-/]\d{1,2}[-/]?\d*.*', '', name)
    name = re.sub(r'\s*\(?\[?\d{2}:\d{2}.*', '', name)
    return name.strip()

# جلب البيانات من السيرفرات
print("بدء جلب القنوات من السيرفرات...")
for url in SERVERS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8').splitlines()
        print(f"تم جلب {len(content)} سطر بنجاح من السيرفر: {url[:35]}...")
        
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
    except Exception as e:
        print(f"خطأ أثناء الجلب من السيرفر {url[:35]}: {e}")
        continue

print(f"إجمالي القنوات الفريدة المكتشفة من السيرفرات: {len(latest_channels)}")

# تحديث الملف المحلي
updated_count = 0
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
                    updated_count += 1
                else:
                    file.write(line)
                    file.write(old_url + "\n")
                i += 2
            else:
                if line.strip() and not line.startswith('http'):
                    file.write(line)
                i += 1
    print(f"تم تحديث أسماء وروابط {updated_count} قناة داخل الملف بنجاح.")
except Exception as e:
    print(f"خطأ أثناء تحديث الملف المحلي: {e}")

# تحديث الـ Gist للاحتياط
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
        print("تم تحديث الـ Gist بنجاح.")
    except Exception as e:
        print(f"فشل تحديث الـ Gist: {e}")
