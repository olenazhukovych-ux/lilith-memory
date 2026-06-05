#!/usr/bin/env python3
import smtplib, json, os, sys, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'support@culinary.com.ua'
SMTP_PASS = 'idaqfjgvzlycxjiz'
FROM_NAME = 'Ірина з Кулінарної Академії'
FROM_ADDR = 'support@culinary.com.ua'
SUBJECT   = '📚 Оновлені матеріали Кондитерського курсу — ваша книга всередині'

LOG_FILE  = '/root/.openclaw/workspace/sent_emails_log.json'
HTML_FILE = '/root/.openclaw/workspace/kon1_reengage_email.html'
TAG       = 'kon1-reengage'

HARD_SKIP = {
    'nadezhdarozhko@icloud.com', 'tatly.kolien@gmail.com',
    'anka1999.2010x@gmail.com', 'olena.zhukovych@gmail.com',
    'oleksii.mychka@gmail.com'
}
SKIP_TAGS = {'kon1', 'kon1-reengage'}

RECIPIENTS = ["sokolova27011985@gmail.com", "eva3108patiston@gmail.com", "ihor.holosai@gmail.com", "marinka.garets@gmail.com", "valter70@meta.ua", "bulakaieva@gmail.com", "rymaralla23@gmail.com", "katepillu@gmail.com", "fellini1807@gmail.com", "julia1khirova@gmail.com", "irka.a1806@gmail.com", "dramaretska0902@gmail.com", "allo672htconemini@gmail.com", "grigoryevna@gmail.com", "mariavileita@gmail.com", "irynashepeta@gmail.com", "anna.romanuk2000@gmail.com", "olga.koshmelyuk@gmail.com", "irynalys@yahoo.es", "slyvkasofiya@gmail.com", "yulia9lipach@gmail.com", "oms.tkachenko@gmail.com", "kozhantanya2@gmail.com", "anutische@gmail.com", "marta.voitanowych@gmail.com", "sveta_2425@ukr.net", "vakulenko2094@gmail.com", "mad.4redhead@gmail.com", "nataliaaleksandrenko@gmail.com", "ganna.kukusya1212@gmail.com", "tanyayatsyshyn@gmail.com", "alina12364658@gmail.com", "minmat102984@gmail.com", "allatrok@yahoo.com", "likakorol11@gmail.com", "m.v.shevchenko.1@gmail.com", "vo310578snv@gmail.com", "vaismans@yahoo.com", "evovk1980@ukr.net", "diana.teb2014@gmail.com", "natasha.k.8523@gmail.com", "alepestii@gmail.com", "char1otte060890@gmail.com", "victoria1410sh@gmail.com", "klimovicn2019@gmail.com", "grischuk.oo@gmail.com", "savenkosabina@gmail.com", "iamxsu@gmail.com", "jana.mykchajlo@gmail.com", "horeca28@ukr.net", "daria.pnmrnk15@gmail.com", "ann.iurchenko@gmail.com", "iraveles@gmail.com", "annaangie@me.com", "latuzov@gmail.com", "velygorskaolga@gmail.com", "zorina07@yahoo.com", "the.malishevskyi@gmail.com", "journalistuk@yahoo.co.uk", "stanislavzubchenkoo@gmail.com", "renatapavl@yahoo.com", "julia.golomedova@gmail.com", "m.sineokaya@gmail.com", "uliana.andersson@gmail.com", "nadiyavrk@yahoo.com", "elena.podkopaieva@gmail.com", "strelka.olga.s@gmail.com", "alinaaleksandrova777@ukr.net", "kkukoyashnaya@gmail.com", "pritula.n77y@gmail.com", "yuriyoursky@gmail.com", "natashakozlovskaya308@gmail.com", "rra.zagorska@gmail.com", "mail.andriyvb@gmail.com", "mashababintseva@gmail.com", "hannayankina@gmail.com", "irustik00@gmail.com", "kucherovpavelbusiness@gmail.com", "juliaboichenko555@gmail.com", "tanyapodvernyk@i.ua", "anya.revega@gmail.com", "oliaradio@gmail.com", "dariam0802@gmail.com", "helen15063105@gmail.com", "melnik_mikola_ukr@ukr.net", "alunia2010@hotmail.com", "katekurinna@gmail.com", "sonia.nosenko@gmail.com", "demynv@gmail.com", "inna.huska@gmail.com", "travelagency.dnepr@gmail.com", "elza14.7mail@gmail.com", "viktoriaivanysko@gmail.com", "tultultaltal@gmail.com", "sofija.medvedeva@gmail.com", "dr.leonenko@gmail.com", "maria1992mini@gmail.com", "piliuchenko@gmail.com", "alenask10@gmail.com", "elyadear@gmail.com", "iryna.doroshkevych@gmail.com", "vadyalotr@gmail.com", "ivvera.f@gmail.com", "mmarinka951@gmail.com", "qwerty1967@live.ru", "pylypenkody@gmail.com", "valery.shadova@gmail.com", "julianaastion@gmail.com", "balytska.nadya@gmail.com", "valentun711@gmail.com", "chernichkooleg34@gmail.com", "natynihao@gmail.com", "ymolkanova@gmail.com", "ilona.fedoriv333@gmail.com", "mariia.bober@gmail.com", "olha.vorobei@outlook.com", "tinatretiak@gmail.com", "ivabra@gmail.com", "alona.prus@icloud.com", "angelinatoth93@gmail.com", "shehalcovat@gmail.com", "kate.skuba@gmail.com", "kolesnichenko1995@gmail.com", "viktoriia.birthday.2022@gmail.com", "lyudmylavlasyuk@ukr.net", "anya.koroliova@gmail.com", "grandahristina95@gmail.com", "sonka.marmelad@gmail.com", "ponomarenkoyav@gmail.com", "ketka2303@icloud.com", "helgoch_ka@ukr.net", "olena.o.strutinska@gmail.com", "foodnat@gmail.com", "yourhope21@gmail.com", "margonosova210809@gmail.com", "gurinayuliia94@gmail.com", "vsushkevych@ukr.net", "zaliju01@gmail.com", "pidvezanao@gmail.com", "handel@echlodnie.com.pl", "lifeisgood.feelit@gmail.com", "bonaqwa07@gmail.com", "libelleweb@gmail.com", "sydorenko.inna@gmail.com", "merefa_1978@ukr.net", "olgaborysovska@gmail.com", "numezmat@ukr.net", "polanna1301@gmail.com", "kononenkoira090283@ukr.net", "kondratyevarita@gmail.com", "npetrova5522@gmail.com", "odskoroxod@gmail.com", "adjkatyadovgamail@gmail.com", "anastasiia.shershnova@gmail.com", "kupko.olesya@gmail.com", "margaritagabeeva@gmail.com", "yulia.yachmenova@yahoo.com", "drevniak1998@gmail.com", "alina.kardash23@gmail.com", "natasha.farion@gmail.com", "urievna1988@ukr.net", "grodairina@gmail.com", "yana.olijnik@gmail.com", "marina.stepanenko96@gmail.com", "success7447@gmail.com", "kostyk.lara17@gmail.com", "straxovanieua@gmail.com", "hanna.rokun@gmail.com", "vtsyban@gmail.com", "natalia.ivashchenko@gmail.com", "olenapanasuk63@gmail.com", "elenapetrovskamay@gmail.com", "zhenia0519@gmail.com", "9996ok@gmail.com", "ironiya19@gmail.com", "halinkapita482@gmail.com", "npolikha@gmail.com", "vovaoleniuk@gmail.com", "ksyuxa19934@gmail.com", "karina.yarmoliuk@gmail.com", "barska0906@gmail.com", "koleda97@icloud.com", "manina.vicka@gmail.com", "kanonishen2203@gmail.com", "sawka943@gmail.com", "darina.mail19@gmail.com", "elinkaa761@gmail.com", "kontatt@gmail.com", "stefanyukolgad@gmail.com", "gffeex@icloud.com", "vladakd96@icloud.com", "irina.solodovnikova@gmail.com", "baktiayairem@gmail.com", "lizaperepechkina21@gmail.com", "galyavovik@gmail.com", "anna.gladkaya@gmail.com", "mkulitskaya@gmail.com", "irina.perevertun@gmail.com", "ksyushasawyer@gmail.com", "zamyatinka1991@gmail.com", "anastezy_b@ukr.net", "drvanovna18@gmail.com", "vladbkasidorenko@gmail.com", "denys131@gmail.com", "daxno65@gmail.com", "nataserhieieva@gmail.com", "polinavovk01@gmail.com", "tetjana-c@ukr.net", "khrystyna.godis@gmail.com", "tatiana_daskal@ukr.net", "kukharukolya@gmail.com", "matkovskay74@gmail.com", "hellen.babenko@gmail.com", "zjeck@ukr.net", "kolesnykovavladyslava@ukr.net", "julia@ribachenko.com", "ykorovchenko@yahoo.com", "alyona.shabaltun55@gmail.com", "intriligators@gmail.com", "soltanovska@meta.ua", "oleonaa@gmail.com", "tetyana70@outlook.com", "mhertsyk29@gmail.com", "aniella.popovich@gmail.com", "miraclekaterina@gmail.com", "lena.taraday@gmail.com", "ask.germes@gmail.com", "afesenko1005@gmail.com", "imarymay@icloud.com", "shima-nata@i.ua", "house@ericthecup.com", "markcherry31@gmail.com", "antoninakononenko6579@gmail.com", "nborovyk@gmail.com", "tultulemma@gmail.com", "anneta197731@gmail.com", "alexandra_pavlenko@ukr.net", "valeriiahonchar@gmail.com", "mshelingovsksya0503@gmail.com", "g.vikav.13@gmail.com", "deva89.nr@gmail.con", "oksanagv1974@gmail.com", "mkozelska93@gmail.com", "silakova.m@gmail.com", "dianapiano98@gmail.com", "pozigvnik@gmail.com", "oleckakuraksina@gmail.com", "bestiya121180@gmail.com", "albaskelovich@gmail.com", "olgalysytsyna@gmail.com", "irai69229@gmail.com", "annabin2014@gmail.com", "iren.gladyshko@gmail.com", "opushneva080918@gmail.com", "n.u.mokridi@gmail.com", "batkovetsgmbh@icloud.com", "koshovamariia@gmail.com", "mulyarevelinka@gmail.com"]

with open(HTML_FILE, encoding='utf-8') as f:
    html_body = f.read()

def load_log():
    try:
        with open(LOG_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_log(log):
    tmp = LOG_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LOG_FILE)

def should_skip(email, log):
    e = email.lower().strip()
    if e in HARD_SKIP:
        return True
    if set(log.get(e, [])) & SKIP_TAGS:
        return True
    return False

log = load_log()
todo = [e for e in RECIPIENTS if not should_skip(e, log)]
print(f"До відправки: {len(todo)}")

sent = 0
errors = 0

try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
    server.ehlo()
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)

    for email in todo:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f'{FROM_NAME} <{FROM_ADDR}>'
            msg['To'] = email
            msg['Subject'] = SUBJECT
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            server.sendmail(FROM_ADDR, email, msg.as_string())
            # atomic log save
            log = load_log()
            e = email.lower().strip()
            if e not in log:
                log[e] = []
            if TAG not in log[e]:
                log[e].append(TAG)
            save_log(log)
            sent += 1
            time.sleep(1.2)
        except smtplib.SMTPDataError as ex:
            code = ex.smtp_code
            print(f"ЛІМІТ {email}: {ex}")
            if code in (550, 451):
                print("Денний ліміт — зупиняюсь")
                break
        except Exception as ex:
            print(f"ERR {email}: {ex}")
            errors += 1

    server.quit()
except Exception as ex:
    print(f"SMTP connect error: {ex}")

print(f"\nГОТОВО: відправлено {sent}, помилок {errors}")
