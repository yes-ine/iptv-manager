import urllib.request
import os
import json
import re

# 1. الـ GIST ID الخاص بك
gist_id = "e39d470ae0b80c4bde495ec54476a927"

# 2. بيانات سيرفرات إكستريم (مستخرجة من روابطك الأصلية)
XTREAM_SERVERS = [
    {"url": "http://uq3uya.2m2h.im:80", "user": "Neserrn202334", "pass": "hGTXB2CzTg4Y"},
    {"url": "http://core.itsall.pro:80", "user": "Allgoodlotfi", "pass": "hhDZSxCpeD"},
    {"url": "http://desyra.co:80", "user": "dipak_25", "pass": "429502"},
    {"url": "http://live.lynxiptv.xyz:80", "user": "206923845871", "pass": "mI45UxamwN"},
    {"url": "http://1.fu4-pro.cfd", "user": "eageapfsat795", "pass": "0d8ie0jv8o"}
]

latest_channels = {}

def get_channel_id(name_str):
    tod_match = re.search(r'TOD EV \d+', name_str, re.IGNORECASE)
    if tod_match:
        return tod_match.group(0).upper().strip()
        
    tvg_match = re.search(r'tvg-name="([^"]+)"', name_str)
    if tvg_match:
        name = tvg_match.group(1).strip()
    else:
        name = name_str.split(',')[-1].strip()
        
    name = re.sub(r'\s*\(?\[?\d{1,2}[-/]\d{1,2}[-/]?\d*.*', '', name)
    name = re.sub(r'\s*\(?\[?\d{2}:\d{2}.*', '', name)
    return name.strip()

# جلب البيانات عبر نظام إكستريم (JSON)
print("بدء جلب القنوات من سيرفرات إكستريم...")
for server in XTREAM_SERVERS:
    api_url = f"{server['url']}/player_api.php?username={server['user']}&password={server['pass']}&action=get_live_streams"
    try:
        # استخدام هُوية تطبيق IPTV لتجنب الحظر
        req = urllib.request.Request(api_url, headers={'User-Agent': 'IPTVSmartersPro'})
        response = urllib.request.urlopen(req, timeout=15)
        
        streams = json.loads(response.read().decode('utf-8'))
        
        count = 0
        for stream in streams:
            if 'name' in stream and 'stream_id' in stream:
                uid = get_channel_id(stream['name'])
                if uid:
                    stream_url = f"{server['url']}/{server['user']}/{server['pass']}/{stream['stream_id']}"
                    latest_channels[uid] = {
                        'server_name': stream['name'].strip(),
                        'url': stream_url
                    }
                    count += 1
                    
        print(f"✅ تم جلب البيانات بنجاح من: {server['url']} (عدد القنوات: {count})")
        
    except Exception as e:
        print(f"❌ خطأ في السيرفر {server['url']}: {e}")
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
                    local_prefix = line.rsplit(',', 1)[0]
                    server_name = latest_channels[uid]['server_name']
                    
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
    print("تم تحديث الملف المحلي بنجاح.")
except Exception as e:
    print(f"خطأ أثناء تحديث الملف: {e}")

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
        print("تم تحديث Gist.")
    except Exception as e:
        print(f"خطأ Gist: {e}")
