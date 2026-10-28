import unittest
import source_map


class SourceMap(unittest.TestCase):
    def test_linked_bytes_and_line_numbers(self):
        table = source_map.read_program('min')
        row = next(row for row in table['rows'] if row['line'] == 21)
        self.assertEqual(row['source'], 'cmp eax, ebx')
        self.assertEqual(row['offset'], 0x100f)
        self.assertEqual(row['hex'], '39 D8')

    def test_relocations_are_read_from_final_elf(self):
        table = source_map.read_program('double')
        row = next(row for row in table['rows'] if row['line'] == 18)
        self.assertEqual(row['offset'], 0x1004)
        self.assertEqual(row['hex'], '48 8D 35 FD 1F 00 00')

    def test_bss_is_not_mapped_to_file_bytes(self):
        table = source_map.read_program('double')
        row = next(row for row in table['data'] if row['name'] == 'inbuf')
        self.assertIsNone(row['offset'])
        self.assertEqual(row['address'], 0x403008)
        self.assertEqual(row['size'], 32)

    def test_instruction_bytes_match_elf(self):
        for name in ['min', 'for', 'double']:
            table = source_map.read_program(name)
            binary = (source_map.ROOT / 'build' / name).read_bytes()
            for row in table['rows']:
                encoded = bytes.fromhex(row['hex'])
                self.assertEqual(binary[row['offset']:row['offset'] + len(encoded)], encoded)
