import struct
import unittest

from tools.elf_loader import load_elf, UnmappedReservation


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

    def test_external_reservation_requires_explicit_opt_in(self):
        data = make_elf([(4, b'ABCD', 8), (0x03000000, b'', 0x800)])
        with self.assertRaises(ValueError):
            load_elf(data, 32)
        elf = load_elf(data, 32, allow_unmapped_reservations=True)
        self.assertEqual(elf.ram[4:12], b'ABCD\0\0\0\0')
        self.assertEqual(elf.unresolved, (UnmappedReservation(1, 0x03000000, 0x800),))

    def test_opt_in_does_not_accept_data_partial_overlap_or_overflow(self):
        for segment in ((32, b'X', 1), (31, b'', 2), (0xfffffff0, b'', 32)):
            with self.subTest(segment=segment), self.assertRaises(ValueError):
                load_elf(make_elf([segment]), 32, allow_unmapped_reservations=True)

    def test_empty_segment_offset_beyond_eof(self):
        data = bytearray(make_elf([(4, b'', 8)]))
        struct.pack_into('<I', data, 56, 0xffffffff)
        self.assertEqual(load_elf(data, 32).ram[4:12], bytes(8))


if __name__ == '__main__':
    unittest.main()
