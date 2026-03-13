#!/usr/bin/env python3
"""
Mass email sender for March 25 campaign.
- 4 SMTP accounts in parallel (sequential per account)
- ~2000/day per account = ~8000/day total
- Logs every send to prevent duplicates on restart
- Checks all existing logs before sending
- Pause between emails to avoid rate limits
"""
import smtplib, json, time, sys, os, re, signal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Config
SUBJECT = "5 кулінарних прийомів, які ви точно не використовуєте (а дарма)"
FROM_NAME = "Ірина з Кулінарної Академії"
REPLY_TO = "support@culinary.com.ua"
DAILY_LIMIT_PER_ACCOUNT = 1900  # safe margin under 2000
DELAY_BETWEEN_EMAILS = 2.5  # seconds
RECONNECT_EVERY = 50  # reconnect SMTP every N emails
LOG_DIR = "."
EMAIL_RE = re.compile(r'[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}', re.I)

# Graceful shutdown
running = True
def handle_signal(sig, frame):
    global running
    print("\n⏸️  Зупинка... завершую поточний лист")
    running = False
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def load_all_sent():
    """Load ALL previously sent emails from ALL log files."""
    sent = set()
    for f in os.listdir(LOG_DIR):
        if f.startswith('sent_') and f.endswith('.txt'):
            with open(os.path.join(LOG_DIR, f)) as fh:
                for line in fh:
                    if line.startswith('OK|'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            sent.add(parts[1].strip().lower())
    return sent

def send_from_account(account_name, account_cfg, email_list_file, log_file):
    """Send emails from one account."""
    global running

    # Load email list
    with open(email_list_file) as f:
        all_emails = [l.strip().lower() for l in f if l.strip()]

    # Load already sent (from ALL logs, not just this account)
    already_sent = load_all_sent()

    # Filter out already sent
    to_send = [e for e in all_emails if e not in already_sent]
    
    print(f"\n📧 {account_name} ({account_cfg['email']})")
    print(f"   Список: {len(all_emails)} | Вже відправлено: {len(all_emails) - len(to_send)} | Залишилось: {len(to_send)}")

    if not to_send:
        print(f"   ✅ Все відправлено!")
        return 0

    # Cap at daily limit
    to_send = to_send[:DAILY_LIMIT_PER_ACCOUNT]
    print(f"   Сьогодні відправлю: {len(to_send)} (ліміт {DAILY_LIMIT_PER_ACCOUNT}/день)")

    # Load HTML
    with open('email-march-2025.html') as f:
        html = f.read()

    sent_count = 0
    err_count = 0
    smtp = None

    try:
        for i, email in enumerate(to_send):
            if not running:
                break

            # Connect/reconnect
            if smtp is None or i % RECONNECT_EVERY == 0:
                if smtp:
                    try: smtp.quit()
                    except: pass
                smtp = smtplib.SMTP(account_cfg['smtp'], account_cfg['port'], timeout=30)
                smtp.starttls()
                smtp.login(account_cfg['email'], account_cfg['appPassword'])

            # Build message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = SUBJECT
            msg['From'] = f"{FROM_NAME} <{account_cfg['email']}>"
            msg['To'] = email
            msg['Reply-To'] = REPLY_TO
            msg['List-Unsubscribe'] = f"<mailto:support@culinary.com.ua?subject=unsubscribe>"
            msg.attach(MIMEText(html, 'html', 'utf-8'))

            ts = datetime.utcnow().isoformat()
            try:
                smtp.sendmail(account_cfg['email'], email, msg.as_string())
                with open(log_file, 'a') as lf:
                    lf.write(f"OK|{email}|{ts}|{SUBJECT[:50]}\n")
                sent_count += 1
            except smtplib.SMTPDataError as e:
                with open(log_file, 'a') as lf:
                    lf.write(f"ERR|{email}|{ts}|{e}\n")
                err_count += 1
                if '550' in str(e) and 'limit' in str(e).lower():
                    print(f"   ⚠️ Денний ліміт! Зупиняюсь після {sent_count} листів")
                    break
            except Exception as e:
                with open(log_file, 'a') as lf:
                    lf.write(f"ERR|{email}|{ts}|{e}\n")
                err_count += 1
                # Reconnect on error
                smtp = None

            # Progress
            if (sent_count + err_count) % 100 == 0:
                print(f"   ... {sent_count} ok, {err_count} err ({i+1}/{len(to_send)})")

            time.sleep(DELAY_BETWEEN_EMAILS)

    finally:
        if smtp:
            try: smtp.quit()
            except: pass

    print(f"   📊 Результат: {sent_count} відправлено, {err_count} помилок")
    return sent_count


def main():
    # Determine phase from argument
    phase = sys.argv[1] if len(sys.argv) > 1 else 'new'
    
    with open('.smtp-config.json') as f:
        cfg = json.load(f)

    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    if phase == 'new':
        print(f"🚀 ФАЗА 1: Нові контакти ({today})")
        prefix = 'send_new'
    elif phase == 'repeat':
        print(f"🚀 ФАЗА 2: Повторні контакти ({today})")
        prefix = 'send_repeat'
    else:
        print(f"Usage: python3 mass_send.py [new|repeat]")
        return

    total = 0
    for account_name in ['support', 'iryna', 'gastro', 'olya']:
        if not running:
            break
        list_file = f"{prefix}_{account_name}.txt"
        log_file = f"sent_log_{today}_{account_name}.txt"
        
        if os.path.exists(list_file):
            count = send_from_account(
                account_name, 
                cfg['accounts'][account_name],
                list_file,
                log_file
            )
            total += count
        else:
            print(f"⚠️ Файл {list_file} не знайдено")

    print(f"\n{'='*50}")
    print(f"✅ ЗАГАЛОМ сьогодні: {total} листів відправлено")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
