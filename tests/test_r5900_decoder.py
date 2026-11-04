import unittest

from tools.r5900_decoder import (
    decode,
    QuadwordMemoryInstruction,
    UnsupportedInstruction,
)


class DecoderTests(unittest.TestCase):
    def test_report_words(self):
        cases = (
            (0x7fb10010, QuadwordMemoryInstruction("SQ", 29, 17, 16)),
            (0x7fb00000, QuadwordMemoryInstruction("SQ", 29, 16, 0)),
            (0x7bb10010, QuadwordMemoryInstruction("LQ", 29, 17, 16)),
            (0x7bb00000, QuadwordMemoryInstruction("LQ", 29, 16, 0)),
        )
        for word, expected in cases:
            with self.subTest(word=word):
                self.assertEqual(decode(word), expected)

    def test_signed_offset(self):
        self.assertEqual(decode(0x7bb1fff0).offset, -16)
        self.assertEqual(decode(0x7bb18000).offset, -32768)
        self.assertEqual(decode(0x7bb17fff).offset, 32767)

    def test_rejects_unsupported_and_invalid(self):
        with self.assertRaises(UnsupportedInstruction):
            decode(0x03e00008)
        for word in (-1, 0x100000000, "7bb10010"):
            with self.subTest(word=word), self.assertRaises(ValueError):
                decode(word)


if __name__ == "__main__":
    unittest.main()
