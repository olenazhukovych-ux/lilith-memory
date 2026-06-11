#!/usr/bin/env python3
import csv, json, os, smtplib, time, re, sys
from email.mime.text import MIMEText

CSV_PATH = '/root/.openclaw/workspace/all_courses_with_offers.csv'
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'
TAG = 'sales-upsell-margarita'
FROM = 'Маргарита | Кулінарна Академія <support@culinary.com.ua>'
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'support@culinary.com.ua'
SMTP_PASS = 'idaqfjgvzlycxjiz'

HARD_SKIP = {
    'olena.zhukovych@gmail.com', 'allaborduk@icloud.com',
    'sofiamohylnytskaya@gmail.com', 'kseniamohyl@icloud.com',
    'vitaliy.vist@gmail.com', 'tatly.kolien@gmail.com',
    'anka1999.2010x@gmail.com', 'nadezhdarozhko@icloud.com',
    'oleksii.mychka@gmail.com'
}

# Transliteration table (longer combos first)
TRANSLIT = [
    ('shch','щ'), ('sch','щ'), ('sh','ш'), ('ch','ч'), ('zh','ж'), ('kh','х'),
    ('ts','ц'), ('ia','я'), ('ie','є'), ('ii','й'), ('iy','й'),
    ('ya','я'), ('ye','є'), ('yu','ю'), ('yo','й'),
    ('a','а'), ('b','б'), ('c','к'), ('d','д'), ('e','е'), ('f','ф'),
    ('g','г'), ('h','г'), ('i','і'), ('j','й'), ('k','к'), ('l','л'),
    ('m','м'), ('n','н'), ('o','о'), ('p','п'), ('r','р'), ('s','с'),
    ('t','т'), ('u','у'), ('v','в'), ('w','в'), ('x','кс'), ('y','и'), ('z','з'),
]

def transliterate(word):
    result = ''
    low = word.lower()
    i = 0
    while i < len(low):
        matched = False
        for lat, cyr in TRANSLIT:
            if low[i:i+len(lat)] == lat:
                result += cyr
                i += len(lat)
                matched = True
                break
        if not matched:
            result += low[i]
            i += 1
    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]
    return result

def is_cyrillic(word):
    return bool(re.match(r'^[А-Яа-яІіЇїЄєҐґ\'\'-]+$', word))

def is_latin_name(word):
    return bool(re.match(r'^[A-Z][a-zA-Z\'-]+$', word)) and not any(c.isdigit() for c in word)

def extract_name(raw_name):
    """Returns Ukrainian name or None"""
    if not raw_name or not raw_name.strip():
        return None
    first_word = raw_name.strip().split()[0]
    
    if is_cyrillic(first_word):
        # Capitalize properly
        return first_word[0].upper() + first_word[1:].lower() if len(first_word) > 1 else first_word.upper()
    
    if is_latin_name(first_word):
        return transliterate(first_word)
    
    # Nickname - no name
    return None

def make_email(name):
    if name:
        subject = f'{name}, є для вас новини від Академії'
        greeting = f'Привіт, {name}!'
    else:
        subject = 'Є для вас новини від Академії'
        greeting = 'Привіт!'
    
    body = f"""{greeting}

Мене звати Маргарита, я з відділу турботи про студентів Кулінарної Академії.

Пишу, бо скоро в нас стартує новий навчальний потік — і хотіла особисто розповісти вам про оновлену програму.

Ті, хто вже пройшов наступний рівень, кажуть що це зовсім інший погляд на кухню. Там інші техніки, інша глибина — і є кілька речей, які краще розповісти на словах, ніж описати текстом.

До того ж зараз діють спеціальні умови вступу — хочу підібрати для вас найкращий варіант.

Це ні до чого вас не зобов'язує — просто поділюсь деталями, і ви самі вирішите.

Напишіть зручний час і ваш номер — я зателефоную.

Або пишіть одразу мені в Telegram: https://t.me/culinaryacademy_support

З теплом,
Маргарита
Кулінарна Академія"""
    
    return subject, body

def load_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}

def save_log(log):
    tmp = LOG_PATH + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=None)
    os.replace(tmp, LOG_PATH)

def main():
    log = load_log()
    
    # Read CSV
    rows = []
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('Email', '').strip().lower()
            offer = row.get('Що пропонувати', '').strip()
            name_raw = row.get("Ім'я", '').strip()
            if email and offer:
                rows.append((email, name_raw))
    
    print(f'Рядків з пропозицією: {len(rows)}', flush=True)
    
    sent = 0
    skipped_dup = 0
    skipped_hard = 0
    errors = []
    
    # Connect SMTP
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.starttls()
    smtp.login(SMTP_USER, SMTP_PASS)
    
    for idx, (email, name_raw) in enumerate(rows):
        # Hard skip
        if email in HARD_SKIP:
            skipped_hard += 1
            continue
        
        # Dedup
        existing_tags = log.get(email, [])
        if TAG in existing_tags:
            skipped_dup += 1
            continue
        
        name = extract_name(name_raw)
        subject, body = make_email(name)
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = FROM
        msg['To'] = email
        msg['Subject'] = subject
        
        try:
            smtp.sendmail(SMTP_USER, email, msg.as_string())
            sent += 1
            
            # Update log
            if email in log:
                log[email].append(TAG)
            else:
                log[email] = [TAG]
            save_log(log)
            
            if sent % 50 == 0:
                print(f'Прогрес: {sent} відправлено', flush=True)
            
            # Pause logic
            if sent % 200 == 0:
                print(f'Пауза 60с після {sent} листів...', flush=True)
                time.sleep(60)
            else:
                time.sleep(3)
                
        except smtplib.SMTPResponseException as e:
            err_msg = f'{email}: {str(e)}'
            errors.append(err_msg)
            print(f'ПОМИЛКА: {err_msg}', flush=True)
            if e.smtp_code == 550 and b'Daily user sending limit' in (e.smtp_error if isinstance(e.smtp_error, bytes) else str(e.smtp_error).encode()):
                print('Досягнуто денний ліміт відправки Gmail. Зупиняємось.', flush=True)
                break
            # Reconnect on other errors
            try:
                smtp.quit()
            except:
                pass
            try:
                smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
            except Exception as e2:
                print(f'SMTP reconnect failed: {e2}')
                break
            time.sleep(5)
        except Exception as e:
            err_msg = f'{email}: {str(e)}'
            errors.append(err_msg)
            print(f'ПОМИЛКА: {err_msg}', flush=True)
            try:
                smtp.quit()
            except:
                pass
            try:
                smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
            except Exception as e2:
                print(f'SMTP reconnect failed: {e2}')
                break
            time.sleep(5)
    
    try:
        smtp.quit()
    except:
        pass
    
    print(f'\n=== РЕЗУЛЬТАТ ===')
    print(f'Відправлено: {sent}')
    print(f'Пропущено (дублікат): {skipped_dup}')
    print(f'Пропущено (HARD_SKIP): {skipped_hard}')
    print(f'Помилок: {len(errors)}')
    if errors:
        print('Помилки:')
        for e in errors:
            print(f'  {e}')

if __name__ == '__main__':
    main()
