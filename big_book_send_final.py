import smtplib, json, os, time, pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'
SMTP_USER = 'support@culinary.com.ua'
SMTP_PASS = 'idaqfjgvzlycxjiz'
BATCH_SIZE = 50

IMG_KON2 = 'https://lh3.googleusercontent.com/d/1ygoTXxRCgutWBPSGRtwzy18Mu9sA4vgV=w600'
IMG_KUL3 = 'https://lh3.googleusercontent.com/d/1n_x6Yf0mN-annrobRxmJys_d8JmI4SjY=w600'
IMG_KUL2 = 'https://lh3.googleusercontent.com/d/1i54RnFnTiPrW4lhfLFDY7pCjiaO4nebT=w600'
URL_KUL1 = 'https://drive.google.com/file/d/1vWrBS9WcJ-4WiX-OKxxQPfnjawPPa3gb/view'
URL_KON1 = 'https://drive.google.com/file/d/13UyI_6IYWocSZ-7V4c_ce8XwCoN6Xvdn/view'
SITE_URL  = 'https://culinaryacademy.com.ua/books'
EBOOK_NOTE = '<p style="font-size:12px;color:#aaa;margin:8px 0 20px;text-align:center;">Наразі доступні в електронному форматі — паперове видання вже готується</p>'
HARD_SKIP = {'nadezhdarozhko@icloud.com','tatly.kolien@gmail.com','anka1999.2010x@gmail.com',
             'olena.zhukovych@gmail.com','oleksii.mychka@gmail.com','info@nai.restaurant'}

def load_log():
    with open(LOG_PATH) as f: return json.load(f)
def save_log(log):
    tmp = LOG_PATH+'.tmp'
    with open(tmp,'w') as f: json.dump(log,f,ensure_ascii=False)
    os.replace(tmp,LOG_PATH)

def upsell_block(covers):
    items=''.join(f'<td align="center" style="padding:0 10px;vertical-align:top;"><img src="{i}" width="150" style="border-radius:6px;display:block;margin:0 auto 10px;"><p style="margin:0;font-size:13px;font-weight:bold;color:#1A232F;">{t}</p><p style="margin:4px 0 0;font-size:12px;color:#888;">{s}</p></td>' for i,t,s in covers)
    return f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0 0;"><tr>{items}</tr></table>'

def kul_html():
    u=upsell_block([(IMG_KUL2,'Кухні світу','8 кухонь · 40 рецептів'),(IMG_KUL3,'Крафтяр','6 ремесел · від сиру до спецій')])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;background:#f5f2ed;font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f2ed;padding:30px 0;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fff;border-radius:8px;overflow:hidden;"><tr><td style="background:#1A232F;padding:32px 40px;text-align:center;"><p style="margin:0;color:#fff;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Кулінарна Академія</p><h1 style="margin:12px 0 0;color:#fff;font-size:22px;font-weight:normal;">Ваша Велика кулінарна книга стала ще більшою</h1></td></tr><tr><td style="padding:36px 40px;"><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 16px;">Ви купували у нас <strong>Велику кулінарну книгу</strong> — і ми хочемо поділитися оновленою електронною версією безкоштовно.</p><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 16px;">З моменту виходу ми суттєво розширили збірник: додали нові рецепти, поглибили техніки та доповнили розділи, які студенти просили найчастіше. Сотні сторінок практики, структурованих за рівнями — від базових бульйонів і соусів до м'яса, риби та складних технік.</p><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 28px;">Ця версія — найповніша. Завантажуйте та готуйте!</p><table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;"><tr><td align="center"><a href="{URL_KUL1}" style="background:#5C6142;color:#fff;text-decoration:none;padding:16px 40px;border-radius:6px;font-size:16px;display:inline-block;">Завантажити оновлену книгу</a></td></tr></table><hr style="border:none;border-top:1px solid #eee;margin:28px 0;"><p style="font-size:14px;color:#5C6142;font-weight:bold;margin:0 0 8px;letter-spacing:1px;text-transform:uppercase;">До речі — є нові частини серії</p><p style="font-size:14px;line-height:1.7;color:#555;margin:0 0 4px;">Поки ви готували за першою книгою, ми встигли написати ще дві — про кухні 8 країн світу та крафтові ремесла: сироваріння, хліб на заквасці, ферментацію, м'ясні вироби. Якщо цікаво — подивіться:</p>{EBOOK_NOTE}{u}<table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0 0;"><tr><td align="center"><a href="{SITE_URL}" style="border:2px solid #5C6142;color:#5C6142;text-decoration:none;padding:12px 32px;border-radius:6px;font-size:14px;display:inline-block;">Переглянути всі книги</a></td></tr></table><hr style="border:none;border-top:1px solid #eee;margin:28px 0;"><p style="font-size:12px;color:#aaa;margin:0;">З теплом,<br>Команда Кулінарної Академії · <a href="https://culinaryacademy.com.ua" style="color:#5C6142;">culinaryacademy.com.ua</a></p></td></tr></table></td></tr></table></body></html>"""

def kon_html():
    u=upsell_block([(IMG_KON2,'Велика кондитерська. Ч.2','Макарони, круасани, торти на замовлення')])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;background:#f0ecf5;font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ecf5;padding:30px 0;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fff;border-radius:8px;overflow:hidden;"><tr><td style="background:#1f2630;padding:32px 40px;text-align:center;"><p style="margin:0;color:#fff;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Кулінарна Академія</p><h1 style="margin:12px 0 0;color:#fff;font-size:22px;font-weight:normal;">Ваша Велика кондитерська книга стала ще більшою</h1></td></tr><tr><td style="padding:36px 40px;"><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 16px;">Ви купували у нас <strong>Велику кондитерську книгу</strong> — і ми хочемо поділитися оновленою електронною версією безкоштовно.</p><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 16px;">З моменту виходу ми суттєво розширили збірник: додали нові рецепти, поглибили техніки та доповнили розділи, які студенти просили найчастіше. Еклери, тістечка, чизкейки, торти — структуровано, покроково, з усіма нюансами кондитерської майстерності.</p><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 28px;">Ця версія — найповніша. Завантажуйте та творіть!</p><table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;"><tr><td align="center"><a href="{URL_KON1}" style="background:#b8afc6;color:#1f2630;text-decoration:none;padding:16px 40px;border-radius:6px;font-size:16px;display:inline-block;">Завантажити оновлену книгу</a></td></tr></table><hr style="border:none;border-top:1px solid #f0ecf5;margin:28px 0;"><p style="font-size:14px;color:#8c7fa0;font-weight:bold;margin:0 0 8px;letter-spacing:1px;text-transform:uppercase;">До речі — з'явилось продовження</p><p style="font-size:14px;line-height:1.7;color:#555;margin:0 0 4px;">Поки ви готували за першою книгою, ми написали другу — поглиблений курс із макаронами, круасанами, веганськими десертами та тортами на замовлення:</p>{EBOOK_NOTE}{u}<table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0 0;"><tr><td align="center"><a href="{SITE_URL}" style="border:2px solid #b8afc6;color:#8c7fa0;text-decoration:none;padding:12px 32px;border-radius:6px;font-size:14px;display:inline-block;">Переглянути всі книги</a></td></tr></table><hr style="border:none;border-top:1px solid #f0ecf5;margin:28px 0;"><p style="font-size:12px;color:#aaa;margin:0;">З теплом,<br>Команда Кулінарної Академії · <a href="https://culinaryacademy.com.ua" style="color:#8c7fa0;">culinaryacademy.com.ua</a></p></td></tr></table></td></tr></table></body></html>"""

def both_html():
    u=upsell_block([(IMG_KUL2,'Кухні світу','8 кухонь · 40 рецептів'),(IMG_KUL3,'Крафтяр','6 ремесел · від сиру до спецій'),(IMG_KON2,'Велика кондитерська. Ч.2','Макарони, круасани, торти')])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;background:#f5f2ed;font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f2ed;padding:30px 0;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fff;border-radius:8px;overflow:hidden;"><tr><td style="background:#1A232F;padding:32px 40px;text-align:center;"><p style="margin:0;color:#fff;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Кулінарна Академія</p><h1 style="margin:12px 0 0;color:#fff;font-size:22px;font-weight:normal;">Ваші книги стали ще більшими</h1></td></tr><tr><td style="padding:36px 40px;"><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 16px;">Ви купували у нас <strong>Велику кулінарну та Велику кондитерську книги</strong> — і ми хочемо поділитися оновленими електронними версіями безкоштовно.</p><p style="font-size:15px;line-height:1.8;color:#333;margin:0 0 24px;">Обидві книги суттєво виросли: нові рецепти, поглиблені техніки, доповнені розділи — те, що студенти просили найчастіше. Найповніші версії вже чекають на вас:</p><p style="font-size:13px;color:#888;margin:0 0 6px;">Оновлена Велика кулінарна книга:</p><table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 14px;"><tr><td align="center"><a href="{URL_KUL1}" style="background:#5C6142;color:#fff;text-decoration:none;padding:14px 32px;border-radius:6px;font-size:15px;display:inline-block;">Завантажити кулінарну</a></td></tr></table><p style="font-size:13px;color:#888;margin:0 0 6px;">Оновлена Велика кондитерська книга:</p><table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;"><tr><td align="center"><a href="{URL_KON1}" style="background:#b8afc6;color:#1f2630;text-decoration:none;padding:14px 32px;border-radius:6px;font-size:15px;display:inline-block;">Завантажити кондитерську</a></td></tr></table><hr style="border:none;border-top:1px solid #eee;margin:28px 0;"><p style="font-size:14px;color:#5C6142;font-weight:bold;margin:0 0 8px;letter-spacing:1px;text-transform:uppercase;">А ще — з'явились нові частини серії</p><p style="font-size:14px;line-height:1.7;color:#555;margin:0 0 4px;">Три нові книги для тих, хто хоче йти далі: кухні світу, крафтові ремесла та поглиблена кондитерка:</p>{EBOOK_NOTE}{u}<table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0 0;"><tr><td align="center"><a href="{SITE_URL}" style="border:2px solid #5C6142;color:#5C6142;text-decoration:none;padding:12px 32px;border-radius:6px;font-size:14px;display:inline-block;">Переглянути всі книги</a></td></tr></table><hr style="border:none;border-top:1px solid #eee;margin:28px 0;"><p style="font-size:12px;color:#aaa;margin:0;">З теплом,<br>Команда Кулінарної Академії · <a href="https://culinaryacademy.com.ua" style="color:#5C6142;">culinaryacademy.com.ua</a></p></td></tr></table></td></tr></table></body></html>"""

TEMPLATES = {
    'kul':  ('Ваша Велика кулінарна книга стала ще більшою',    kul_html(),  ['big-kul-upsell']),
    'kon':  ('Ваша Велика кондитерська книга стала ще більшою', kon_html(),  ['big-kon-upsell']),
    'both': ('Ваші книги стали ще більшими',                    both_html(), ['big-kul-upsell','big-kon-upsell']),
}

with open('/root/.openclaw/workspace/big_book_segments.pkl','rb') as f:
    segments = pickle.load(f)

queue = []
for seg_name, emails in [('both',segments['both']),('kul',segments['kul']),('kon',segments['kon'])]:
    subj, html, tags = TEMPLATES[seg_name]
    log = load_log()
    for email in emails:
        email = email.lower().strip()
        if email in HARD_SKIP: continue
        if set(log.get(email,[])) & set(tags): continue
        queue.append((email, subj, html, tags))

print(f"Черга: {len(queue)} листів")

sent = errors = 0
smtp = None
batch_count = 0

for i, (email, subj, html, tags) in enumerate(queue):
    if batch_count == 0 or batch_count >= BATCH_SIZE:
        if smtp:
            try: smtp.quit()
            except: pass
        smtp = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        batch_count = 0
        print(f"  [SMTP reconnect #{i}]")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['From'] = f'Ірина з Кулінарної Академії <{SMTP_USER}>'
    msg['To'] = email
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    try:
        smtp.sendmail(SMTP_USER, [email], msg.as_string())
        log = load_log()
        if email not in log: log[email] = []
        for t in tags:
            if t not in log[email]: log[email].append(t)
        save_log(log)
        sent += 1
        batch_count += 1
        if sent % 25 == 0:
            print(f"  [{sent}/{len(queue)}] відправлено")
        time.sleep(1.0)
    except smtplib.SMTPServerDisconnected:
        batch_count = BATCH_SIZE
        try: smtp.quit()
        except: pass
        smtp = None
        errors += 1
        print(f"  [disconnect] {email}")
    except Exception as e:
        print(f"  ERROR {email}: {e}")
        errors += 1
        batch_count += 1

if smtp:
    try: smtp.quit()
    except: pass

print(f"DONE: sent={sent} errors={errors}")
