import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Arithmetic(unittest.TestCase):
    def execute(self, name, definitions, expected):
        with tempfile.TemporaryDirectory() as directory:
            obj, exe = Path(directory) / 'task.o', Path(directory) / 'task'
            subprocess.run(['nasm', '-f', 'elf64', *definitions,
                            str(ROOT / f'{name}.asm'), '-o', str(obj)],
                           check=True, capture_output=True)
            subprocess.run(['ld', '-o', str(exe), str(obj)], check=True, capture_output=True)
            result = subprocess.run([str(exe)], capture_output=True, timeout=2)
            self.assertEqual(result.returncode, expected & 255)
            self.assertEqual(result.stdout, b'')
            self.assertEqual(result.stderr, b'')

    def test_minimum_branches_equal_and_signed_boundaries(self):
        for values in [(7, 3, 2), (1, 3, 2), (3, 1, 2), (2, 3, 1),
                       (4, 4, 4), (-1, 0, 1), (0, -7, 2), (0, 2, -7),
                       (-2147483648, 2147483647, 0), (2147483647,) * 3]:
            with self.subTest(values=values):
                self.execute('min', [f'-D{k}={v}' for k, v in zip('ABC', values)], min(values))

    def test_even_sum_boundaries_and_exit_truncation(self):
        for n in [0, 1, 2, 8, 9, 10, 32, 65534]:
            with self.subTest(n=n):
                self.execute('for', [f'-DN={n}'], (n // 2) * (n // 2 + 1))

    def test_invalid_sum_bounds_are_rejected_by_assembler(self):
        with tempfile.TemporaryDirectory() as directory:
            for n in [-1, 65535]:
                result = subprocess.run(['nasm', '-f', 'elf64', f'-DN={n}',
                                         str(ROOT / 'for.asm'), '-o', str(Path(directory) / 'bad.o')],
                                        capture_output=True)
                self.assertNotEqual(result.returncode, 0)
