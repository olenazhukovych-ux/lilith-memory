import smtplib, csv, json, os, time, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'iryna@culinary.com.ua'
SMTP_PASS = 'oymoyevavbucaccx'
FROM = 'Ірина з Кулінарної Академії <iryna@culinary.com.ua>'

CSV_FILE = '/root/.openclaw/media/inbound/leads_60166f85e565352230de0fa9369d26aff246cba30e500144356bc3---c9ee0365-9f61-43f7-8ad6-4dc283cd7418.csv'
LOG_FILE = '/root/.openclaw/workspace/sent_emails_log.json'
HTML_FILE = '/root/.openclaw/workspace/kul1_reengage_v2_email.html'
TAG = 'kul1-reengage'

HARD_SKIP = {
    'nadezhdarozhko@icloud.com', 'tatly.kolien@gmail.com',
    'anka1999.2010x@gmail.com', 'olena.zhukovych@gmail.com',
    'oleksii.mychka@gmail.com'
}
SKIP_TAGS = {'kul1', 'kul1-reengage'}

with open(LOG_FILE) as f:
    log = json.load(f)

with open(HTML_FILE, encoding='utf-8') as f:
    html = f.read()

# Extract unique culinary emails
with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

seen = set()
to_send = []
for r in rows:
    items = r.get('Товары в заказе', '')
    email = r.get('Email', '').strip().lower()
    if 'кулінарний' not in items.lower() or not email or email in seen:
        continue
    seen.add(email)
    if email in HARD_SKIP:
        continue
    tags = set(log.get(email, []))
    if tags & SKIP_TAGS:
        continue
    to_send.append(email)

print(f"До відправки: {len(to_send)}")

def save_log():
    tmp = LOG_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LOG_FILE)

sent = 0
errors = 0

try:
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.starttls()
    smtp.login(SMTP_USER, SMTP_PASS)

    for email in to_send:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '🥦 Ваші матеріали з Кулінарного курсу — оновлена версія'
            msg['From'] = FROM
            msg['To'] = email
            msg.attach(MIMEText(html, 'html', 'utf-8'))
            smtp.sendmail(SMTP_USER, [email], msg.as_string())

            if email not in log:
                log[email] = []
            if TAG not in log[email]:
                log[email].append(TAG)
            save_log()

            sent += 1
            if sent % 50 == 0:
                print(f"[{sent}/{len(to_send)}] відправлено...")
            time.sleep(1.2)

        except smtplib.SMTPServerDisconnected:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.sendmail(SMTP_USER, [email], msg.as_string())
            if email not in log:
                log[email] = []
            if TAG not in log[email]:
                log[email].append(TAG)
            save_log()
            sent += 1
            time.sleep(1.2)

        except Exception as e:
            print(f"ERROR {email}: {e}")
            errors += 1

    smtp.quit()
except Exception as e:
    print(f"FATAL: {e}")
    sys.exit(1)

print(f"\nГОТОВО: відправлено {sent}, помилок {errors}")
