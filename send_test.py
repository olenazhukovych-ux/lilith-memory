#!/usr/bin/env python3
"""Send test email from all 4 accounts to Olena's test address."""
import smtplib, json, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TO = "olena.zhukovych@gmail.com"
SUBJECT = "5 кулінарних прийомів, які ви точно не використовуєте (а дарма)"
FROM_NAME = "Ірина з Кулінарної Академії"

with open('.smtp-config.json') as f:
    cfg = json.load(f)

with open('email-march-2025.html') as f:
    html = f.read()

for name, acc in cfg['accounts'].items():
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = f"{FROM_NAME} <{acc['email']}>"
        msg['To'] = TO
        msg['Reply-To'] = "support@culinary.com.ua"
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        s = smtplib.SMTP(acc['smtp'], acc['port'], timeout=15)
        s.starttls()
        s.login(acc['email'], acc['appPassword'])
        s.sendmail(acc['email'], TO, msg.as_string())
        s.quit()
        print(f"✅ {name} ({acc['email']}) → відправлено")
    except Exception as e:
        print(f"❌ {name} ({acc['email']}) → помилка: {e}")
