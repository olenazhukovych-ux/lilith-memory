import csv, json, re, smtplib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CSV_PATH = '/root/.openclaw/media/inbound/6a21828c278a5---07eeae6c-1b53-49ac-9360-53747410c095.csv'
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'

with open('/root/.openclaw/workspace/kul1_email.html') as f:
    BASE_HTML = f.read()

def extract_first_name(name):
    name = name.strip()
    parts = name.split()
    if not parts: return "Шефе"
    first = parts[0]
    if re.match(r'^[А-ЯІЇЄ][а-яіїє\']+$', first) or re.match(r'^[A-Z][a-z]+$', first):
        return first
    return "Шефе"

def make_html(first_name):
    greeting = f"{first_name}, привіт!" if first_name != "Шефе" else "Шефе, привіт!"
    return BASE_HTML.replace("Шефе, привіт!", greeting)

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

with open(LOG_PATH) as f:
    log = json.load(f)

to_send = [(r['Email'].strip(), extract_first_name(r['Name'])) for r in rows
           if 'kul1' not in log.get(r['Email'].strip().lower(), [])]

print(f"Відправляти: {len(to_send)}", flush=True)

sent = 0
failed = []

for i in range(0, len(to_send), 10):
    batch = to_send[i:i+10]
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as s:
            s.starttls()
            s.login('support@culinary.com.ua', 'idaqfjgvzlycxjiz')
            for email, name in batch:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = '🔪 Твої матеріали Кулінарного курсу 1 рівня — оновлено і розширено!'
                msg['From'] = 'Команда Кулінарної Академії <support@culinary.com.ua>'
                msg['To'] = email
                msg.attach(MIMEText(make_html(name), 'html', 'utf-8'))
                try:
                    s.send_message(msg)
                    sent += 1
                    key = email.lower()
                    if key not in log: log[key] = []
                    if 'kul1' not in log[key]: log[key].append('kul1')
                    print(f"[{sent}] OK {email}", flush=True)
                except Exception as e:
                    failed.append(email)
                    print(f"FAIL {email}: {e}", flush=True)
                time.sleep(0.5)
    except Exception as e:
        print(f"BATCH ERROR: {e}", flush=True)
        failed.extend([em for em, _ in batch])

with open(LOG_PATH, 'w') as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print(f"\nДОНЕ: sent={sent}, failed={len(failed)}")
if failed:
    print("FAILED:", failed)
