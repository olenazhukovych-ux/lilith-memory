import csv, json, re, smtplib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CSV_PATH = '/root/.openclaw/media/inbound/6a217df2ebf22---ff73586f-6db3-4624-834c-dbd7e0e36d08.csv'
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'

AC = "#5C6142"
H2 = "#7a8a55"
BG = "#f5f2ed"
MB = "#f0ede6"

def extract_first_name(name):
    name = name.strip()
    parts = name.split()
    if not parts: return "Шефе"
    first = parts[0]
    if re.match(r'^[А-ЯІЇЄ][а-яіїє\']+$', first) or re.match(r'^[A-Z][a-z]+$', first):
        return first
    return "Шефе"

def mod(title, recipes, theory, book):
    r = " &nbsp;·&nbsp; ".join(recipes)
    t = " &nbsp;·&nbsp; ".join(theory)
    return f"""<tr><td style="padding:0 40px 8px;"><table width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px;overflow:hidden;"><tr><td style="background:{AC};padding:10px 16px;"><p style="margin:0;font-size:13px;color:#ffffff;font-weight:bold;">{title}</p></td></tr><tr><td style="background:{MB};padding:12px 16px;"><p style="margin:0 0 5px;font-size:13px;color:#2a2a2a;line-height:1.9;"><strong style="color:{AC};">Рецепти:</strong> {r}</p><p style="margin:0 0 4px;font-size:12px;color:#555;line-height:1.8;"><strong>Теорія:</strong> {t}</p><p style="margin:0;font-size:12px;color:#888;line-height:1.8;">📖 {book}</p></td></tr></table></td></tr>"""

toc = \
mod("Модуль 1 — Французька кухня",["Цибулевий суп","Цесарка у вині","Телячий бланкет","Фрікасе","Пате ан крут"],["Гастрономічні регіони Франції","Хліб Франції","Французькі сири","Французькі вина","Французькі коктейлі","Історія Мішлену","Французькі шефи","Страви-візитівки","Словник кухаря"],"Французька кухня") + \
mod("Модуль 2 — Італійська кухня",["Качо е пеппе","Папарделі з рагу","Різотто Парміджано","Різотто з морепродуктами","Тортеліні з м'ясом"],["Гастрономічні регіони","Види борошна","Види пасти","Італійські сири","Італійські вина","Італійські коктейлі","Італійські шефи","Страви-візитівки","Словник"],"Італійська кухня") + \
mod("Модуль 3 — Іспанська кухня",["Паелья","Восьминіг по-галісійськи","Тушені бичачі хвости","Іспанська тортілья","Каталонський крем"],["Гастрономічні регіони Іспанії","Види олії","Іспанські сири","Іспанські коктейлі","Види хамону","Іспанські вина","Іспанські шефи","Страви-візитівки","Словник"],"Іспанська кухня") + \
mod("Модуль 4 — Індійська кухня",["Курка Масала","Суп Даал","Курка Тандурі","Паранта","Карі та пілав"],["Гастрономічні регіони Індії","Індійські спеції","Молочні продукти Індії","Чаї і напої Індії","Страви-візитівки","Словник кухаря"],"Індійська кухня") + \
mod("Модуль 5 — Скандинавська кухня (Данія)",["Чорна тріска з корнеплодами","Датський хліб для сморебродів","Закуска з редисом","Смажений топінамбур і оселедець","Смореброди"],["Гастрономічна Скандинавія","Принципи нордичної кухні","New Nordic Cuisine","Страви-візитівки Данії","Страви-візитівки Швеції","Страви-візитівки Норвегії","Страви Фінляндії та Ісландії","Скандинавські шефи","Словник кухаря"],"Скандинавська кухня") + \
mod("Модуль 6 — Американська кухня (США)",["Бейгл","Бургер з картоплею фрі","Краб кейк","Крильця BBQ","Нагетси"],["Гастрономічна Америка","Принципи американської кухні","Спеції: міфи і факти","Страви-візитівки американської кухні","Улюблені страви президентів США","Американські шефи","Словник кухаря"],"Американська кухня") + \
mod("Модуль 7 — Тайська кухня",["Том Ям","Том Кха","Пад Тай","Као Пат","Салат з папаєю","Манго стікі райс"],["Гастрономічний Таїланд","Принципи тайської кухні","Тайські ароматичні продукти","Історія тайської кухні","Страви-візитівки Таїланду","Тайські шефи","Словник кухаря"],"Тайська кухня") + \
mod("Модуль 8 — Мексиканська кухня",["Тортілья та Кесаділья","Тако з яловичиною","Енчіладас","Чілі кон карне","Три молока"],["Гастрономічна Мексика","Принципи мексиканської кухні","Чилі та спеції Мексики","Історія мексиканської кухні","Страви-візитівки Мексики","Мексиканські шефи","Словник кухаря","Рекомендована література"],"Мексиканська кухня")

def make_html(first_name):
    greeting = f"{first_name}, привіт!" if first_name != "Шефе" else "Шефе, привіт!"
    return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:{BG};font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};padding:40px 0;"><tr><td align="center"><table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;overflow:hidden;">
  <tr><td style="background:{AC};padding:32px 40px;text-align:center;"><p style="margin:0 0 6px;color:rgba(255,255,255,0.6);font-size:11px;letter-spacing:3px;text-transform:uppercase;">Кулінарна Академія</p><h1 style="margin:0 0 8px;color:#ffffff;font-size:24px;font-weight:normal;">Ти об'їхав(ла) весь світ — не виходячи з кухні 🌍</h1><p style="margin:0;color:rgba(255,255,255,0.75);font-size:15px;">Кулінарний курс 2 рівень завершено</p></td></tr>
  <tr><td style="padding:36px 40px 20px;"><p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">{greeting}</p><p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">Вітаємо з завершенням Кулінарного курсу 2 рівня! Франція, Італія, Іспанія, Індія, Скандинавія, США, Таїланд, Мексика — 8 кухонь, десятки технік, і все це тепер у твоєму арсеналі.</p><p style="margin:0;font-size:16px;color:#333;line-height:1.7;">Дякуємо, що пройшов(ла) цей смачний шлях разом з нами 💛</p></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#fff8e6;border:2px solid #e8c84a;border-radius:8px;padding:20px 22px;"><tr><td><p style="margin:0 0 8px;font-size:16px;color:#2a2a2a;font-weight:bold;">🆕 Матеріали оновлено і значно розширено!</p><p style="margin:0 0 8px;font-size:14px;color:#444;line-height:1.7;">Ми переробили і доповнили всі 8 книг курсу — додали нові розділи, розширили теоретичну базу, вклали більше гастрономічного контексту по кожній країні.</p><p style="margin:0;font-size:14px;color:#444;line-height:1.7;"><strong>Якщо ти вже скачував(ла) матеріали раніше — обов'язково завантаж нові версії.</strong> Там справді набагато більше.</p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};border-left:3px solid {AC};border-radius:0 8px 8px 0;padding:20px 22px;"><tr><td><p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Твої матеріали курсу</p><p style="margin:0 0 8px;font-size:14px;color:#444;line-height:1.7;">8 книг — по одній на кожну кухню світу — плюс зведений посібник усього курсу.</p><p style="margin:0;font-size:14px;color:#444;line-height:1.7;">📚 <strong>Усі текстові матеріали — твої назавжди</strong><br>📱 <strong>Доступ до відеоуроків</strong> — до <strong>березня 2027 року</strong></p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{AC};border-radius:8px;padding:22px 24px;"><tr><td><p style="margin:0 0 4px;font-size:12px;color:rgba(255,255,255,0.65);letter-spacing:1px;text-transform:uppercase;">Головна книга курсу</p><p style="margin:0 0 14px;font-size:17px;color:#ffffff;font-weight:bold;">Кухні світу — зведений посібник</p><a href="https://drive.google.com/file/d/1B1xoEQFPA_gNK5mrIb-jcLBmC5hFg_Ul/view" style="display:inline-block;background:#ffffff;color:{AC};text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;font-weight:bold;">Завантажити книгу →</a></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#fff8e6;border-radius:8px;padding:16px 20px;"><tr><td><p style="margin:0;font-size:14px;color:#555;line-height:1.8;">💡 <strong>Як користуватись книгою:</strong><br>— Усі пункти у змісті <strong>клікабельні</strong> — натисни на назву і одразу перейдеш на потрібну сторінку.<br>— Натисни <strong>Ctrl+F</strong> (або Cmd+F на Mac) і введи страву, інгредієнт або країну — знайде миттєво.</p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 12px;"><p style="margin:0 0 4px;font-size:17px;color:#2a2a2a;font-weight:bold;">Що є в книзі</p><p style="margin:0;font-size:13px;color:#999;">8 кухонь світу &nbsp;·&nbsp; 40+ рецептів &nbsp;·&nbsp; гастрономічний контекст, вина, шефи, словники</p></td></tr>
  {toc}
  <tr><td style="padding:24px 40px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{MB};border-radius:8px;padding:20px 22px;"><tr><td><p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Що далі? 🔪</p><p style="margin:0 0 12px;font-size:14px;color:#444;line-height:1.7;">На <strong>Кулінарному 3 рівні — Крафтяр</strong> тебе чекають авторські техніки, ферментація, хліб на заквасці, робота з локальними продуктами і власний кулінарний стиль. Це рівень, де ти вже не повторюєш — а створюєш.</p><p style="margin:0 0 16px;font-size:14px;color:#444;line-height:1.7;">Старт — <strong>25 вересня</strong>. Вступити можна вже зараз.</p><a href="https://culinaryacademy.com.ua/basic" style="display:inline-block;background:{AC};color:#ffffff;text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;">Дізнатись про 3 рівень →</a></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><p style="margin:0 0 10px;font-size:15px;color:#333;line-height:1.7;">І маленьке прохання — якщо навчання було для тебе цінним, залиш відгук на Google. Це правда допомагає нам і дозволяє знаходити нових студентів 🙏</p><a href="https://g.page/r/CVTTiYeu4opqEAE/review" style="display:inline-block;border:1px solid {AC};color:{AC};text-decoration:none;padding:10px 22px;border-radius:5px;font-size:14px;">Залишити відгук на Google →</a><p style="margin:14px 0 0;font-size:14px;color:#777;line-height:1.6;">Є думки, що ми можемо покращити? Просто відповідай на цей лист — ми читаємо кожне слово.</p></td></tr>
  <tr><td style="padding:0 40px 36px;"><p style="margin:0 0 4px;font-size:15px;color:#333;">До зустрічі на наступному рівні! 💛</p><p style="margin:12px 0 0;font-size:14px;color:#666;">Команда Кулінарної Академії</p></td></tr>
  <tr><td style="background:{BG};padding:18px 40px;text-align:center;"><p style="margin:0;font-size:12px;color:#999;"><a href="https://culinaryacademy.com.ua" style="color:{AC};text-decoration:none;">culinaryacademy.com.ua</a> &nbsp;·&nbsp; <a href="https://www.instagram.com/culinary_academy_ua/" style="color:{AC};text-decoration:none;">Instagram</a> &nbsp;·&nbsp; <a href="https://t.me/uca_service" style="color:{AC};text-decoration:none;">@uca_service</a></p></td></tr>
</table></td></tr></table></body></html>"""

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

with open(LOG_PATH) as f:
    log = json.load(f)

to_send = [(r['Email'].strip(), extract_first_name(r['Name'])) for r in rows if 'kul2' not in log.get(r['Email'].strip().lower(), [])]
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
                msg['Subject'] = '🌍 Твої матеріали Кулінарного курсу 2 рівня — 8 оновлених книг!'
                msg['From'] = 'Команда Кулінарної Академії <support@culinary.com.ua>'
                msg['To'] = email
                msg.attach(MIMEText(make_html(name), 'html', 'utf-8'))
                try:
                    s.send_message(msg)
                    sent += 1
                    key = email.lower()
                    if key not in log: log[key] = []
                    if 'kul2' not in log[key]: log[key].append('kul2')
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
