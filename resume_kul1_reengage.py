#!/usr/bin/env python3
"""
Скрипт відновлення kul1-reengage розсилки.
Запускати з: python3 resume_kul1_reengage.py
Автоматично пропускає всіх кому вже надіслано (перевіряє sent_emails_log.json).
"""
import csv, json, smtplib, time, re, os

CSVS = [
    ('/root/.openclaw/media/inbound/leads_1f3f6f8f965e88a4a14d3fbe15479d940135215c4f84190b764085---ffd20f6b-6c6d-4007-8b78-641e8692faa7.csv', 'Email', 'Name', ';'),
    ('/root/.openclaw/media/inbound/leads_3a7108a69b28f189b2805f966b69c2d4286a52ca0e30cb1cdd64a1---2be09876-3154-4b15-941c-b8a9fb645ca4.csv', 'Email', 'Название', ';'),
    ('/root/.openclaw/media/inbound/1_рівень_кулінарного---da5b41ff-5b2f-4da8-a7c8-3b3635c097d2.csv', 'Email', 'Name', ';'),
]
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'
TAG = 'kul1-reengage'
SKIP_TAGS = {'kul1', 'kul1-reengage'}

with open('/root/.openclaw/workspace/kul1_reengage_v2_email.html') as f:
    BASE_HTML = f.read()

def load_log():
    try:
        with open(LOG_PATH) as f: return json.load(f)
    except: return {}

def save_log(log):
    tmp = LOG_PATH + '.tmp'
    with open(tmp, 'w') as f: json.dump(log, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LOG_PATH)

def first_name(name):
    if not name: return None
    parts = name.strip().split()
    if not parts: return None
    first = parts[0]
    if re.match(r'^[А-ЯІЇЄA-Z][а-яіїєa-z\']+$', first): return first
    return None

hard_skip = {'nadezhdarozhko@icloud.com','tatly.kolien@gmail.com',
             'anka1999.2010x@gmail.com','olena.zhukovych@gmail.com'}

log = load_log()
to_send, skipped = [], []
seen = set()

for path, ecol, ncol, delim in CSVS:
    with open(path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter=delim))
    for r in rows:
        email = r.get(ecol, '').strip()
        if not email or '@' not in email: continue
        el = email.lower()
        if el in hard_skip or el in seen: continue
        seen.add(el)
        if set(log.get(el, [])) & SKIP_TAGS:
            skipped.append(email)
            continue
        to_send.append((email, first_name(r.get(ncol, ''))))

print(f"Відправляти: {len(to_send)} | Пропущено (вже отримали): {len(skipped)}", flush=True)

if not to_send:
    print("Всім вже надіслано! Нічого робити.")
    exit(0)

sent, failed = 0, []
smtp = None
conn_count = 0

def reconnect():
    global smtp, conn_count
    try:
        if smtp: smtp.quit()
    except: pass
    smtp = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    smtp.starttls()
    smtp.login('iryna@culinary.com.ua', 'oymoyevavbucaccx')
    conn_count = 0

reconnect()

for email, name in to_send:
    if conn_count >= 10:
        reconnect()
        time.sleep(1)

    html = BASE_HTML
    if name: html = html.replace('Привіт!', f'{name}, привіт!')
    msg_obj = __import__('email.mime.multipart', fromlist=['MIMEMultipart']).MIMEMultipart('alternative')
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Ваші матеріали Кулінарного курсу оновлено — завантажте безкоштовно'
    msg['From'] = 'Ірина з Кулінарної Академії <iryna@culinary.com.ua>'
    msg['To'] = email
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    try:
        smtp.send_message(msg)
        el = email.lower()
        if el not in log: log[el] = []
        if TAG not in log[el]: log[el].append(TAG)
        save_log(log)
        sent += 1; conn_count += 1
        print(f"[{sent}] OK {email}", flush=True)
    except Exception as e:
        err = str(e)
        failed.append(email)
        print(f"FAIL {email}: {e}", flush=True)
        if any(x in err.lower() for x in ['connect', 'closed', 'timed out', '550']):
            try: reconnect()
            except: pass
    time.sleep(0.5)

try: smtp.quit()
except: pass

print(f"\nДОНЕ: sent={sent}, failed={len(failed)}")
if failed: print("FAILED:", failed)
