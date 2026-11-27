import asyncio
import random
import time
import os
import io
import qrcode
from telethon import TelegramClient, events, errors

# ============ НАСТРОЙКИ ============
api_id = int(os.environ.get("TG_API_ID", 123456))
api_hash = os.environ.get("TG_API_HASH", "your_api_hash")

print("API_ID загружен:", api_id != 123456)
print("API_HASH загружен:", api_hash != "your_api_hash")

DELAY_MIN, DELAY_MAX = 2, 3
REPLY_DELAY_MIN, REPLY_DELAY_MAX = 2, 3
ZAGLO_IN_NAME = False

LATIN_LOOKALIKE = {
    'а': ['a'], 'А': ['A'], 'в': ['B'], 'В': ['B'],
    'е': ['e'], 'Е': ['E'], 'к': ['k'], 'К': ['K'],
    'м': ['m'], 'М': ['M'], 'н': ['H'], 'Н': ['H'],
    'о': ['o'], 'О': ['O'], 'р': ['p'], 'Р': ['P'],
    'с': ['c', 's'], 'С': ['C', 'S'], 'т': ['T'], 'Т': ['T'],
    'у': ['y'], 'У': ['Y'], 'х': ['x'], 'Х': ['X'],
    'ш': ['W'], 'Ш': ['W'], 'ь': ['b'], 'Ь': ['b'],
    'г': ['r'], 'Г': ['R'], 'д': ['d'], 'Д': ['D'],
    'л': ['l'], 'Л': ['L'], 'п': ['n'], 'П': ['N'],
    'ф': ['f'], 'Ф': ['F'], 'ц': ['u'], 'Ц': ['U'],
    'ч': ['4'], 'Ч': ['4'], 'я': ['R'], 'Я': ['R'],
}

ZAGLO_MAP = {
    'а': ['ä', 'á', 'à', 'â', 'α', 'å', 'ã'],
    'А': ['Ä', 'Á', 'À', 'Â', 'Α', 'Å', 'Ã'],
    'б': ['ƀ', 'ҍ', 'þ', 'ɓ'], 'Б': ['Ɓ', 'Ҍ', 'Þ', 'Ƃ'],
    'в': ['в', 'ѵ', 'β', 'ʙ'], 'В': ['В', 'Ѵ', 'Β', 'ʙ'],
    'г': ['г', 'ğ', 'ǵ', 'ɠ'], 'Г': ['Г', 'Ğ', 'Ǵ', 'Ɠ'],
    'д': ['д', 'đ', 'ď', 'δ'], 'Д': ['Д', 'Đ', 'Ď', 'Δ'],
    'е': ['ё', 'é', 'è', 'ë', 'ê', 'ε', 'е'], 'Е': ['Ё', 'É', 'È', 'Ë', 'Ê', 'Ε', 'Е'],
    'ё': ['е', 'ë', 'é', 'è', 'ê'], 'Ё': ['Е', 'Ë', 'É', 'È', 'Ê'],
    'ж': ['ж', 'ž', 'ƶ', 'ĵ'], 'Ж': ['Ж', 'Ž', 'Ƶ', 'Ĵ'],
    'з': ['з', 'ž', 'ź', 'ƶ', 'ʒ'], 'З': ['З', 'Ž', 'Ź', 'Ƶ', 'Ʒ'],
    'и': ['и', 'í', 'ì', 'î', 'ï', 'ι', 'u'], 'И': ['И', 'Í', 'Ì', 'Î', 'Ï', 'Ι', 'U'],
    'й': ['й', 'ý', 'ÿ', 'ĵ', 'j'], 'Й': ['Й', 'Ý', 'Ÿ', 'Ĵ', 'J'],
    'к': ['к', 'κ', 'ķ', 'ƙ', 'k'], 'К': ['К', 'Κ', 'Ķ', 'Ƙ', 'K'],
    'л': ['л', 'λ', 'ľ', 'ł'], 'Л': ['Л', 'Λ', 'Ľ', 'Ł'],
    'м': ['м', 'ṃ', 'm'], 'М': ['М', 'Ṃ', 'M'],
    'н': ['н', 'ñ', 'ń', 'η', 'h'], 'Н': ['Н', 'Ñ', 'Ń', 'Η', 'H'],
    'о': ['ø', 'ö', 'ó', 'ò', 'ô', 'õ', 'ѳ', 'σ', 'ο'], 'О': ['Ø', 'Ö', 'Ó', 'Ò', 'Ô', 'Õ', 'Ѳ', 'Σ', 'Ο'],
    'п': ['п', 'π', 'þ', 'p'], 'П': ['П', 'Π', 'Þ', 'P'],
    'р': ['р', 'ρ', 'ř', 'ŕ', 'p'], 'Р': ['Р', 'Ρ', 'Ř', 'Ŕ', 'P'],
    'с': ['с', 'ş', 'ś', 'š', 'ς', 'c'], 'С': ['С', 'Ş', 'Ś', 'Š', 'Σ', 'C'],
    'т': ['т', 'τ', 'ť', 'ţ', 't'], 'Т': ['Т', 'Τ', 'Ť', 'Ţ', 'T'],
    'у': ['у', 'ü', 'ú', 'ù', 'û', 'υ', 'y'], 'У': ['У', 'Ü', 'Ú', 'Ù', 'Û', 'Υ', 'Y'],
    'ф': ['ф', 'φ', 'ƒ', 'f'], 'Ф': ['Ф', 'Φ', 'Ƒ', 'F'],
    'х': ['х', 'χ', '×', 'x'], 'Х': ['Х', 'Χ', '×', 'X'],
    'ц': ['ц', 'ç', 'ć', 'c'], 'Ц': ['Ц', 'Ç', 'Ć', 'C'],
    'ч': ['ч', 'č', 'ç', 'ĉ'], 'Ч': ['Ч', 'Č', 'Ç', 'Ĉ'],
    'ш': ['ш', 'š', 'ş', 'ω'], 'Ш': ['Ш', 'Š', 'Ş', 'Ω'],
    'щ': ['щ', 'ŝ', 'ş', 'ω'], 'Щ': ['Щ', 'Ŝ', 'Ş', 'Ω'],
    'ъ': ['ъ', 'ʺ', 'ˮ'], 'Ъ': ['Ъ', 'ʺ', 'ˮ'],
    'ы': ['ы', 'ý', 'ÿ', 'y'], 'Ы': ['Ы', 'Ý', 'Ÿ', 'Y'],
    'ь': ['ь', 'ʹ', 'ʼ'], 'Ь': ['Ь', 'ʹ', 'ʼ'],
    'э': ['э', 'é', 'è', 'ë', 'ε', 'e'], 'Э': ['Э', 'É', 'È', 'Ë', 'Ε', 'E'],
    'ю': ['ю', 'ü', 'ú', 'û', 'yu'], 'Ю': ['Ю', 'Ü', 'Ú', 'Û', 'Yu'],
    'я': ['я', 'ý', 'ÿ', 'ya'], 'Я': ['Я', 'Ý', 'Ÿ', 'Ya'],
}

client = TelegramClient('/data/my_session', api_id, api_hash)

# ============ СОСТОЯНИЕ ============
POSTING_ENABLED = False
AUTO_REPLY_ENABLED = True
ACTIVE_TARGETS = []
ST_CHAT_ID = None
_suffix_queue = []

# ============ ФУНКЦИИ ============

def inject(text):
    chars = list(text)
    zaglo_pos = [i for i, c in enumerate(chars) if c in ZAGLO_MAP]
    random.shuffle(zaglo_pos)
    for pos in zaglo_pos[:random.randint(1, 3)]:
        chars[pos] = random.choice(ZAGLO_MAP[chars[pos]])
    latin_pos = [i for i, c in enumerate(chars) if c in LATIN_LOOKALIKE]
    random.shuffle(latin_pos)
    for pos in latin_pos[:random.randint(1, 4)]:
        chars[pos] = random.choice(LATIN_LOOKALIKE[chars[pos]])
    return ''.join(chars)

def load_prefixes():
    items = []
    try:
        with open('prefix.txt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '|' in line:
                    num, text = line.split('|', 1)
                    items.append((int(num.strip()), text.strip()))
                else:
                    items.append((0, line))
    except FileNotFoundError:
        print("prefix.txt не найден.")
    return items

def load_suffixes():
    items = []
    try:
        with open('suffix.txt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    items.append(line)
    except FileNotFoundError:
        print("suffix.txt не найден.")
    return items

def next_prefix(count):
    items = load_prefixes()
    if not items:
        return None
    exact = [t for n, t in items if n == count]
    if exact:
        return random.choice(exact)
    universal = [t for n, t in items if n == 0]
    if universal:
        return random.choice(universal)
    return random.choice([t for _, t in items])

def next_suffix():
    global _suffix_queue
    if not _suffix_queue:
        items = load_suffixes()
        if not items:
            return None
        _suffix_queue = items[:]
        random.shuffle(_suffix_queue)
    return _suffix_queue.pop(0)

def build_message(left, right, mentions):
    if '...' not in left:
        head = left + ' ' + ' '.join(mentions)
    else:
        parts = left.split('...')
        slots = len(parts) - 1
        result = parts[0]
        idx = 0
        for i in range(slots):
            if i == slots - 1:
                chunk = mentions[idx:]
            else:
                chunk = mentions[idx:idx + max(1, len(mentions) // slots)]
            result += ' '.join(chunk) + parts[i + 1]
            idx += len(chunk)
        head = result
    return f"{head} // {right}".strip()

# ============ QR-ВХОД ============

async def qr_login():
    if await client.is_user_authorized():
        print("Сессия уже есть, вход не нужен.")
        return
    print("Запрашиваю QR-код...")
    qr = await client.qr_login()
    qr_obj = qrcode.QRCode(border=1)
    qr_obj.add_data(qr.url)
    qr_obj.make(fit=True)
    f = io.StringIO()
    qr_obj.print_ascii(out=f, invert=True)
    print(f.getvalue())
    print(f"Или открой ссылку на телефоне: {qr.url}")
    print("Telegram → Настройки → Устройства → Подключить устройство")
    try:
        await qr.wait(timeout=120)
        print("Вход выполнен! Сессия сохранена в /data/my_session.session")
    except asyncio.TimeoutError:
        print("QR истёк. Перезапусти бота, чтобы получить новый.")
        raise

# ============ КОМАНДЫ ============

HELP_TEXT = """📖 **Команды бота**

`.help` — это меню
`.st @user1 123456789` — установить цели и запустить цикл в этом чате
`.sp` — stop posting: остановить цикл
`.ar` — auto reply: вкл/выкл авто-реплай
`.ss` — show status: показать текущие настройки"""

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
async def cmd_help(event):
    await event.edit(HELP_TEXT)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.st(?:\s+(.*))?$'))
async def cmd_start(event):
    global POSTING_ENABLED, ACTIVE_TARGETS, ST_CHAT_ID
    raw = event.pattern_match.group(1)
    if not raw:
        await event.edit("❌ Укажи цели: `.st @user1 123456789`")
        return
    parts = raw.split()
    targets = []
    for p in parts:
        if p.startswith('@'):
            targets.append(p)
        elif p.lstrip('-').isdigit():
            uid = int(p)
            try:
                user = await client.get_entity(uid)
                name = user.first_name or user.username or str(uid)
                targets.append(f"[{name}](tg://user?id={uid})")
            except Exception:
                targets.append(f"[{uid}](tg://user?id={uid})")
        else:
            targets.append(p)
    ACTIVE_TARGETS = targets
    ST_CHAT_ID = event.chat_id
    POSTING_ENABLED = True
    lines = "\n".join(f"{i+1}. {t}" for i, t in enumerate(targets))
    await event.edit(f"▶️ Цели установлены ({len(targets)}):\n{lines}\n\nЦикл запущен в этом чате.")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.sp$'))
async def cmd_stop(event):
    global POSTING_ENABLED
    POSTING_ENABLED = False
    await event.edit("⏸ Цикл отправки остановлен.")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ar$'))
async def cmd_autoreply(event):
    global AUTO_REPLY_ENABLED
    AUTO_REPLY_ENABLED = not AUTO_REPLY_ENABLED
    state = "вкл" if AUTO_REPLY_ENABLED else "выкл"
    await event.edit(f"💬 Авто-реплай: {state}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ss$'))
async def cmd_status(event):
    text = (
        f"📊 **Статус**\n"
        f"Отправка: {'вкл' if POSTING_ENABLED else 'выкл'}\n"
        f"Авто-реплай: {'вкл' if AUTO_REPLY_ENABLED else 'выкл'}\n"
        f"Цели ({len(ACTIVE_TARGETS)}): {', '.join(ACTIVE_TARGETS) if ACTIVE_TARGETS else 'нет'}"
    )
    await event.edit(text)

# ============ АВТО-РЕПЛАЙ ============

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if not AUTO_REPLY_ENABLED:
        return
    try:
        if event.out or (event.sender and getattr(event.sender, 'bot', False)):
            return
        await asyncio.sleep(random.uniform(REPLY_DELAY_MIN, REPLY_DELAY_MAX))
        left = next_prefix(len(ACTIVE_TARGETS))
        right = next_suffix()
        if left is None or right is None:
            return
        text = build_message(inject(left), inject(right), ACTIVE_TARGETS)
        await event.reply(text)
    except errors.FloodWait as e:
        print(f"FloodWait (реплай): {e.value} сек.")
        await asyncio.sleep(e.value * 1.3)
    except Exception as e:
        print(f"Ошибка авто-реплая: {e}")

# ============ ОСНОВНОЙ ЦИКЛ ============

async def main():
    await client.connect()
    await qr_login()
    print("Юзербот запущен. Напиши .help в любой чат.")
    while True:
        try:
            if not POSTING_ENABLED or not ACTIVE_TARGETS or ST_CHAT_ID is None:
                await asyncio.sleep(5)
                continue
            left = next_prefix(len(ACTIVE_TARGETS))
            right = next_suffix()
            if left is None or right is None:
                await asyncio.sleep(60)
                continue
            text = build_message(inject(left), inject(right), ACTIVE_TARGETS)
            await client.send_message(ST_CHAT_ID, text)
            print(f"Отправлено: {text[:80]}")
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        except errors.FloodWait as e:
            wait = e.value * 1.3
            print(f"FloodWait: ждём {wait:.0f} сек.")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"Ошибка цикла: {e}. Перезапуск через 30 сек.")
            await asyncio.sleep(30)

if __name__ == '__main__':
    while True:
        try:
            client.loop.run_until_complete(main())
        except Exception as e:
            print(f"Критическая ошибка: {e}. Перезапуск через 60 сек.")
            time.sleep(60)
