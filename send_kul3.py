import csv, json, re, smtplib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CSV_PATH = '/root/.openclaw/media/inbound/6a217f2b3884b---5a33f058-bf28-45ae-95d8-04cda75ad59b.csv'
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'
SKIP = {'tatly.kolien@gmail.com'}  # пожиттєвий доступ

AC = "#5C6142"
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

def mod(num, title, items):
    dots = " &nbsp;·&nbsp; ".join(items)
    return f"""<tr><td style="padding:0 40px 8px;"><table width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px;overflow:hidden;"><tr><td style="background:{AC};padding:10px 16px;"><p style="margin:0;font-size:13px;color:#ffffff;font-weight:bold;">Модуль {num} — {title}</p></td></tr><tr><td style="background:{MB};padding:12px 16px;"><p style="margin:0;font-size:13px;color:#3a3a3a;line-height:2.0;">{dots}</p></td></tr></table></td></tr>"""

toc = \
mod("I","Крафтовий сир",["Вступ","Молоко","Закваски і ферменти","Обладнання і гігієна","Техніки","Після приготування","Довідники","Де купити","Види сирів","Travel Blog","Типові помилки","Матриця сирів","Чек-лист сироробу","Моцарела","Рикота","Панір","Лабне","Бринза","Камамбер","Рецепти з моцарелою","Рецепти з рикотою","Рецепти з паніром","Рецепти з бринзою"]) + \
mod("II","Хліб на заквасці",["Вступ і словник","Закваска","Борошно для хліба","Вода, сіль, інгредієнти","Тісто: заміс, ферментація","Обладнання пекаря","Формування, надрізання, випікання","Планування, заморозка, дискард","Тартін","Чіабата","Хліб у рукаві","Цільнозерновий хліб","Багет","Фокачча","Житній і безглютеновий","Помилки і чек-лист","Закваска замість дріжджів"]) + \
mod("III","Ферментація",["Словник кухаря-ферментатора","Теорія ферментації","Базові правила ферментації овочів","Квашена капуста","Ферментована морква","Ферментовані огірки","Ферментована редиска","Швидкоферментований гарбуз","Ферментована цибуля","Буряк з яблуком та імбиром","Перець болгарський","Цвітна капуста з куркумою","Ферментовані томати","Кімчі","Ферментація фруктів і лимони","Часниковий соус","Домашні кваси","Комбуча","Йогурт і кефір","Лабне і творог"]) + \
mod("IV","Джеми і консервація",["Словник кухаря","Пастеризація і стерилізація","Банки, кришки, інструменти","Консерванти і текстура","Кислотність і мікробіологія","Довідкові таблиці","Власна рецептура","Айвовий мармелад","Апельсиновий джем","Малиновий джем","Абрикосовий джем","Апельсиновий мармелад","Персиковий джем","Вишневий джем","Грушеве варення","Яблучний джем","Груша в сиропі","Цибулевий конфітюр","Томати пелаті","В'ялені томати","Соус BBQ","Томатний соус для пасти","Сливовий соус","Обліпиховий соус з медом"]) + \
mod("V","М'ясні вироби",["Основи роботи з м'ясом","Техніки засолення, копчення, в'ялення","Безпека та контроль якості","Ковбаски Буден Блан","Терин де Кампань","Курячі джерки","В'ялена качина грудка","Копчена шинка","Копчена курка","Копчені свинячі ребра","Бекон і шинка (3 варіації)","Смальці та м'ясні намазки (5 рецептів)","Вегетаріанські альтернативи (3 рецепти)","Словник кухаря"]) + \
mod("VI","Спеції",["Теорія спецій","Техніки обробки","Поєднання спецій","Дегідровані овочі","Сухий бульйон","Селерова сіль","Ванільний рай","Овочеві та фруктові пудри","В'ялені томати","Крафтові солі","Цукри і медові настої","Олії і ферментовані соуси","Фруктові соуси","Холодні соуси","Суміші спецій","Суміші для десертів","Маринади","Словник кухаря","Рекомендована література всього курсу","Лист від Олі"])

def make_html(first_name):
    greeting = f"{first_name}, привіт!" if first_name != "Шефе" else "Шефе, привіт!"
    return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:{BG};font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};padding:40px 0;"><tr><td align="center"><table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;overflow:hidden;">
  <tr><td style="background:{AC};padding:32px 40px;text-align:center;"><p style="margin:0 0 6px;color:rgba(255,255,255,0.6);font-size:11px;letter-spacing:3px;text-transform:uppercase;">Кулінарна Академія</p><h1 style="margin:0 0 8px;color:#ffffff;font-size:24px;font-weight:normal;">Ти пройшов(ла) весь кулінарний шлях 🏆</h1><p style="margin:0;color:rgba(255,255,255,0.75);font-size:15px;">Кулінарний курс 3 рівень — Крафтяр — завершено</p></td></tr>
  <tr><td style="padding:36px 40px 20px;"><p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">{greeting}</p><p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">Вітаємо з завершенням Кулінарного курсу 3 рівня! Ти навчився(лась) робити сир, пекти хліб на заквасці, ферментувати, консервувати, в'ялити м'ясо і складати власні суміші спецій. Це вже не просто «готувати» — це справжнє крафтове ремесло.</p><p style="margin:0;font-size:16px;color:#333;line-height:1.7;">Дякуємо, що пройшов(ла) цей шлях до кінця 💛</p></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#fff8e6;border:2px solid #e8c84a;border-radius:8px;padding:20px 22px;"><tr><td><p style="margin:0 0 8px;font-size:17px;color:#2a2a2a;font-weight:bold;">🆕 Матеріали суттєво оновлено і розширено!</p><p style="margin:0 0 10px;font-size:14px;color:#444;line-height:1.7;">Ми повністю переглянули всі 6 модулів — додали нові рецепти, поглибили теорію, розширили довідники і практичні гайди. Особливо великі оновлення у модулях про сир, ферментацію і спеції.</p><p style="margin:0;font-size:14px;color:#2a2a2a;line-height:1.7;font-weight:bold;">Якщо ти вже завантажував(ла) матеріали раніше — обов'язково скачай нові версії. Там набагато більше.</p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};border-left:3px solid {AC};border-radius:0 8px 8px 0;padding:20px 22px;"><tr><td><p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Твої матеріали курсу</p><p style="margin:0 0 8px;font-size:14px;color:#444;line-height:1.7;">6 великих модулів — сир, хліб, ферментація, консервація, м'ясні вироби, спеції. Кожен — окремий всесвіт.</p><p style="margin:0;font-size:14px;color:#444;line-height:1.7;">📚 <strong>Усі текстові матеріали — твої назавжди</strong><br>📱 <strong>Доступ до відеоуроків</strong> — до <strong>березня 2027 року</strong></p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{AC};border-radius:8px;padding:22px 24px;"><tr><td><p style="margin:0 0 4px;font-size:12px;color:rgba(255,255,255,0.65);letter-spacing:1px;text-transform:uppercase;">Головна книга курсу</p><p style="margin:0 0 14px;font-size:17px;color:#ffffff;font-weight:bold;">Крафтяр — Велика книга. Повний посібник</p><a href="https://drive.google.com/file/d/1Q3wbyCV-mmbBSQNBNwZoPvwUgnJ8Hoyt/view" style="display:inline-block;background:#ffffff;color:{AC};text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;font-weight:bold;">Завантажити книгу →</a></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:#fff8e6;border-radius:8px;padding:16px 20px;"><tr><td><p style="margin:0;font-size:14px;color:#555;line-height:1.8;">💡 <strong>Як користуватись книгою:</strong><br>— Усі пункти у змісті <strong>клікабельні</strong> — натисни на назву і перейдеш одразу на потрібну сторінку.<br>— Натисни <strong>Ctrl+F</strong> (або Cmd+F на Mac) і введи будь-яке слово — «кімчі», «закваска», «бринза» — знайде миттєво.</p></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 12px;"><p style="margin:0 0 4px;font-size:17px;color:#2a2a2a;font-weight:bold;">Що є в книзі</p><p style="margin:0;font-size:13px;color:#999;">6 модулів &nbsp;·&nbsp; 100+ рецептів і технік &nbsp;·&nbsp; довідники, чек-листи, словники майстра</p></td></tr>
  {toc}
  <tr><td style="padding:24px 40px;"><table width="100%" cellpadding="0" cellspacing="0" style="background:{MB};border-radius:8px;padding:20px 22px;"><tr><td><p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">А якщо хочеш ще? 🍰</p><p style="margin:0 0 12px;font-size:14px;color:#444;line-height:1.7;">Ти пройшов(ла) всі три рівні кулінарного — тепер відкрито ще один напрямок. <strong>Кондитерські курси</strong> — це окремий світ: тарти, еклери, торти, макарони, шоколад. Зовсім інша техніка, інша точність, інший кайф.</p><p style="margin:0 0 16px;font-size:14px;color:#444;line-height:1.7;">Старт — <strong>25 вересня</strong>. Місця є.</p><a href="https://culinaryacademy.com.ua/candy" style="display:inline-block;background:{AC};color:#ffffff;text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;">Переглянути кондитерські курси →</a></td></tr></table></td></tr>
  <tr><td style="padding:0 40px 24px;"><p style="margin:0 0 10px;font-size:15px;color:#333;line-height:1.7;">І маленьке прохання — якщо навчання було для тебе цінним, залиш відгук на Google. Це правда допомагає нам і дозволяє знаходити нових студентів 🙏</p><a href="https://g.page/r/CVTTiYeu4opqEAE/review" style="display:inline-block;border:1px solid {AC};color:{AC};text-decoration:none;padding:10px 22px;border-radius:5px;font-size:14px;">Залишити відгук на Google →</a><p style="margin:14px 0 0;font-size:14px;color:#777;line-height:1.6;">Є думки, що ми можемо покращити? Просто відповідай на цей лист — ми читаємо кожне слово.</p></td></tr>
  <tr><td style="padding:0 40px 36px;"><p style="margin:0 0 4px;font-size:15px;color:#333;">З повагою і гордістю за тебе 💛</p><p style="margin:12px 0 0;font-size:14px;color:#666;">Команда Кулінарної Академії</p></td></tr>
  <tr><td style="background:{BG};padding:18px 40px;text-align:center;"><p style="margin:0;font-size:12px;color:#999;"><a href="https://culinaryacademy.com.ua" style="color:{AC};text-decoration:none;">culinaryacademy.com.ua</a> &nbsp;·&nbsp; <a href="https://www.instagram.com/culinary_academy_ua/" style="color:{AC};text-decoration:none;">Instagram</a> &nbsp;·&nbsp; <a href="https://t.me/uca_service" style="color:{AC};text-decoration:none;">@uca_service</a></p></td></tr>
</table></td></tr></table></body></html>"""

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

with open(LOG_PATH) as f:
    log = json.load(f)

to_send = []
skipped = []
for r in rows:
    email = r['Email'].strip()
    key = email.lower()
    if key in SKIP:
        skipped.append(email)
        print(f"SKIP (не контактувати): {email}", flush=True)
    elif 'kul3' in log.get(key, []):
        skipped.append(email)
        print(f"SKIP (вже отримав kul3): {email}", flush=True)
    else:
        to_send.append((email, extract_first_name(r['Name'])))

print(f"Відправляти: {len(to_send)}, пропустити: {len(skipped)}", flush=True)

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
                msg['Subject'] = '🏆 Твої матеріали Кулінарного курсу 3 рівня (Крафтяр) — оновлено і розширено!'
                msg['From'] = 'Команда Кулінарної Академії <support@culinary.com.ua>'
                msg['To'] = email
                msg.attach(MIMEText(make_html(name), 'html', 'utf-8'))
                try:
                    s.send_message(msg)
                    sent += 1
                    key = email.lower()
                    if key not in log: log[key] = []
                    if 'kul3' not in log[key]: log[key].append('kul3')
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

print(f"\nДОНЕ: sent={sent}, skipped={len(skipped)}, failed={len(failed)}")
if failed:
    print("FAILED:", failed)
