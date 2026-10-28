# АКОС: три работы на NASM x86-64

Самостоятельно собираемые решения по материалам [DumDereDum/course.exe](https://github.com/DumDereDum/course.exe).
Платформа: **Linux x86-64**, NASM, GNU binutils. Подходит Ubuntu и WSL2 Ubuntu.

| Файл | Задача | Результат по умолчанию |
|---|---|---|
| [min.asm](min.asm) | Минимум трёх знаковых 32-битных чисел | 7, 3, 2 → статус 2 |
| [for.asm](for.asm) | Сумма чётных от 0 до N включительно | N=10 → статус 30 |
| [double.asm](double.asm) | Ввод 0…99, удвоение, печать | 21 → `Result: 42` |

## Установка и проверка

Команды выполняются в Bash внутри Linux/WSL, из корня клона:

```bash
sudo apt-get update
sudo apt-get install -y nasm binutils python3
bash build.sh
python3 -m unittest discover -v
```

Проект не зависит от Python-пакетов, графических редакторов или локальных расширений.
Python нужен только для тестов и генерации карты байтов; вычисления выполняют ASM-программы.

## Запуск без обёрток

```bash
./build/min
echo $?           # 2
./build/for
echo $?           # 30
./build/double    # ввести 21 и Enter; вывод Result: 42
```

`echo $?` выполняется сразу после программы. Min и for **не печатают ответ**:
они передают его через exit, оболочка видит только младшие восемь бит.
Например, N=32 даёт сумму 272, но статус 16. У double ответ — текст,
а статус успешного завершения равен 0.

Параметры min/for задаются при сборке, не читаются с клавиатуры:

```bash
nasm -f elf64 -DA=9 -DB=4 -DC=6 min.asm -o build/min.o
ld -o build/min build/min.o
./build/min
echo $?           # 4
nasm -f elf64 -DN=8 for.asm -o build/for.o
ld -o build/for build/for.o
./build/for
echo $?           # 20
```

Для возврата к стандартным значениям: `bash build.sh`.

## Навигация

- [Контекст и правила для облачного агента](AGENTS.md).
- [Происхождение заданий и требования к сдаче](docs/assignment.md).
- [Алгоритмы, регистры и машинное кодирование](docs/explanation.md).
- [Полная карта строк, байтов и смещений](ШПАРГАЛКА.md).
- [Отчёт по double](docs/double-report.md) и [шесть прогонов](docs/samples.txt).
- [Эталонные ELF, листинги, дизассемблирование и SHA-256](reference/).

## Самостоятельный разбор бинарника

```bash
objdump -d -M intel build/double
readelf -SW build/double
nm -n build/double
od -Ax -tx1 -j 0x1028 -N 3 build/double
```

Последняя команда для стандартной сборки показывает `83 f9 30` — `cmp ecx, '0'`.
Objdump показывает адрес памяти, Hex Editor/od — файловое смещение.
Формула: `file_offset = section_offset + instruction_address - section_address`.
В эталонной сборке `.text`: адрес 0x401000, файловое смещение 0x1000.
Смещения зависят от исходника и компоновки: для изменённой сборки проверяйте их заново.

`reference/` — версия стандартной сборки NASM 2.16.01 / GNU ld 2.42.
Обычная сборка пишет в игнорируемый `build/`. Для осознанного обновления
эталонных файлов: `bash snapshot.sh`; затем повторить тесты и сверить отчёт.
Этот репозиторий содержит решения и пояснения; весь сторонний курс не копируется.
