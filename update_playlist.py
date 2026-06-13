import urllib.request
import os
import json
import re

gist_id = "e39d470ae0b80c4bde495ec54476a927"

# السيرفرات القديمة (لتحديث القنوات الموجودة)
XTREAM_SERVERS = [
    {"url": "http://uq3uya.2m2h.im:80", "user": "Neserrn202334", "pass": "hGTXB2CzTg4Y"},
    {"url": "http://core.itsall.pro:80", "user": "Allgoodlotfi", "pass": "hhDZSxCpeD"},
    {"url": "http://desyra.co:80", "user": "dipak_25", "pass": "429502"},
    {"url": "http://live.lynxiptv.xyz:80", "user": "206923845871", "pass": "mI45UxamwN"},
    {"url": "http://1.fu4-pro.cfd", "user": "eageapfsat795", "pass": "0d8ie0jv8o"},
    {"url": "http://marveliptv.life:80", "user": "RLVKClECTD", "pass": "PGr4peyP5U"}
]

# السيرفرات الجديدة (لإضافة قنوات محددة)
NEW_SERVERS = [
    {"name": "Hydra", "url": "http://hydraa.st:80", "user": "ssd990987", "pass": "bgb6669099", "keywords": ["bein", "alwan"]},
    {"name": "Aroma", "url": "http://my.atrupo4k.com:80", "user": "youssef2506", "pass": "hAXNTNSJWRjE2Bv", "keywords": ["ar| fifa world cup"]},
    {"name": "Legend", "url": "http://legendking.net:80", "user": "imaneomar", "pass": "e3hzfxuo", "keywords": ["fifa world cup"]},
    {"name": "Digi", "url": "http://digi.dtv3.lol:2082", "user": "mejdoubnew_958581", "pass": "CHmNLjSr", "keywords": ["fifa world cup", "tod bein sports"]},
    {"name": "Sans", "url": "http://sans7.org:88", "user": "70:b1:3d:e4:e9:b0", "pass": "PDZOITARCX", "keywords": ["world cup 2026"]}
]

latest_channels = {}
updated_counts = {srv['url']: 0 for srv in XTREAM_SERVERS}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*'
}

def get_channel_id(name_str):
    tod_match = re.search(r'TOD EV \d+', name_str, re.IGNORECASE)
    if tod_match: return tod_match.group(0).upper().strip()
    tvg_match = re.search(r'tvg-name="([^"]+)"', name_str)
    if tvg_match:
        name = tvg_match.group(1).strip()
    else:
        name = name_str.split(',')[-1].strip()
    name = re.sub(r'\s*\(?\[?\d{1,2}[-/]\d{1,2}[-/]?\d*.*', '', name)
    name = re.sub(r'\s*\(?\[?\d{2}:\d{2}.*', '', name)
    return name.strip()

print("بدء جلب القنوات للتحديث...")
for server in XTREAM_SERVERS:
    api_url = f"{server['url']}/player_api.php?username={server['user']}&password={server['pass']}&action=get_live_streams"
    try:
        req = urllib.request.Request(api_url, headers=HEADERS)
        response = urllib.request.urlopen(req, timeout=15)
        streams = json.loads(response.read().decode('utf-8'))
        print(f"✅ تم الاتصال بنجاح بالسيرفر القديم: {server['url']}")
        for stream in streams:
            if 'name' in stream and 'stream_id' in stream:
                uid = get_channel_id(stream['name'])
                if uid:
                    if "lynxiptv" in server['url']:
                    stream_url = f"http://ibo.lynxiptv.com/live/{server['user']}/{server['pass']}/{stream['stream_id']}.m3u8"
                else:
                    stream_url = f"{server['url']}/{server['user']}/{server['pass']}/{stream['stream_id']}"
                    latest_channels[uid] = {
                        'server_name': stream['name'].strip(),
                        'url': stream_url,
                        'server_url': server['url']
                    }
    except Exception as e:
        print(f"❌ خطأ في السيرفر {server['url']}: {e}")
        continue

print("\nبدء جلب القنوات الجديدة...")
new_channels_lines = []
for server in NEW_SERVERS:
    cat_url = f"{server['url']}/player_api.php?username={server['user']}&password={server['pass']}&action=get_live_categories"
    streams_url = f"{server['url']}/player_api.php?username={server['user']}&password={server['pass']}&action=get_live_streams"
    try:
        req_cat = urllib.request.Request(cat_url, headers=HEADERS)
        cats_data = json.loads(urllib.request.urlopen(req_cat, timeout=15).read().decode('utf-8'))
        
        valid_cats = {}
        for cat in cats_data:
            cat_name = str(cat.get('category_name', ''))
            if any(kw.lower() in cat_name.lower() for kw in server['keywords']):
                valid_cats[str(cat.get('category_id'))] = f"[{server['name']}] {cat_name}"
        
        if valid_cats:
            req_str = urllib.request.Request(streams_url, headers=HEADERS)
            streams_data = json.loads(urllib.request.urlopen(req_str, timeout=15).read().decode('utf-8'))
            count = 0
            for stream in streams_data:
                cat_id = str(stream.get('category_id'))
                if cat_id in valid_cats:
                    name = stream.get('name', '').strip()
                    stream_id = stream.get('stream_id')
                    logo = stream.get('stream_icon', '')
                    group_title = valid_cats[cat_id]
                    stream_url = f"{server['url']}/{server['user']}/{server['pass']}/{stream_id}"
                    
                    extinf = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title}",{name}\n'
                    new_channels_lines.append(extinf)
                    new_channels_lines.append(f"{stream_url}\n")
                    count += 1
            print(f"✅ تمت إضافة {count} قناة من سيرفر {server['name']}")
        else:
            print(f"⚠️ لم يتم العثور على مجموعات مطابقة في {server['name']}")
    except Exception as e:
        print(f"❌ خطأ في السيرفر الجديد {server['name']}: {e}")

try:
    with open('tv_channels_max_servers.m3u', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open('tv_channels_max_servers.m3u', 'w', encoding='utf-8') as file:
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('#EXTINF'):
                # تفادي التكرار لجميع السيرفرات الجديدة المضافة
                if any(f'group-title="[{ns["name"]}]' in line for ns in NEW_SERVERS):
                    i += 2
                    continue
                    
                uid = get_channel_id(line)
                old_url = lines[i+1].strip() if (i+1) < len(lines) else ""
                
                if uid in latest_channels:
                    local_prefix = line.rsplit(',', 1)[0]
                    server_name = latest_channels[uid]['server_name']
                    source_url = latest_channels[uid]['server_url']
                    
                    file.write(f"{local_prefix},{server_name}\n")
                    file.write(latest_channels[uid]['url'] + "\n")
                    if source_url in updated_counts:
                        updated_counts[source_url] += 1
                else:
                    file.write(line)
                    if old_url:
                        file.write(old_url + "\n")
                i += 2
            else:
                if line.strip() and not line.startswith('http'):
                    file.write(line)
                i += 1
                
        if new_channels_lines:
            file.writelines(new_channels_lines)
            
    print("\n📊 إحصائيات التحديث:")
    for srv_url, count in updated_counts.items():
        if count > 0:
            print(f"🔹 {srv_url} : تم تحديث {count} قناة قديمة")
            
except Exception as e:
    print(f"❌ خطأ أثناء التحديث: {e}")

token = os.environ.get("GIST_TOKEN")
if token and gist_id != "ضع_الـID_هنا":
    try:
        with open('tv_channels_max_servers.m3u', 'r', encoding='utf-8') as f:
            updated_content = f.read()
        url = f"https://api.github.com/gists/{gist_id}"
        req = urllib.request.Request(url, data=json.dumps({"files": {"playlist.m3u": {"content": updated_content}}}).encode('utf-8'), headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"})
        req.get_method = lambda: 'PATCH'
        urllib.request.urlopen(req)
        print("✅ تم تحديث Gist.")
    except Exception as e:
        print(f"❌ خطأ Gist: {e}")
