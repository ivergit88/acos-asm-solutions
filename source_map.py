import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHEAT = ROOT / 'ШПАРГАЛКА.md'


def command(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def sections(data):
    offset = struct.unpack_from('<Q', data, 40)[0]
    size, count, strings = struct.unpack_from('<HHH', data, 58)
    headers = [struct.unpack_from('<IIQQQQIIQQ', data, offset + i * size)
               for i in range(count)]
    names_header = headers[strings]
    names = data[names_header[4]:names_header[4] + names_header[5]]
    return {names[h[0]:].split(b'\0', 1)[0].decode():
            {'address': h[3], 'offset': h[4], 'size': h[5], 'type': h[1]}
            for h in headers}


def read_program(name):
    source = (ROOT / f'{name}.asm').read_text(encoding='utf-8')
    lines = source.splitlines()
    binary = (ROOT / 'build' / name).read_bytes()
    areas = sections(binary)
    text = areas['.text']
    line_sections = {}
    section = None
    for number, line in enumerate(lines, 1):
        match = re.match(r'\s*section\s+(\S+)', line)
        if match:
            section = match[1]
        line_sections[number] = section
    line_by_address = {}
    for line in (ROOT / 'build' / f'{name}.lst').read_text(encoding='utf-8').splitlines():
        match = re.match(r'^\s*(\d+)\s+([0-9A-Fa-f]{8,16})\s+\S+', line)
        if not match:
            continue
        number = int(match[1])
        if line_sections.get(number) != '.text':
            continue
        if not line.rstrip().endswith(lines[number - 1].strip()):
            raise RuntimeError(f'{name}.asm changed; rebuild it first')
        line_by_address[text['address'] + int(match[2], 16)] = number
    rows = []
    disasm = command('objdump', '-d', '-M', 'intel', '--wide', f'build/{name}')
    for line in disasm.splitlines():
        match = re.match(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\s*(\S.*)$', line)
        if not match:
            continue
        address = int(match[1], 16)
        offset = text['offset'] + address - text['address']
        encoded = bytes.fromhex(match[2])
        if binary[offset:offset + len(encoded)] != encoded:
            raise RuntimeError(f'{name}: linked bytes do not match objdump')
        number = line_by_address[address]
        source_instruction = lines[number - 1].split(';', 1)[0].strip()
        rows.append({'line': number, 'source': source_instruction,
                     'hex': encoded.hex(' ').upper(), 'offset': offset,
                     'address': address, 'decoded': match[3]})
    symbols = {}
    for line in command('nm', '-n', f'build/{name}').splitlines():
        value, _, symbol = line.split()
        symbols[symbol] = int(value, 16)
    data_rows = []
    labels = []
    for number, line in enumerate(lines, 1):
        match = re.match(r'^\s*(\w+):\s*(.*?)(?:;.*)?$', line)
        if not match or match[1] not in symbols:
            continue
        label, declaration = match.groups()
        area = areas[line_sections[number]]
        address = symbols[label]
        offset = None if area['type'] == 8 else area['offset'] + address - area['address']
        if not declaration.strip():
            labels.append({'name': label, 'line': number, 'address': address, 'offset': offset})
            continue
        reserve = re.match(r'resb\s+(\d+)', declaration)
        size = int(reserve[1]) if reserve else area['size'] - (address - area['address'])
        data_rows.append({'name': label, 'line': number, 'source': line.split(';', 1)[0].strip(),
                          'section': line_sections[number], 'address': address, 'offset': offset,
                          'size': size, 'hex': '' if offset is None else binary[offset:offset + size].hex(' ').upper()})
    return {'name': name, 'rows': rows, 'data': data_rows, 'labels': labels,
            'sections': areas, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'binary_sha256': hashlib.sha256(binary).hexdigest()}


INTRO = '''# Карта исходников и бинарников

Это карта стандартной сборки трёх ASM-программ. Исходники лежат в корне.
Выполните bash build.sh. Для самостоятельного поиска используйте objdump -d -M intel,
readelf -SW и Hex Editor: Ctrl+G, файловое смещение. Пользовательских команд нет.
Off — позиция в полном ELF, Addr — виртуальный адрес памяти.
Формула: file_offset = section_offset + address - section_address.
Текущий байт-код берётся из скомпонованного ELF, а не из .o.
Decoded Text показывает символы, не инструкции. .bss не содержит байтов в файле.
Подробнее: [README](README.md), [объяснения](docs/explanation.md).

'''


def write_all():
    programs = {name: read_program(name) for name in ['min', 'for', 'double']}
    content = [INTRO]
    summaries = {
        'min': ('Минимум трёх чисел', 'EAX — текущий минимум, EBX — B, ECX — C. Для 7/3/2 ответ 2.'),
        'for': ('Сумма чётных', 'EAX — i, EBX — N, ECX — сумма. Старт 0, шаг 2, выход i>N; N=10 → 30.'),
        'double': ('Ввод, удвоение и вывод', 'read → число=value×10+цифра → ADD EAX,EAX → DIV на 10 → write. 21 → Result: 42.')}
    for name, table in programs.items():
        title, summary = summaries[name]
        text = table['sections']['.text']
        content += [f'## {name}.asm — {title}', '', summary, '',
                    f'`.text`: Off=`0x{text["offset"]:X}`, Addr=`0x{text["address"]:X}`. '
                    'Байты ниже взяты из скомпонованного ELF, включая исправленные адреса LEA.', '',
                    '| Строка | Инструкция в исходнике | HEX в ELF | Смещение файла | Адрес памяти |',
                    '|---:|---|---|---|---|']
        alias = 'sum' if name == 'for' else name
        for row in table['rows']:
            line = row['line']
            content.append(f'| [{line}]({name}.asm#L{line}) | `{row["source"]}` | '
                           f'`{row["hex"]}` | `0x{row["offset"]:X}` | `0x{row["address"]:X}` |')
        if table['data']:
            content += ['', '### Данные и буферы', '',
                        '| Имя / строка | Секция | Адрес в памяти | Смещение в файле | Размер / байты |',
                        '|---|---|---|---|---|']
            for row in table['data']:
                offset = 'Нет: NOBITS' if row['offset'] is None else f'`0x{row["offset"]:X}`'
                description = f'{row["size"]} байт' + (f'; `{row["hex"]}`' if row['hex'] else '')
                content.append(f'| {row["name"]} / [{row["line"]}]({name}.asm#L{row["line"]}) | '
                               f'`{row["section"]}` | `0x{row["address"]:X}` | {offset} | {description} |')
        content += ['', '### Метки', '',
                    '| Метка | Строка | Адрес в памяти | Смещение файла |',
                    '|---|---:|---|---|']
        for label in table['labels']:
            content.append(f'| `{label["name"]}` | {label["line"]} | `0x{label["address"]:X}` | `0x{label["offset"]:X}` |')
        content += ['']
    content += ['## Важные ответы по double', '',
                '- EDX очищается перед каждым DIV: делится EDX:EAX, а предыдущий остаток остаётся в EDX.',
                '- Цифры пишутся справа налево: деление сначала даёт младшую цифру.',
                '- Ноль проходит цикл хотя бы один раз, поэтому печатается 0.',
                '- В .bss нет байтов буфера в файле; адрес загрузки inbuf ищи по LEA RSI.',
                '- Все SYSCALL имеют байты 0F 05; действие выбирает RAX: 0 / 1 / 60.',
                '', 'Шпаргалка обновляется после сборки. Если меняешь константы, код или комментарии, '
                'снова выполни bash build.sh: номера строк и байты должны соответствовать текущим файлам.', '']
    CHEAT.write_text('\n'.join(content), encoding='utf-8')
    (ROOT / 'build' / 'source-map.json').write_text(json.dumps(programs, ensure_ascii=False, indent=2), encoding='utf-8')
    return programs


if __name__ == '__main__':
    write_all()
