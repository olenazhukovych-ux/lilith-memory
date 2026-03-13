#!/usr/bin/env python3
"""Prepare clean send lists for March 25 campaign. No duplicates across accounts."""
import csv, re, os

EMAIL_RE = re.compile(r'[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}', re.I)

# 1. Load all CRM emails
crm_emails = set()
with open('crm-base.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row and row[0]:
            m = EMAIL_RE.search(row[0].lower().strip())
            if m:
                crm_emails.add(m.group())

print(f"CRM унікальних email: {len(crm_emails)}")

# 2. Load all previously sent emails (from ALL logs)
sent_emails = set()
log_files = [
    'sent_all_25feb_01mar.txt',
    'sent_log_02_03_support.txt', 'sent_log_02_03_iryna.txt',
    'sent_log_03_03.txt', 'sent_log_03_03_wave1.txt',
    'sent_log_04_03_wave1.txt', 'sent_log_05_03_wave1.txt'
]
for lf in log_files:
    if os.path.exists(lf):
        with open(lf, 'r') as f:
            for line in f:
                for m in EMAIL_RE.finditer(line.lower()):
                    sent_emails.add(m.group())

print(f"Раніше відправлено (унікальних): {len(sent_emails)}")

# 3. Load unsubscribed
unsub = set()
if os.path.exists('unsubscribed.txt'):
    with open('unsubscribed.txt') as f:
        for line in f:
            line = line.strip().lower()
            if line and '@' in line:
                unsub.add(line)

# Add known do-not-contact
unsub.add('nadezhdarozhko@icloud.com')
unsub.add('olena.zhukovych@gmail.com')  # test email

print(f"Відписки + не контактувати: {len(unsub)}")

# 4. Split: NEW (never received) vs REPEAT (already received before)
new_emails = crm_emails - sent_emails - unsub
repeat_emails = (crm_emails & sent_emails) - unsub

print(f"\nНОВІ (ще не отримували жодного листа): {len(new_emails)}")
print(f"ПОВТОРНІ (вже отримували раніше): {len(repeat_emails)}")
print(f"Виключено (відписки): {len(crm_emails & unsub)}")

# 5. Split new emails into 4 equal parts (one per SMTP account)
new_list = sorted(new_emails)
chunk_size = len(new_list) // 4
chunks = {
    'support': new_list[0:chunk_size],
    'iryna': new_list[chunk_size:chunk_size*2],
    'gastro': new_list[chunk_size*2:chunk_size*3],
    'olya': new_list[chunk_size*3:]
}

# Verify no overlaps
all_assigned = set()
for name, emails in chunks.items():
    overlap = all_assigned & set(emails)
    if overlap:
        print(f"⚠️ ДУБЛІ в {name}: {len(overlap)}")
    all_assigned.update(emails)
    with open(f'send_new_{name}.txt', 'w') as f:
        for e in emails:
            f.write(e + '\n')
    print(f"  {name}: {len(emails)} email → send_new_{name}.txt")

# 6. Split repeat emails into 4 equal parts
repeat_list = sorted(repeat_emails)
r_chunk = len(repeat_list) // 4
r_chunks = {
    'support': repeat_list[0:r_chunk],
    'iryna': repeat_list[r_chunk:r_chunk*2],
    'gastro': repeat_list[r_chunk*2:r_chunk*3],
    'olya': repeat_list[r_chunk*3:]
}

for name, emails in r_chunks.items():
    with open(f'send_repeat_{name}.txt', 'w') as f:
        for e in emails:
            f.write(e + '\n')
    print(f"  {name} (repeat): {len(emails)} email → send_repeat_{name}.txt")

# 7. Final check - absolutely no duplicates across all files
all_new = set()
all_repeat = set()
for name in ['support', 'iryna', 'gastro', 'olya']:
    with open(f'send_new_{name}.txt') as f:
        emails = {l.strip() for l in f if l.strip()}
    all_new.update(emails)
    with open(f'send_repeat_{name}.txt') as f:
        emails = {l.strip() for l in f if l.strip()}
    all_repeat.update(emails)

cross_overlap = all_new & all_repeat
print(f"\n✅ Перевірка дублів між НОВИМИ списками: {len(all_new)} (має = {len(new_emails)})")
print(f"✅ Перевірка дублів між ПОВТОРНИМИ списками: {len(all_repeat)} (має = {len(repeat_emails)})")
print(f"✅ Перетин нових і повторних: {len(cross_overlap)} (має бути 0)")
print(f"\nЗАГАЛОМ до розсилки: {len(all_new) + len(all_repeat)} email")
