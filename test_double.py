"""Run from Ubuntu/WSL: python3 -m unittest test_double.py."""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class DoubleHomework(unittest.TestCase):
    def test_all_inputs_0_to_99(self):
        with tempfile.TemporaryDirectory() as folder:
            obj = Path(folder) / 'double.o'
            exe = Path(folder) / 'double'
            subprocess.run(['nasm', '-f', 'elf64', str(ROOT / 'double.asm'),
                            '-o', str(obj)], check=True, capture_output=True)
            subprocess.run(['ld', '-o', str(exe), str(obj)],
                           check=True, capture_output=True)
            for value in range(100):
                with self.subTest(value=value):
                    result = subprocess.run([str(exe)], input=f'{value}\n'.encode(),
                                            capture_output=True, timeout=2)
                    self.assertEqual(result.stdout, f'Result: {2 * value}\n'.encode())
                    self.assertEqual(result.stderr, b'')
                    self.assertEqual(result.returncode, 0)
