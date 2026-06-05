#!/usr/bin/env python3
import smtplib, json, os, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
FROM_EMAIL = 'iryna@culinary.com.ua'
FROM_NAME = 'Ірина з Кулінарної Академії'
FROM_PASS = 'oymoyevavbucaccx'
LOG_PATH = '/root/.openclaw/workspace/sent_emails_log.json'
TAG = 'kul1-reengage'
SKIP_TAGS = {'kul1', 'kul1-reengage'}
HARD_SKIP = {'nadezhdarozhko@icloud.com','tatly.kolien@gmail.com',
             'anka1999.2010x@gmail.com','olena.zhukovych@gmail.com'}

EMAILS = [
  'ksena0000@ukr.net','6354093@gmail.com','alexeybachuk2@icloud.com','amazonnikitina@gmail.com',
  'angel3008@icloud.com','anna.yenina96@gmail.com','anyaborysovskay@gmail.com','kiryna13@icloud.com',
  'bzalogamarta@gmail.com','kuzmenkohanna@gmail.com','darinavysotskaya@icloud.com','dimtcuk@gmail.com',
  'engityr@gmail.com','eugeniakolosovska@gmail.com','uva.vua.re@gmail.com','tanya.dulko2018@gmail.com',
  'hnv2017@ukr.net','july80@ukr.net','katrinorlova1707@gmail.com','kamay_iren@ukr.net',
  'kursskr@gmail.com','lamerumasha@gmail.com','lorhen9999@gmail.com','lera12015@gmail.com',
  'olifanmy@icloud.com','marsvet125@gmail.com','maryshtd@gmail.com','mihaminkov.wot@gmail.com',
  'mnfedko@gmail.com','nadiadi07@gmail.com','nafanja05@icloud.com','nadiia.dmytriieva@appflame.com',
  'neshca@ukr.net','o-bagnyuk@ukr.net','denis.stikhin@gmail.com','foreverdrunk1717@gmail.com',
  'olenadidyk974@gmail.com','igor.nosats@gmail.com','permanent_csc@icloud.com','pylypenochka@gmail.com',
  'daryna.chukvitska@gmail.com','romanyk0803@icloud.com','ekaterina.golyuk@gmail.com',
  'sidorenko.darya@gmail.com','spayk88@gmail.com','stokolyas.g11.06@gmail.com','citadelna7@outlook.com',
  'q9308484@gmail.com','svetlana22vv@gmail.com','tetyana.birchak@icloud.com','tramontanahott@gmail.com',
  'uliana.kharyna@gmail.com','gumennaanna@gmail.com','maksym.svystunov@jti.com','nadezdabarinova192@gmail.com',
  'vezzas10plus@gmail.com','vira.katuna@gmai.com','vira.pereginec@gmail.com','yevhenii.postolenko@gmail.com',
  'yakyma.m1@icloud.com','janin00781@gmail.com','sheremetkat@gmail.com','markizaangelov30@gmail.com',
  'dyonyse@gmail.com','a.reg.bah@gmail.com','kseniamohylnytskaya@gmail.com','svitlana.baibara@icloud.com',
  'mamonova.svetlana23.82@gmail.com','ilumen07@gmail.com','danasebesevych@gmail.com','nadiia.litucha@gmail.com',
  'naninets.marina@gmail.com','imalchenko@icloud.com','stepanchuk01@gmail.com','kivarkova2017@gmail.com',
  'pitv82014@gmail.com','siniuhanna@gmail.com','tosyabat2210@gmail.com','spitkovska@gmail.com',
  'slavatsiba@gmail.com','nastka.zahar@gmail.com','annamariausyk@gmail.com','gorodilova.lera@gmail.com',
  'oksanaspolyak@gmail.com','svarfolomeeva743@gmail.com','burstintotears12@gmail.com','grifviktoria@gmail.com',
  'julia1912ua@gmail.com','anastasiiaborysenko@gmail.com','ira.malitskaya@gmail.com','irinayudelevych@gmail.com',
  'olka.kalinina.0107@gmail.com','sankakomisar@gmail.com','julia.guzovska@gmail.com','svintsitskanatali@gmail.com',
  'yulliavoitiuk@gmail.com','nikitchukk@gmail.com','ivanpanasuk88@gmail.com','ndovmat@gmail.com',
  'margaryta.shykula@gmail.com','yuliyakrot@yahoo.com','aodlyvanska@gmail.com','katrenkuprivet77@gmail.com',
  'pilipenkomvi@gmail.com','nsizonets28@gmail.com','nadyshabarinova@gmail.com','zmiyun@gmail.com',
  'anyfedorenko1506@gmail.com','yistratova9@gmail.com','feilong.diana@gmail.com','azavgorodnjaya@gmail.com',
  'bagdasaryan@ukr.net','anton.a.sid@gmail.com','aghayevad@gmail.com','lebed555lebed@gmail.com',
  'galina.shapoval3011@gmail.com','alinaaleksandrova777@ukr.net','andriym2000@icloud.com',
  'annamymail.anna@gmail.com','antoninavintonyak@gmail.com','kristalik90@gmail.com',
  'kuznetsova.letta@gmail.com','lidusia92@gmail.com','mariia.davydova@outlook.com',
  'marusialutvun@gmail.com','mbulakhova@gmail.com','n.v.reznik@gmail.com','aila.yagoda@gmail.com',
  'natasha.shaporenko@gmail.com','semvladislav@ukr.net','sty.ktps@gmail.com','victoriakondes@gmail.com',
  'voznyukanna1998@icloud.com','yaaaakam@gmail.com','stas.yamkovyi@gmail.com','platena089@gmail.com',
  'belovolova.natalya@gmail.com','askrgr@gmail.com',
  # new from lists 5-7
  'andriiyadrov08@gmail.com','azimhal@gmail.com','vikanestrachuk@gmail.com','sokd@ukr.net',
  'rozmyslova3013@gmail.com','diana.teb2014@gmail.com','bobrfin01@gmail.com','sh-el@ukr.net',
  'aleksandradudar3201@gmail.com','tetiana.kazarian@gmail.com','glownata@yandex.ru',
  'mary.kadralieva@gmail.com','janesolomon2012@gmail.com','runadrag@gmail.com',
  'pentsak.a@gmail.com','irynaboiko000@gmail.com','marymanka@bk.ru','shtachenkom@gmail.com',
  'victoria.brich@gmail.com','luboff.bauer1011@gmail.com','iryna.chr@gmail.com','markketi12@gmail.com',
  'denys.baluba@gmail.com','msavtest3@gmail.com','makarchuk.svet@gmail.com','nanni18@i.ua',
  'hvitalyano@gmail.com','viktoriaoleksandrivnasemenist@gmail.com','merkulova3101@gmail.com',
  'sofiasvitlik@gmail.com','1982irinanm@gmail.com','mam030494@gmail.com','barvin@ukr.net',
  'moriagusenitsa@gmail.com','kotovalena2000@gmail.com','trofanchuklena@gmail.com',
  'halyayevtukh@gmail.com','tanya.repetska@gmail.com','svitlanasobchuk@gmail.com',
  'likhachova.yulia@gmail.com','smileryddi1702@gmail.com','dmytronovikov69@gmail.com',
  'adrianasvyatkivska@gmail.com','ksyuha1206@gmail.com','galyna10tkachyk@gmail.com',
  'minmat102984@gmail.com','julia.kmita@gmail.com','isvnukova@gmail.com',
  'kameneva_xxx@mail.ru','dmitry.landkom@gmail.com','macjopa@gmail.com','julia@kalaeva.com',
  'rustik00@gmail.com','ohorodnykbogdanna@gmail.com','oksana.kitchenit@gmail.com',
  'nokkostik@ukr.net','voevutskaya20111@gmail.com','g1h3k5@gmail.com','magallana12@gmail.com',
  'evovk1980@ukr.net','irustik00@gmail.com','mableeks@gmail.com','dpsplus@gmail.com',
  'mailme5757@gmail.com','voitenko.boy@gmail.com','ljudmila.galij@gmail.com',
  'olesiakrmn@gmail.com','yulia.maniachuk@gmail.com',
  # micro-list
  'pronchatovaliliya45@gmail.com','lenusik2805@gmail.com','eliseykashuba@gmail.com',
  'dzhelialova@gmail.com','siroezhkina@gmail.com',
]

# Deduplicate
seen = set()
emails_dedup = []
for e in EMAILS:
    e = e.lower().strip()
    if e and e not in seen:
        seen.add(e)
        emails_dedup.append(e)

with open('/root/.openclaw/workspace/kul1_reengage_v2_email.html', encoding='utf-8') as f:
    html_template = f.read()

def save_log(log):
    tmp = LOG_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LOG_PATH)

with open(LOG_PATH, encoding='utf-8') as f:
    log = json.load(f)

sent = skipped = 0

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.starttls()
    smtp.login(FROM_EMAIL, FROM_PASS)

    for email in emails_dedup:
        e = email.lower().strip()
        if e in HARD_SKIP:
            print(f'HARD_SKIP {e}')
            skipped += 1
            continue
        if set(log.get(e, [])) & SKIP_TAGS:
            print(f'SKIP {e}')
            skipped += 1
            continue

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '🥦 Ваші матеріали Кулінарного курсу оновлено — завантажте безкоштовно'
            msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
            msg['To'] = e
            msg.attach(MIMEText(html_template, 'html', 'utf-8'))
            smtp.sendmail(FROM_EMAIL, [e], msg.as_bytes())
            
            if e not in log:
                log[e] = []
            if TAG not in log[e]:
                log[e].append(TAG)
            save_log(log)
            
            sent += 1
            print(f'[{sent}] OK {e}')
            time.sleep(0.3)
        except Exception as ex:
            print(f'FAIL {e}: {ex}')

print(f'\nГотово: відправлено {sent}, пропущено {skipped}')
