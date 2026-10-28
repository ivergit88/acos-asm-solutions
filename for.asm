; Складываем чётные числа от 0 до N включительно.
; Это for (i = 0; i <= N; i += 2), в теле которого sum += i.
; При N=10 получаем 0+2+4+6+8+10 = 30.
%ifndef N
    %define N 10
%endif
; Эта проверка выполняется при сборке, а не во время запуска.
%if N < 0 || N > 65534
    %error "N must be in 0..65534"
%endif
bits 64
global _start
section .text
_start:
    mov ebx, N             ; верхняя граница
    mov ecx, 0             ; накопленная сумма
    mov eax, 0             ; текущее чётное число, начинаем с нуля
check:
    cmp eax, ebx           ; сравнить текущее число с N
    jg done                ; выходим только при i > N, поэтому равенство входит в цикл
    add ecx, eax           ; прибавить текущее число к сумме
    add eax, 2             ; перейти к следующему чётному
    jmp check              ; снова проверить границу, не обнуляя счётчик
done:
    mov edi, ecx           ; передать сумму как код завершения
    mov eax, 60            ; системный вызов exit
    syscall
; echo $? показывает младшие 8 бит ответа. Для N=10 все 30 видны целиком.
section .note.GNU-stack noalloc noexec nowrite progbits
