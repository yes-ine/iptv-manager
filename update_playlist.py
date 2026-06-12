import urllib.request
import os
import json
import re

gist_id = "e39d470ae0b80c4bde495ec54476a927"

XTREAM_SERVERS = [
    {"url": "http://uq3uya.2m2h.im:80", "user": "Neserrn202334", "pass": "hGTXB2CzTg4Y"},
    {"url": "http://core.itsall.pro:80", "user": "Allgoodlotfi", "pass": "hhDZSxCpeD"},
    {"url": "http://desyra.co:80", "user": "dipak_25", "pass": "429502"},
    {"url": "http://live.lynxiptv.xyz:80", "user": "206923845871", "pass": "mI45UxamwN"},
    {"url": "http://1.fu4-pro.cfd", "user": "eageapfsat795", "pass": "0d8ie0jv8o"}
]

latest_channels = {}
# إنشاء عداد فارغ لكل سيرفر
updated_counts = {srv['url']: 0 for srv in XTREAM_SERVERS}

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

print("بدء جلب القنوات من سيرفرات إكستريم...")
for server in XTREAM_SERVERS:
    api_url = f"{server['url']}/player_api.php?username={server['user']}&password={server['pass']}&action=get_live_streams"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'IPTVSmartersPro'})
        response = urllib.request.urlopen(req, timeout=15)
        streams = json.loads(response.read().decode('utf-8'))
        
        print(f"✅ تم الاتصال بنجاح بالسيرفر: {server['url']}")
        
        for stream in streams:
            if 'name' in stream and 'stream_id' in stream:
                uid = get_channel_id(stream['name'])
                if uid:
                    stream_url = f"{server['url']}/{server['user']}/{server['pass']}/{stream['stream_id']}"
                    latest_channels[uid] = {
                        'server_name': stream['name'].strip(),
                        'url': stream_url,
                        'server_url': server['url'] # نحتفظ برابط السيرفر المصدر
                    }
    except Exception as e:
        print(f"❌ خطأ في السيرفر {server['url']}: {e}")
        continue

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
                    source_url = latest_channels[uid]['server_url']
                    
                    file.write(f"{local_prefix},{server_name}\n")
                    file.write(latest_channels[uid]['url'] + "\n")
                    
                    # زيادة العداد عند التحديث الفعلي للقناة
                    if source_url in updated_counts:
                        updated_counts[source_url] += 1
                else:
                    file.write(line)
                    file.write(old_url + "\n")
                i += 2
            else:
                if line.strip() and not line.startswith('http'):
                    file.write(line)
                i += 1
                
    # طباعة النتيجة النهائية
    print("\n📊 إحصائيات التحديث الفعلي داخل ملفك:")
    for srv_url, count in updated_counts.items():
        if count > 0:
            print(f"🔹 {srv_url} : تم تحديث {count} قناة")
            
except Exception as e:
    print(f"❌ خطأ أثناء تحديث الملف: {e}")

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
        print("✅ تم تحديث Gist.")
    except Exception as e:
        print(f"❌ خطأ Gist: {e}")
