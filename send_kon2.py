import csv, json, re, smtplib, time, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CSV_PATH = '/root/.openclaw/media/inbound/6a217c22e4b72---8b500a55-b14f-4a74-9126-0de0062dfc73.csv'
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'

H1 = "#1f2630"
H2 = "#8c7fa0"
BG = "#f7f4fb"

def extract_first_name(name):
    name = name.strip()
    parts = name.split()
    if not parts: return "Шефе"
    first = parts[0]
    if re.match(r'^[А-ЯІЇЄ][а-яіїє\']+$', first) or re.match(r'^[A-Z][a-z]+$', first):
        return first
    return "Шефе"

def mod(title, color, r_list, t_list, d_list):
    r = " &nbsp;·&nbsp; ".join(r_list) if r_list else ""
    t = " &nbsp;·&nbsp; ".join(t_list) if t_list else ""
    d = " &nbsp;·&nbsp; ".join(d_list) if d_list else ""
    rows = f'<p style="margin:0 0 5px;font-size:13px;color:#2a2a2a;line-height:1.9;">{r}</p>' if r else ""
    rows += f'<p style="margin:0 0 4px;font-size:12px;color:#555;line-height:1.8;">{t}</p>' if t else ""
    rows += f'<p style="margin:0;font-size:12px;color:#aaa;line-height:1.8;">{d}</p>' if d else ""
    return f"""<tr><td style="padding:0 40px 8px;"><table width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px;overflow:hidden;"><tr><td style="background:{color};padding:10px 16px;"><p style="margin:0;font-size:13px;color:#ffffff;font-weight:bold;">{title}</p></td></tr><tr><td style="background:{BG};padding:12px 16px;">{rows}</td></tr></table></td></tr>"""

toc = \
mod("Модуль 1 — Макарони", H1,
    ["07 Французька меренга","08 Італійська меренга","09 Фісташковий ганаш","10 Шоколадно-малиновий ганаш","11 Збірка макарон","12 Веганські макарони"],
    ["01 Вступ та словник","02 Інгредієнти","03 Обладнання та духовка","04 Техніки меренги","05 Від макаронажу до макарона","06 Помилки та FAQ"],
    ["13 Начинки — принципи","14 Бонусні рецепти начинок","15 Чек-лист та шпаргалки"]) + \
mod("Модуль 2 — Круасани", H2,
    ["05 Круасан класичний","06 Даніш","07 Пліє","08 Додаткові рецепти та начинки","09 Кольорове тісто"],
    ["01 Вступ та словник","02 Інгредієнти","03 Обладнання","04 Заміс, ферментація і ламінування"],
    ["10 Помилки та FAQ","11 Чек-лист та зберігання"]) + \
mod("Модуль 3 — Веганські десерти", H2,
    ["05 Карамельний тарт","06 Веганський Наполеон","07 Веганський чізкейк","08 Веганський кекс","09 Веганське морозиво","10 Веганський тірамісу","11 Веганські брауні","12 Веганські макарони","13 Шоколадний мус з авокадо"],
    ["01 Вступ та філософія","02 Основи та заміни","03 Веганські технології","04 Зберігання, продукти, бренди"],
    ["14 Словник кондитера"]) + \
mod("Модуль 4 — Безглютенові десерти", H2,
    ["Безглютеновий медівник","Безглютеновий бісквіт Женуаз","Безглютенові млинці","Безглютенові шу","Безглютеновий шоколадний бісквіт","Мигдальне печиво на аквафабі","Безглютеновий ягідний пиріг","Кокосовий торт на аквафабі","Безглютеновий лимонний тарт","Безглютенові брауні з горіхами","Безглютенові медові мафіни","Безглютенове шоколадне печиво","Безглютенові панкейки з бананом","Безглютеновий гарбузовий пиріг","Безглютенові шоколадні трюфелі"],
    ["17 Теорія безглютенової випічки","18 Техніка випікання та зберігання","19 Креми та прошарки"],
    ["16 Словник кондитера"]) + \
mod("Модуль 5 — Авторські цукерки та шоколад", H2,
    ["06 Цукерка з лаймом","07 Дубайський шоколад","08 Трюфель із бренді","09 Мармелад із маракуї","10 Моті","11 Вишня в коньяку","12 Морська карамель","13 Лате-Макіато","14 Малина Розе","15 After Eight"],
    ["01 Вступ та словник","02 Типи цукерок та начинки","03 Темперування шоколаду","04 Фарбування форм","05 Зберігання, бренди та довідник"],
    []) + \
mod("Модуль 6 — Торти на замовлення", H2,
    ["09 Снікерс","10 Чорниця-лимон","11 Класичний Ванільний","12 Шоколадний торт з ганашем","13 Медовик","14 Червоний оксамит","15 Фісташка-малина","16 Тарт Татен","17 Штрудель","18 Тірамісу"],
    ["01 Словник кондитера","02 Бісквіти та креми","03 Зберігання і транспортування","04 Бізнес: ціна та клієнти"],
    ["05 Базові бісквіти","06 Базові креми","07 Базові фруктові прошарки","08 Базові хрусткі прошарки","19 Рекомендована література"])

def make_html(first_name):
    greeting = f"{first_name}, привіт!" if first_name != "Шефе" else "Шефе, привіт!"
    return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f0ecf5;font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ecf5;padding:40px 0;"><tr><td align="center"><table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;overflow:hidden;">
  <tr><td style="background:{H1};padding:32px 40px;text-align:center;"><p style="margin:0 0 6px;color:#b8afc6;font-size:11px;letter-spacing:3px;text-transform:uppercase;">Кулінарна Академія</p><h1 style="margin:0 0 8px;color:#ffffff;font-size:24px;font-weight:normal;">Ти завершив(ла) другий рівень 🍰</h1><p style="margin:0;color:rgba(255,255,255,0.7);font-size:15px;">це вже справжній рівень майстра</p></td></tr>
  <tr><td style="padding:36px 40px 24px;"><p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">{greeting}</p><p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">Вітаємо з завершенням Кондитерського курсу 2 рівня! Від макаронів і круасанів до тортів на замовлення — ти пройшов(ла) шлях, який відкриває справжні можливості.</p><p style="margin:0;font-size:16px;color:#333;line-height:1.7;">Дякуємо, що довірив(ла) нам цей шлях 💛</p></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};border-left:3px solid #b8afc6;border-radius:0 8px 8px 0;padding:20px 22px;"><tr><td><p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Твої матеріали курсу</p><p style="margin:0 0 8px;font-size:14px;color:#444;line-height:1.7;">Протягом курсу ми фіксували всі запитання студентів і оновили матеріали у зручному форматі — з підказками, лайфхаками та відповідями на найпоширеніші питання.</p><p style="margin:0;font-size:14px;color:#444;line-height:1.7;">📚 <strong>Усі текстові матеріали — твої назавжди</strong><br>📱 <strong>Доступ до відеоуроків</strong> — до <strong>березня 2027 року</strong></p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{H1};border-radius:8px;padding:22px 24px;"><tr><td><p style="margin:0 0 4px;font-size:12px;color:#b8afc6;letter-spacing:1px;text-transform:uppercase;">Головна книга курсу</p><p style="margin:0 0 14px;font-size:17px;color:#ffffff;font-weight:bold;">Велика кондитерська книга — Частина 2</p><a href="https://drive.google.com/file/d/1HJ6l6kbd9AsJ1yB6ny8MjIKcPXqQICGL/view" style="display:inline-block;background:#b8afc6;color:#1f2630;text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;font-weight:bold;">Завантажити книгу →</a></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf5f4;border-radius:8px;padding:16px 20px;"><tr><td><p style="margin:0;font-size:14px;color:#555;line-height:1.8;">💡 <strong>Як користуватись книгою:</strong><br>— Усі пункти у змісті <strong>клікабельні</strong> — натисни на назву і одразу перейдеш на потрібну сторінку.<br>— Натисни <strong>Ctrl+F</strong> (або Cmd+F на Mac) і введи будь-яке слово — наприклад «ламінування», «темперування» або «аквафаба» — книга знайде все миттєво.</p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 12px;"><p style="margin:0 0 4px;font-size:17px;color:#2a2a2a;font-weight:bold;">Що є в книзі</p><p style="margin:0;font-size:13px;color:#999;">6 модулів &nbsp;·&nbsp; 60+ рецептів &nbsp;·&nbsp; теорія, техніки і словники кондитера</p></td></tr>
  {toc}
  <tr><td style="padding:24px 40px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf5f4;border-radius:8px;padding:20px 22px;"><tr><td><p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Що далі? ✨</p><p style="margin:0 0 12px;font-size:14px;color:#444;line-height:1.7;">Наступні рівні кондитерських курсів вже у розробці — поки що по секрету 🤫</p><p style="margin:0 0 12px;font-size:14px;color:#444;line-height:1.7;">А поки чекаєш — зазирни на <strong>кулінарні курси</strong>. Техніки, кухні світу, ножі, м'ясо, хліб, соуси — теж цікаво, обіцяємо 🙂</p><a href="https://culinaryacademy.com.ua/basic" style="display:inline-block;background:{H1};color:#ffffff;text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;">Переглянути кулінарні курси →</a></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><p style="margin:0 0 10px;font-size:15px;color:#333;line-height:1.7;">І маленьке прохання — якщо навчання було для тебе цінним, залиш відгук на Google. Це правда допомагає нам і дозволяє знаходити нових студентів 🙏</p><a href="https://g.page/r/CVTTiYeu4opqEAE/review" style="display:inline-block;border:1px solid #b8afc6;color:#8c7fa0;text-decoration:none;padding:10px 22px;border-radius:5px;font-size:14px;">Залишити відгук на Google →</a><p style="margin:14px 0 0;font-size:14px;color:#777;line-height:1.6;">Є думки, що ми можемо покращити? Просто відповідай на цей лист — ми читаємо кожне слово.</p></td></tr>
  <tr><td style="padding:0 40px 36px;"><p style="margin:0 0 4px;font-size:15px;color:#333;">Успіхів тобі на кухні — ти вже майстер! 💛</p><p style="margin:12px 0 0;font-size:14px;color:#666;">Команда Кулінарної Академії</p></td></tr>
  <tr><td style="background:#f0ecf5;padding:18px 40px;text-align:center;"><p style="margin:0;font-size:12px;color:#999;"><a href="https://culinaryacademy.com.ua" style="color:#8c7fa0;text-decoration:none;">culinaryacademy.com.ua</a> &nbsp;·&nbsp; <a href="https://www.instagram.com/culinary_academy_ua/" style="color:#8c7fa0;text-decoration:none;">Instagram</a> &nbsp;·&nbsp; <a href="https://t.me/uca_service" style="color:#8c7fa0;text-decoration:none;">@uca_service</a></p></td></tr>
</table></td></tr></table></body></html>"""

# Load CSV
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Load log
with open(LOG_PATH) as f:
    log = json.load(f)

# Build send list (skip already sent kon2)
to_send = []
for r in rows:
    email = r['Email'].strip()
    key = email.lower()
    if 'kon2' not in log.get(key, []):
        to_send.append((email, extract_first_name(r['Name'])))

print(f"Відправляти: {len(to_send)}", flush=True)

sent = 0
failed = []
batch_size = 10

for i in range(0, len(to_send), batch_size):
    batch = to_send[i:i+batch_size]
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as s:
            s.starttls()
            s.login('support@culinary.com.ua', 'idaqfjgvzlycxjiz')
            for email, name in batch:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = '🍰 Твої матеріали Кондитерського курсу 2 рівня — лови і зберігай!'
                msg['From'] = 'Команда Кулінарної Академії <support@culinary.com.ua>'
                msg['To'] = email
                msg.attach(MIMEText(make_html(name), 'html', 'utf-8'))
                try:
                    s.send_message(msg)
                    sent += 1
                    # Update log
                    key = email.lower()
                    if key not in log:
                        log[key] = []
                    if 'kon2' not in log[key]:
                        log[key].append('kon2')
                    print(f"[{sent}] OK {email}", flush=True)
                except Exception as e:
                    failed.append(email)
                    print(f"FAIL {email}: {e}", flush=True)
                time.sleep(0.5)
    except Exception as e:
        print(f"BATCH ERROR: {e}", flush=True)
        failed.extend([em for em, _ in batch])

# Save updated log
with open(LOG_PATH, 'w') as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print(f"\nДОНЕ: sent={sent}, failed={len(failed)}")
if failed:
    print("FAILED:", failed)
