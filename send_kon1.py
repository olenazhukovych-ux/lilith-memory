import csv, re, smtplib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def extract_first_name(name):
    name = name.strip()
    parts = name.split()
    if not parts: return "Шефе"
    first = parts[0]
    if re.match(r'^[А-ЯІЇЄ][а-яіїє\']+$', first) or re.match(r'^[A-Z][a-z]+$', first):
        return first
    return "Шефе"

def make_html(first_name):
    H1 = "#1f2630"
    H2 = "#8c7fa0"
    BG = "#f7f4fb"

    def mod(title, color, r_list, t_list, d_list):
        r = " &nbsp;·&nbsp; ".join(r_list)
        t = " &nbsp;·&nbsp; ".join(t_list)
        d = " &nbsp;·&nbsp; ".join(d_list)
        return f"""
  <tr><td style="padding:0 40px 8px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px;overflow:hidden;">
      <tr><td style="background:{color};padding:10px 16px;"><p style="margin:0;font-size:13px;color:#ffffff;font-weight:bold;">{title}</p></td></tr>
      <tr><td style="background:{BG};padding:12px 16px;">
        <p style="margin:0 0 5px;font-size:13px;color:#2a2a2a;line-height:1.9;">{r}</p>
        <p style="margin:0 0 4px;font-size:12px;color:#555;line-height:1.8;">{t}</p>
        <p style="margin:0;font-size:12px;color:#aaa;line-height:1.8;">{d}</p>
      </td></tr>
    </table>
  </td></tr>"""

    toc = f"""
  <tr><td style="padding:0 40px 8px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px;overflow:hidden;">
      <tr><td style="background:{H1};padding:10px 16px;"><p style="margin:0;font-size:13px;color:#ffffff;font-weight:bold;">Модуль 0 — Бонусний розділ «Трюфель»</p></td></tr>
      <tr><td style="background:{BG};padding:12px 16px;">
        <p style="margin:0 0 4px;font-size:13px;color:#2a2a2a;line-height:1.9;">Трюфель — рецепт у 6 етапах</p>
        <p style="margin:0;font-size:12px;color:#888;line-height:1.8;">Температурні режими &nbsp;·&nbsp; Словник &nbsp;·&nbsp; Список продуктів</p>
      </td></tr>
    </table>
  </td></tr>""" + \
    mod("Модуль 1 — Лимонний тарт", H2,
        ["R1 Класичний","R2 Запечений","R3 Порційний"],
        ["01 Види меренги","02 Желатин і загусники","03 Критичність цукру","04 Набір кондитера-початківця","05 Температурні режими","06 Форми для тарта","07 Як оцінити тарт","10 Перерахунок під свою форму","11 Як зрозуміти свою духовку"],
        ["08 Словник","09 Література"]) + \
    mod("Модуль 2 — Еклери", H2,
        ["R1 Класичні","R2 Снікерс","R3 З ганашем"],
        ["01 Особливості випікання","02 Десерти з заварного тіста","03 Темперування шоколаду","04 Температурні режими","05 Як оцінити еклер"],
        ["06 Словник","07 Література"]) + \
    mod("Модуль 3 — Кекси", H2,
        ["R1 Мармуровий","R2 Безглютеновий","R3 Мигдалевий нуазет"],
        ["01 Види бісквітів","02 Температурні режими","03 Як оцінити кекс"],
        ["04 Словник","05 Література"]) + \
    mod("Модуль 4 — Чизкейки", H2,
        ["R1 Нью-Йорк","R2 Баскський","R3 Чизкейк-персик"],
        ["01 Види сиру","02 Види тіста","03 Варіації","04 Пектин","05 Кондитерський велюр","06 Температурні режими","07 Як оцінити"],
        ["08 Словник","09 Література"]) + \
    mod("Модуль 5 — Шоколадні десерти", H2,
        ["R1 Шоколадний нуазет","R2 Брауні","R3 Кейк манго"],
        ["01 Шоколад","02 Десерти з шоколаду","03 Праліне","04 Поради по карамелі","05 Температурні режими","06 Як оцінити"],
        ["07 Словник","08 Література"]) + \
    mod("Модуль 6 — Антреме", H2,
        ["R1 Мигдалево-смородиновий","R2 Різдвяне поліно","R3 Анна Павлова"],
        ["01 Види кремів","02 Гід смаків","03 Крем-брюле","04 Кулі та пюре","05 Кондитерський барвник","06 Температурні режими","07 Як оцінити"],
        ["08 Словник","09 Література"]) + \
    mod("Модуль 7 — Бріоші", H2,
        ["R1 З шоколадом","R2 Листковий","R3 Ромова баба"],
        ["01 Борошно","02 Масло","03 Температурні режими","04 Як оцінити"],
        ["05 Словник","06 Література"]) + \
    mod("Модуль 8 — Торти", H2,
        ["R1 Мигдальний","R2 Бенто медовик","R3 Мусовий торт Fantasy"],
        ["01 Горіхи","02 Креми для вирівнювання","03 Дзеркальна глазур","04 Температурні режими","05 Як оцінити"],
        ["06 Словник","08 Література модуля","09 Література всього курсу"])

    greeting = f"{first_name}, привіт!" if first_name != "Шефе" else "Шефе, привіт!"

    return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f0ecf5;font-family:Georgia,serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ecf5;padding:40px 0;">
<tr><td align="center"><table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;overflow:hidden;">
  <tr><td style="background:{H1};padding:32px 40px;text-align:center;">
    <p style="margin:0 0 6px;color:#b8afc6;font-size:11px;letter-spacing:3px;text-transform:uppercase;">Кулінарна Академія</p>
    <h1 style="margin:0 0 8px;color:#ffffff;font-size:24px;font-weight:normal;">Ти завершив(ла) перший рівень 🎂</h1>
    <p style="margin:0;color:rgba(255,255,255,0.7);font-size:15px;">і це лише початок чогось солодкого</p>
  </td></tr>
  <tr><td style="padding:36px 40px 24px;">
    <p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">{greeting}</p>
    <p style="margin:0 0 14px;font-size:16px;color:#333;line-height:1.7;">Вітаємо з завершенням Кондитерського курсу 1 рівня! Ти пройшов(ла) шлях від трюфеля до мусового торту — і тепер знаєш, як працює справжня кондитерська кухня.</p>
    <p style="margin:0;font-size:16px;color:#333;line-height:1.7;">Дякуємо, що довірив(ла) нам цей шлях 💛</p>
  </td></tr>
  <tr><td style="padding:0 40px 24px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};border-left:3px solid #b8afc6;border-radius:0 8px 8px 0;padding:20px 22px;">
      <tr><td>
        <p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Твої матеріали курсу</p>
        <p style="margin:0 0 8px;font-size:14px;color:#444;line-height:1.7;">Протягом курсу ми фіксували всі запитання студентів і оновили матеріали у зручному форматі — з підказками, лайфхаками та відповідями на найпоширеніші питання.</p>
        <p style="margin:0;font-size:14px;color:#444;line-height:1.7;">📚 <strong>Усі текстові матеріали — твої назавжди</strong><br>📱 <strong>Доступ до відеоуроків</strong> — до <strong>березня 2027 року</strong></p>
      </td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:0 40px 24px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:{H1};border-radius:8px;padding:22px 24px;">
      <tr><td>
        <p style="margin:0 0 4px;font-size:12px;color:#b8afc6;letter-spacing:1px;text-transform:uppercase;">Головна книга курсу</p>
        <p style="margin:0 0 14px;font-size:17px;color:#ffffff;font-weight:bold;">Кондитерський курс 1 рівень — повний посібник</p>
        <a href="https://drive.google.com/file/d/13UyI_6IYWocSZ-7V4c_ce8XwCoN6Xvdn/view" style="display:inline-block;background:#b8afc6;color:#1f2630;text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;font-weight:bold;">Завантажити книгу →</a>
      </td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:0 40px 24px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf5f4;border-radius:8px;padding:16px 20px;">
      <tr><td>
        <p style="margin:0;font-size:14px;color:#555;line-height:1.8;">💡 <strong>Як користуватись книгою:</strong><br>
        — Усі пункти у змісті <strong>клікабельні</strong> — натисни на назву і одразу перейдеш на потрібну сторінку.<br>
        — Натисни <strong>Ctrl+F</strong> (або Cmd+F на Mac) і введи будь-яке слово — наприклад «велюр», «ганаш» або «пектин» — книга знайде все миттєво.</p>
      </td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:0 40px 12px;">
    <p style="margin:0 0 4px;font-size:17px;color:#2a2a2a;font-weight:bold;">Що є в книзі</p>
    <p style="margin:0;font-size:13px;color:#999;">9 модулів &nbsp;·&nbsp; 25+ рецептів &nbsp;·&nbsp; теорія, техніки і словники кондитера</p>
  </td></tr>
  {toc}
  <tr><td style="padding:24px 40px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf5f4;border-radius:8px;padding:20px 22px;">
      <tr><td>
        <p style="margin:0 0 10px;font-size:16px;color:#2a2a2a;font-weight:bold;">Що далі? 🍰</p>
        <p style="margin:0 0 12px;font-size:14px;color:#444;line-height:1.7;">На <strong>Кондитерському 2 рівні</strong> тебе чекає справжнє — французькі Макарони, круасани, торти на замовлення з правильним розрахунком, авторські цукерки і шоколад, веганські і безглютенові десерти. Це вже не «я вмію пекти» — це рівень, з яким можна виходити на ринок.</p>
        <p style="margin:0 0 16px;font-size:14px;color:#444;line-height:1.7;">Старт — <strong>25 вересня</strong>. Але вступити і отримати доступ до матеріалів можна вже зараз.</p>
        <a href="https://culinaryacademy.com.ua/candy" style="display:inline-block;background:{H1};color:#ffffff;text-decoration:none;padding:11px 26px;border-radius:5px;font-size:14px;">Дізнатись про 2 рівень →</a>
      </td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:0 40px 24px;">
    <p style="margin:0 0 10px;font-size:15px;color:#333;line-height:1.7;">І маленьке прохання — якщо навчання було для тебе цінним, залиш відгук на Google. Це правда допомагає нам і дозволяє знаходити нових студентів 🙏</p>
    <a href="https://g.page/r/CVTTiYeu4opqEAE/review" style="display:inline-block;border:1px solid #b8afc6;color:#8c7fa0;text-decoration:none;padding:10px 22px;border-radius:5px;font-size:14px;">Залишити відгук на Google →</a>
    <p style="margin:14px 0 0;font-size:14px;color:#777;line-height:1.6;">Є думки, що ми можемо покращити? Просто відповідай на цей лист — ми читаємо кожне слово.</p>
  </td></tr>
  <tr><td style="padding:0 40px 36px;">
    <p style="margin:0 0 4px;font-size:15px;color:#333;">Успіхів тобі на кухні — і до зустрічі на наступному рівні! 💛</p>
    <p style="margin:12px 0 0;font-size:14px;color:#666;">Команда Кулінарної Академії</p>
  </td></tr>
  <tr><td style="background:#f0ecf5;padding:18px 40px;text-align:center;">
    <p style="margin:0;font-size:12px;color:#999;">
      <a href="https://culinaryacademy.com.ua" style="color:#8c7fa0;text-decoration:none;">culinaryacademy.com.ua</a> &nbsp;·&nbsp;
      <a href="https://www.instagram.com/culinary_academy_ua/" style="color:#8c7fa0;text-decoration:none;">Instagram</a> &nbsp;·&nbsp;
      <a href="https://t.me/uca_service" style="color:#8c7fa0;text-decoration:none;">@uca_service</a>
    </p>
  </td></tr>
</table></td></tr></table></body></html>"""

with open('/root/.openclaw/media/inbound/6a2175840ba16---b6ac7aee-192d-4c9d-8d16-ccadeeb056de.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

sent = 0
failed = []

with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as s:
    s.starttls()
    s.login('support@culinary.com.ua', 'idaqfjgvzlycxjiz')
    for row in rows:
        email = row['Email'].strip()
        name = extract_first_name(row['Name'])
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🎂 Твої матеріали Кондитерського курсу 1 рівня — лови і зберігай!'
        msg['From'] = 'Команда Кулінарної Академії <support@culinary.com.ua>'
        msg['To'] = email
        msg.attach(MIMEText(make_html(name), 'html', 'utf-8'))
        try:
            s.send_message(msg)
            sent += 1
            print(f"[{sent}] OK {email}", flush=True)
        except Exception as e:
            failed.append(email)
            print(f"FAIL {email}: {e}", flush=True)
        time.sleep(0.5)

print(f"\nДОНЕ: sent={sent}, failed={len(failed)}")
if failed:
    print("FAILED:", failed)
