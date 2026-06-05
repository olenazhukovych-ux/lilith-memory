#!/usr/bin/env python3
import json, smtplib, os, time, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

REMAINING_FILE = '/root/.openclaw/workspace/kon1_reengage_new2_remaining.json'
LOG_FILE = '/root/.openclaw/workspace/sent_emails_log.json'
HTML_FILE = '/root/.openclaw/workspace/kon1_reengage_email.html'
TAG = 'kon1-reengage'
SKIP_TAGS = {'kon1', 'kon1-reengage'}

ACCOUNTS = [
    ('iryna@culinary.com.ua', 'oymoyevavbucaccx'),
    ('support@culinary.com.ua', 'idaqfjgvzlycxjiz'),
]

FROM_NAME = 'Ірина з Кулінарної Академії'
SUBJECT = 'Ваша кондитерська книга — оновлена версія 💜'

with open(HTML_FILE, encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {}

def save_log(log):
    tmp = LOG_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LOG_FILE)

def load_remaining():
    if os.path.exists(REMAINING_FILE):
        with open(REMAINING_FILE) as f:
            return json.load(f)
    return []

def save_remaining(lst):
    tmp = REMAINING_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(lst, f, ensure_ascii=False)
    os.replace(tmp, REMAINING_FILE)

def connect_smtp(user, pwd):
    s = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    s.starttls()
    s.login(user, pwd)
    return s

def send_email(smtp, from_addr, to_email, name):
    html = HTML_TEMPLATE
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = f'{FROM_NAME} <{from_addr}>'
    msg['To'] = to_email
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    smtp.sendmail(from_addr, to_email, msg.as_string())

remaining = load_remaining()
log = load_log()

# Re-filter against log in case state changed
to_send = [r for r in remaining if not (set(log.get(r['email'], [])) & SKIP_TAGS)]
print(f"До відправки: {len(to_send)}")

sent = 0
errors = 0
acc_idx = 0

smtp = None
current_user = None

i = 0
while i < len(to_send):
    item = to_send[i]
    email = item['email']
    name = item.get('name', '')

    # Try to connect if not connected
    if smtp is None:
        while acc_idx < len(ACCOUNTS):
            user, pwd = ACCOUNTS[acc_idx]
            try:
                smtp = connect_smtp(user, pwd)
                current_user = user
                print(f"Підключено: {user}")
                break
            except Exception as e:
                print(f"Не вдалося підключитись до {user}: {e}")
                acc_idx += 1
        if smtp is None:
            print("Всі акаунти недоступні — зупиняюсь")
            break

    try:
        send_email(smtp, current_user, email, name)
        # Log immediately
        entry = log.get(email, [])
        if TAG not in entry:
            entry.append(TAG)
        log[email] = entry
        save_log(log)
        # Remove from remaining
        remaining = [r for r in remaining if r['email'] != email]
        save_remaining(remaining)
        sent += 1
        print(f"OK {email}")
        time.sleep(1.2)
        i += 1
    except smtplib.SMTPRecipientsRefused as e:
        print(f"ERR refused {email}: {e}")
        errors += 1
        i += 1
    except smtplib.SMTPServerDisconnected:
        print(f"З'єднання обірвалось, reconnect...")
        smtp = None
    except Exception as e:
        errmsg = str(e)
        if '451' in errmsg or '550' in errmsg or 'limit' in errmsg.lower() or 'quota' in errmsg.lower():
            print(f"ЛІМІТ {email}: {e}")
            smtp = None
            acc_idx += 1
            if acc_idx >= len(ACCOUNTS):
                print("Всі ліміти вичерпані — зупиняюсь")
                break
        elif 'connect' in errmsg.lower() or 'timed out' in errmsg.lower():
            print(f"ERR conn {email}: {e}")
            smtp = None
        else:
            print(f"ERR {email}: {e}")
            errors += 1
            i += 1

if smtp:
    try:
        smtp.quit()
    except:
        pass

print(f"\nГОТОВО: відправлено {sent}, помилок {errors}")
remaining_count = len(load_remaining())
print(f"Залишилось у файлі: {remaining_count}")
