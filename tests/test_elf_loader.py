import struct
import unittest

from tools.elf_loader import load_elf


def make_elf(segments):
    """segments: (address, file bytes, memory size)."""
    ident = b'\x7fELF\x01\x01\x01' + bytes(9)
    header = ident + struct.pack('<HHIIIIIHHHHHH', 2, 8, 1, 4, 52, 0, 0,
                                 52, 32, len(segments), 0, 0, 0)
    offset = 52 + 32 * len(segments)
    table, payload = bytearray(), bytearray()
    for addr, content, memsize in segments:
        table += struct.pack('<8I', 1, offset, addr, addr, len(content), memsize, 0, 1)
        payload += content
        offset += len(content)
    return header + table + payload


class ElfLoaderTests(unittest.TestCase):
    def test_bss_overlap_preserves_file_data_in_both_orders(self):
        a = (8, b'ABCD', 4)
        b = (4, b'', 12)
        for segments in ((a, b), (b, a)):
            with self.subTest(segments=segments):
                elf = load_elf(make_elf(segments), 32)
                self.assertEqual(elf.entry, 4)
                self.assertEqual(elf.ram[4:16], b'\0' * 4 + b'ABCD' + b'\0' * 4)

    def test_overlapping_file_data_last_segment_wins(self):
        elf = load_elf(make_elf([(4, b'ABCD', 8), (6, b'xy', 2)]), 16)
        self.assertEqual(elf.ram[4:12], b'ABxy\0\0\0\0')

    def test_rejects_invalid_segments_and_truncation(self):
        for data in (make_elf([(4, b'ABCD', 2)]),
                     make_elf([(31, b'', 2)]),
                     make_elf([(0, b'1234', 4)])[:-1],
                     make_elf([])[:30]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                load_elf(data, 32)


if __name__ == '__main__':
    unittest.main()
