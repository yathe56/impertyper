import asyncio
import random
import os
import io
import qrcode
from telethon import TelegramClient, events, errors

api_id = int(os.environ.get("TG_API_ID", 123456))
api_hash = os.environ.get("TG_API_HASH", "your_api_hash")

DEFAULT_DELAY_MIN = 10
DEFAULT_DELAY_MAX = 15

LATIN_LOOKALIKE = {
    'а': ['a'], 'А': ['A'], 'в': ['B'], 'В': ['B'], 'е': ['e'], 'Е': ['E'], 'к': ['k'], 'К': ['K'],
    'м': ['m'], 'М': ['M'], 'н': ['H'], 'Н': ['H'], 'о': ['o'], 'О': ['O'], 'р': ['p'], 'Р': ['P'],
    'с': ['c', 's'], 'С': ['C', 'S'], 'т': ['T'], 'Т': ['T'], 'у': ['y'], 'У': ['Y'], 'х': ['x'], 'Х': ['X'],
    'ш': ['W'], 'Ш': ['W'], 'ь': ['b'], 'Ь': ['b'], 'г': ['r'], 'Г': ['R'], 'д': ['d'], 'Д': ['D'],
    'л': ['l'], 'Л': ['L'], 'п': ['n'], 'П': ['N'], 'ф': ['f'], 'Ф': ['F'], 'ц': ['u'], 'Ц': ['U'],
    'ч': ['4'], 'Ч': ['4'], 'я': ['R'], 'Я': ['R'],
}

ZAGLO_MAP = {
    'а': ['ä', 'á', 'à', 'â', 'α', 'å', 'ã'], 'А': ['Ä', 'Á', 'À', 'Â', 'Α', 'Å', 'Ã'],
    'б': ['ƀ', 'ҍ', 'þ', 'ɓ'], 'Б': ['Ɓ', 'Ҍ', 'Þ', 'Ƃ'], 'в': ['в', 'ѵ', 'β', 'ʙ'], 'В': ['В', 'Ѵ', 'Β', 'ʙ'],
    'г': ['г', 'ğ', 'ǵ', 'ɠ'], 'Г': ['Г', 'Ğ', 'Ǵ', 'Ɠ'], 'д': ['д', 'đ', 'ď', 'δ'], 'Д': ['Д', 'Đ', 'Ď', 'Δ'],
    'е': ['ё', 'é', 'è', 'ë', 'ê', 'ε', 'е'], 'Е': ['Ё', 'É', 'È', 'Ë', 'Ê', 'Ε', 'Е'],
    'ё': ['е', 'ë', 'é', 'è', 'ê'], 'Ё': ['Е', 'Ë', 'É', 'È', 'Ê'], 'ж': ['ж', 'ž', 'ƶ', 'ĵ'], 'Ж': ['Ж', 'Ž', 'Ƶ', 'Ĵ'],
    'з': ['з', 'ž', 'ź', 'ƶ', 'ʒ'], 'З': ['З', 'Ž', 'Ź', 'Ƶ', 'Ʒ'], 'и': ['и', 'í', 'ì', 'î', 'ï', 'ι', 'u'], 'И': ['И', 'Í', 'Ì', 'Î', 'Ï', 'Ι', 'U'],
    'й': ['й', 'ý', 'ÿ', 'ĵ', 'j'], 'Й': ['Й', 'Ý', 'Ÿ', 'Ĵ', 'J'], 'к': ['к', 'κ', 'ķ', 'ƙ', 'k'], 'К': ['К', 'Κ', 'Ķ', 'Ƙ', 'K'],
    'л': ['л', 'λ', 'ľ', 'ł'], 'Л': ['Л', 'Λ', 'Ľ', 'Ł'], 'м': ['м', 'ṃ', 'm'], 'М': ['М', 'Ṃ', 'M'],
    'н': ['н', 'ñ', 'ń', 'η', 'h'], 'Н': ['Н', 'Ñ', 'Ń', 'Η', 'H'], 'о': ['ø', 'ö', 'ó', 'ò', 'ô', 'õ', 'ѳ', 'σ', 'ο'], 'О': ['Ø', 'Ö', 'Ó', 'Ò', 'Ô', 'Õ', 'Ѳ', 'Σ', 'Ο'],
    'п': ['п', 'π', 'þ', 'p'], 'П': ['П', 'Π', 'Þ', 'P'], 'р': ['р', 'ρ', 'ř', 'ŕ', 'p'], 'Р': ['Р', 'Ρ', 'Ř', 'Ŕ', 'P'],
    'с': ['с', 'ş', 'ś', 'š', 'ς', 'c'], 'С': ['С', 'Ş', 'Ś', 'Š', 'Σ', 'C'], 'т': ['т', 'τ', 'ť', 'ţ', 't'], 'Т': ['Т', 'Τ', 'Ť', 'Ţ', 'T'],
    'у': ['у', 'ü', 'ú', 'ù', 'û', 'υ', 'y'], 'У': ['У', 'Ü', 'Ú', 'Ù', 'Û', 'Υ', 'Y'], 'ф': ['ф', 'φ', 'ƒ', 'f'], 'Ф': ['Ф', 'Φ', 'Ƒ', 'F'],
    'х': ['х', 'χ', '×', 'x'], 'Х': ['Х', 'Χ', '×', 'X'], 'ц': ['ц', 'ç', 'ć', 'c'], 'Ц': ['Ц', 'Ç', 'Ć', 'C'],
    'ч': ['ч', 'č', 'ç', 'ĉ'], 'Ч': ['Ч', 'Č', 'Ç', 'Ĉ'], 'ш': ['ш', 'š', 'ş', 'ω'], 'Ш': ['Ш', 'Š', 'Ş', 'Ω'],
    'щ': ['щ', 'ŝ', 'ş', 'ω'], 'Щ': ['Щ', 'Ŝ', 'Ş', 'Ω'], 'ъ': ['ъ', 'ʺ', 'ˮ'], 'Ъ': ['Ъ', 'ʺ', 'ˮ'],
    'ы': ['ы', 'ý', 'ÿ', 'y'], 'Ы': ['Ы', 'Ý', 'Ÿ', 'Y'], 'ь': ['ь', 'ʹ', 'ʼ'], 'Ь': ['Ь', 'ʹ', 'ʼ'],
    'э': ['э', 'é', 'è', 'ë', 'ε', 'e'], 'Э': ['Э', 'É', 'È', 'Ë', 'Ε', 'E'], 'ю': ['ю', 'ü', 'ú', 'û', 'yu'], 'Ю': ['Ю', 'Ü', 'Ú', 'Û', 'Yu'],
    'я': ['я', 'ý', 'ÿ', 'ya'], 'Я': ['Я', 'Ý', 'Ÿ', 'Ya'],
}

if os.path.exists('/data'):
    session_file = '/data/my_session'
else:
    session_file = 'my_session'

client = TelegramClient(session_file, api_id, api_hash)

POSTING_ENABLED = False
ACTIVE_TARGETS = []
ST_CHAT_ID = None
ST_MESSAGE_ID = None
CURRENT_DELAY = None
_suffix_queue = []

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
        print("Файл prefix.txt не найден!")
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
        print("Файл suffix.txt не найден!")
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

HELP_TEXT = """Команды бота

.help - это меню
.st @user1 45 - запустить с задержкой 45 сек
.st @user1 - запустить с задержкой по умолчанию (10-15 сек)
(Команду .st отправляй реплаем на сообщение оппонента)
.sp - остановить цикл
.ss - показать статус"""

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
async def cmd_help(event):
    await event.edit(HELP_TEXT)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.st(?:\s+(.*))?$'))
async def cmd_start(event):
    global POSTING_ENABLED, ACTIVE_TARGETS, ST_CHAT_ID, ST_MESSAGE_ID, CURRENT_DELAY
    raw = event.pattern_match.group(1)
    
    targets = []
    timer_val = None
    
    if raw:
        parts = raw.split()
        for p in parts:
            if p.startswith('@'):
                targets.append(p)
            elif p.lstrip('-').isdigit():
                if p.startswith('-') or len(p) > 6:
                    uid = int(p)
                    try:
                        user = await client.get_entity(uid)
                        name = user.first_name or user.username or str(uid)
                        targets.append(f"[{name}](tg://user?id={uid})")
                    except Exception:
                        targets.append(f"[{uid}](tg://user?id={uid})")
                else:
                    timer_val = int(p)
    
    if not targets:
        await event.edit("Укажи цели: .st @user1 или .st @user1 45")
        return

    ACTIVE_TARGETS = targets
    ST_CHAT_ID = event.chat_id
    
    if timer_val:
        CURRENT_DELAY = timer_val
        delay_msg = f"{timer_val} сек."
    else:
        CURRENT_DELAY = None
        delay_msg = "по умолчанию (10-15 сек)"

    reply_msg = await event.get_reply_message()
    if reply_msg:
        ST_MESSAGE_ID = reply_msg.id
        target_info = "на сообщение оппонента"
    else:
        ST_MESSAGE_ID = event.message.id
        target_info = "на твою команду"

    POSTING_ENABLED = True
    lines = "\n".join(f"{i+1}. {t}" for i, t in enumerate(targets))
    await event.edit(f"Цели ({len(targets)}):\n{lines}\n\nЗадержка: {delay_msg}\nБот отвечает {target_info}.")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.sp$'))
async def cmd_stop(event):
    global POSTING_ENABLED
    POSTING_ENABLED = False
    await event.edit("Цикл отправки остановлен.")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ss$'))
async def cmd_status(event):
    delay_str = f"{CURRENT_DELAY} сек." if CURRENT_DELAY else f"по умолчанию ({DEFAULT_DELAY_MIN}-{DEFAULT_DELAY_MAX} сек.)"
    text = (
        f"Статус\n"
        f"Отправка: {'вкл' if POSTING_ENABLED else 'выкл'}\n"
        f"Задержка: {delay_str}\n"
        f"Цели ({len(ACTIVE_TARGETS)}): {', '.join(ACTIVE_TARGETS) if ACTIVE_TARGETS else 'нет'}"
    )
    await event.edit(text)

async def main():
    print("Подключение к Telegram...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Сессия не найдена. Запрашиваю QR-код...")
        qr = await client.qr_login()
        
        qr_obj = qrcode.QRCode(border=1)
        qr_obj.add_data(qr.url)
        qr_obj.make(fit=True)
        f = io.StringIO()
        qr_obj.print_ascii(out=f, invert=True)
        print(f.getvalue())
        
        print(f"\nИЛИ ОТКРОЙ ЭТУ ССЫЛКУ НА ТЕЛЕФОНЕ:\n{qr.url}")
        print("\nTelegram -> Настройки -> Устройства -> Подключить устройство")
        
        try:
            await qr.wait(timeout=120)
            print("Вход выполнен успешно!")
        except asyncio.TimeoutError:
            print("QR истек, перезапустите бота.")
            return
            
    print("Юзербот запущен. Напиши .help в любой чат.")
    
    while True:
        try:
            if not POSTING_ENABLED or not ACTIVE_TARGETS or ST_CHAT_ID is None:
                await asyncio.sleep(1)
                continue
                
            left = next_prefix(len(ACTIVE_TARGETS))
            right = next_suffix()
            
            if left is None or right is None:
                print("Ожидание: нет фраз в prefix.txt или suffix.txt")
                await asyncio.sleep(5)
                continue
                
            text = build_message(inject(left), inject(right), ACTIVE_TARGETS)
            
            await client.send_message(ST_CHAT_ID, text, reply_to=ST_MESSAGE_ID)
            print(f"Отправлено (задержка: {CURRENT_DELAY or 'дефолт'}): {text[:60]}...")
            
            if CURRENT_DELAY:
                await asyncio.sleep(CURRENT_DELAY)
            else:
                await asyncio.sleep(random.uniform(DEFAULT_DELAY_MIN, DEFAULT_DELAY_MAX))
                
        except errors.FloodWaitError as e:
            print(f"FloodWait: ждём {e.seconds} сек.")
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            print(f"Ошибка цикла: {e}. Перезапуск через 30 сек.")
            await asyncio.sleep(30)

if __name__ == '__main__':
    while True:
        try:
            with client:
                client.loop.run_until_complete(main())
                client.run_until_disconnected()
        except Exception as e:
            print(f"Критическая ошибка: {e}. Перезапуск через 60 сек.")
            import time
            time.sleep(60)
