"""تحديث يومي لمقاطع لولوتيوب من خلاصات RSS لقنوات يوتيوب."""
import json, re, sys, time, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

DATA = "data.json"
KEEP = 45  # أقصى عدد مقاطع محفوظة لكل قناة
UA = {"User-Agent": "Mozilla/5.0 (LoLoTube daily updater)"}
BAD = re.compile(r"krishna|ganesh|hanuman|diwali|deepavali|\bholi\b|shiva|vishnu|buddha|\brama\b|ramayan|mahabharat|navratri|\bpuja\b|pooja|temple|mytholog|\bgods?\b|goddess|zeus|\bthor\b|odin|idol|yoga|namaste|chakra|meditat|mindful|zodiac|horoscope|astrolog|wish|witch|wizard|sorcer|magic spell|tarot|church|jesus|bible|christmas|xmas|easter|santa|halloween|spooky|skeleton|skull|haunted|frankenstein|pumpkin|trick.or.treat|ghost|vampire|zombie|demon|devil|valentine|\blove\b|kiss|prank|scary|horror|creep|monster(?!\s*truck)|afraid of the dark|يوغا|معبد|آلهة|الآلهة|أبراج|الأبراج|ساحر|ساحرة|السحرة|شعوذة|تعويذة|كنيسة|المسيح|كريسماس|الكريسماس|هالوين|الهالوين|عيد الحب|عيد الميلاد|بابا نويل|سانتا|شبح|أشباح|الجن|مصاص|زومبي|شيطان|رعب|مرعب|الوحش|وحوش|#shorts|[ऀ-෿]", re.I)
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "media": "http://search.yahoo.com/mrss/"}

def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
opener = urllib.request.build_opener(NoRedirect)

def is_short(vid):
    """رابط /shorts/ يرجع 200 للمقاطع القصيرة ويحوّل للمقاطع العادية."""
    try:
        r = opener.open(urllib.request.Request("https://www.youtube.com/shorts/" + vid, headers=UA, method="HEAD"), timeout=15)
        return r.status == 200
    except urllib.error.HTTPError as e:
        return False
    except Exception:
        return False

def main():
    d = json.load(open(DATA, encoding="utf-8"))
    added = 0; failed = 0
    for c in d["channels"]:
        try:
            root = ET.fromstring(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + c["id"]))
        except Exception as e:
            failed += 1; continue
        have = {v[0] for v in c["v"]}
        new = []
        for en in root.findall("a:entry", NS):
            vid = en.findtext("yt:videoId", "", NS); title = (en.findtext("a:title", "", NS) or "").strip()
            if not vid or vid in have or not title or BAD.search(title): continue
            if is_short(vid): continue
            new.append([vid, title, "", ""])
            time.sleep(0.2)
        if new:
            c["v"] = (new + c["v"])[:KEEP]; added += len(new)
        time.sleep(0.3)
    print(f"added={added} failed_channels={failed}")
    if failed > len(d["channels"]) // 2:
        print("too many failures, not writing"); sys.exit(0)
    if added:
        d["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

if __name__ == "__main__":
    main()
