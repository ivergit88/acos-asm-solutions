# Источники и сдача

Оригинальный курс: https://github.com/DumDereDum/course.exe
Локальная исходная версия курса: commit 4ee5ab416c34977b97687fca6703cda20e3acba9.
Текущее задание double дополнительно сверено с main 29.10.2026.

- [01-isa: регистры и инструкции](https://github.com/DumDereDum/course.exe/blob/main/lectures/asm/01-isa.html)
- [02-control: условия, циклы и бинарники](https://github.com/DumDereDum/course.exe/blob/main/lectures/asm/02-control.html)
- [03-io: ввод, вывод, пример 21→42](https://github.com/DumDereDum/course.exe/blob/main/lectures/asm/03-io.html)
- [Полное ТЗ double](https://github.com/DumDereDum/course.exe/blob/main/examples/asm/io/README.md)

В прочитанном ТЗ double требуется сдать исходник, вывод для 0/1/7/21/49/99
и отчёт: расположение Result:, блок DIV, входной буфер .bss; бонус — SYSCALL.
Обязательная публикация на GitHub или конкретный канал сдачи там не указан.
Индивидуальные указания преподавателя могут задавать канал сдачи отдельно.
Публичный репозиторий подготовлен по желанию автора решения, публикация сама
по себе не означает сдачу или принятие работы преподавателем.

min изначально обсуждался как задача на два числа; здесь реализовано расширение
до трёх по запросу. for здесь — именно сумма ЧЁТНЫХ 0…N включительно.
Это выбранные варианты решения; не следует утверждать, что все эти детали
дословно сформулированы в официальном README double.
