#!/usr/bin/env python3
"""Send from 5th account (recipes) in parallel with main script."""
import smtplib, json, time, os, re, signal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SUBJECT = "5 кулінарних прийомів, які ви точно не використовуєте (а дарма)"
FROM_NAME = "Ірина з Кулінарної Академії"
REPLY_TO = "support@culinary.com.ua"
DAILY_LIMIT = 1900
DELAY = 2.5
RECONNECT_EVERY = 50
EMAIL_RE = re.compile(r'[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}', re.I)

running = True
def handle_signal(sig, frame):
    global running
    print("\n⏸️  Зупинка...")
    running = False
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def load_all_sent():
    sent = set()
    for f in os.listdir('.'):
        if f.startswith('sent_') and f.endswith('.txt'):
            with open(f) as fh:
                for line in fh:
                    if line.startswith('OK|'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            sent.add(parts[1].strip().lower())
    return sent

with open('.smtp-config.json') as f:
    cfg = json.load(f)['accounts']['recipes']

with open('email-march-2025.html') as f:
    html = f.read()

with open('send_new_recipes.txt') as f:
    all_emails = [l.strip().lower() for l in f if l.strip()]

already_sent = load_all_sent()
to_send = [e for e in all_emails if e not in already_sent][:DAILY_LIMIT]

today = datetime.utcnow().strftime('%Y-%m-%d')
log_file = f"sent_log_{today}_recipes.txt"

print(f"📧 recipes ({cfg['email']})")
print(f"   Залишилось: {len(to_send)} | Ліміт: {DAILY_LIMIT}")

sent_count = 0
smtp = None

try:
    for i, email in enumerate(to_send):
        if not running:
            break
        if smtp is None or i % RECONNECT_EVERY == 0:
            if smtp:
                try: smtp.quit()
                except: pass
            smtp = smtplib.SMTP(cfg['smtp'], cfg['port'], timeout=30)
            smtp.starttls()
            smtp.login(cfg['email'], cfg['appPassword'])

        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = f"{FROM_NAME} <{cfg['email']}>"
        msg['To'] = email
        msg['Reply-To'] = REPLY_TO
        msg['List-Unsubscribe'] = "<mailto:support@culinary.com.ua?subject=unsubscribe>"
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        ts = datetime.utcnow().isoformat()
        try:
            smtp.sendmail(cfg['email'], email, msg.as_string())
            with open(log_file, 'a') as lf:
                lf.write(f"OK|{email}|{ts}|{SUBJECT[:50]}\n")
            sent_count += 1
        except smtplib.SMTPDataError as e:
            with open(log_file, 'a') as lf:
                lf.write(f"ERR|{email}|{ts}|{e}\n")
            if '550' in str(e) and 'limit' in str(e).lower():
                print(f"   ⚠️ Денний ліміт після {sent_count}")
                break
        except Exception as e:
            with open(log_file, 'a') as lf:
                lf.write(f"ERR|{email}|{ts}|{e}\n")
            smtp = None

        if sent_count % 100 == 0 and sent_count > 0:
            print(f"   ... {sent_count} ok ({i+1}/{len(to_send)})")
        time.sleep(DELAY)
finally:
    if smtp:
        try: smtp.quit()
        except: pass

print(f"📊 recipes: {sent_count} відправлено")
