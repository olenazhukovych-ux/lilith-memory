import smtplib, time, json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open('/root/.openclaw/workspace/fermentation_upsell_email.html') as f:
    HTML = f.read()

with open('/tmp/fermentation_emails.txt') as f:
    emails = [e.strip() for e in f.readlines() if e.strip()]

# Skip "не контактувати" list
skip = {'nadezhdarozhko@icloud.com', 'tatly.kolien@gmail.com', 'anka1999.2010x@gmail.com'}
emails = [e for e in emails if e.lower() not in skip]

print(f"Відправляти: {len(emails)}", flush=True)

sent, failed = 0, []

for i in range(0, len(emails), 10):
    batch = emails[i:i+10]
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as s:
            s.starttls()
            s.login('support@culinary.com.ua', 'idaqfjgvzlycxjiz')
            for email in batch:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Ваш збірник з ферментації — оновлена версія всередині 🫙'
                msg['From'] = 'Команда Кулінарної Академії <support@culinary.com.ua>'
                msg['To'] = email
                msg.attach(MIMEText(HTML, 'html', 'utf-8'))
                try:
                    s.send_message(msg)
                    sent += 1
                    print(f"[{sent}] OK {email}", flush=True)
                except Exception as e:
                    failed.append(email)
                    print(f"FAIL {email}: {e}", flush=True)
                time.sleep(0.5)
    except Exception as e:
        print(f"BATCH ERROR batch {i//10+1}: {e}", flush=True)
        failed.extend(batch)

print(f"\nДОНЕ: sent={sent}, failed={len(failed)}")
if failed:
    print("FAILED:", failed)
