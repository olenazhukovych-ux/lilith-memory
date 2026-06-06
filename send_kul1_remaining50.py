#!/usr/bin/env python3
import json, smtplib, time, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "support@culinary.com.ua"
SMTP_PASS = "idaqfjgvzlycxjiz"
FROM_ADDR = "Ірина з Кулінарної Академії <support@culinary.com.ua>"
SUBJECT = "🥦 Ваші матеріали з Кулінарного курсу — оновлена версія"
TAG = "kul1-reengage"

with open("kul1_charity_remaining.json") as f:
    recipients = json.load(f)

with open("kul1_reengage_v2_email.html") as f:
    html_body = f.read()

with open("sent_emails_log.json") as f:
    log = json.load(f)

# Filter already sent
to_send = [e for e in recipients if TAG not in log.get(e, [])]
print(f"Total in list: {len(recipients)}, already sent: {len(recipients)-len(to_send)}, to send: {len(to_send)}")

if not to_send:
    print("Nothing to send!")
    sys.exit(0)

sent_count = 0
errors = []

server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
server.ehlo()
server.starttls()
server.login(SMTP_USER, SMTP_PASS)

for i, email in enumerate(to_send):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = FROM_ADDR
        msg["To"] = email
        msg["Subject"] = SUBJECT
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        server.sendmail(SMTP_USER, email, msg.as_string())
        
        # Update log
        if email not in log:
            log[email] = []
        log[email].append(TAG)
        
        sent_count += 1
        print(f"[{i+1}/{len(to_send)}] ✓ {email}")
        
        # Rate limit: pause every 10 emails
        if sent_count % 10 == 0 and i < len(to_send) - 1:
            with open("sent_emails_log.json", "w") as f:
                json.dump(log, f, indent=2, ensure_ascii=False)
            time.sleep(3)
        else:
            time.sleep(1)
            
    except Exception as e:
        errors.append((email, str(e)))
        print(f"[{i+1}/{len(to_send)}] ✗ {email}: {e}")

server.quit()

# Save final log
with open("sent_emails_log.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)

print(f"\n=== DONE ===")
print(f"Sent: {sent_count}/{len(to_send)}")
if errors:
    print(f"Errors: {len(errors)}")
    for em, err in errors:
        print(f"  - {em}: {err}")
