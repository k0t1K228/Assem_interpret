"""Тесты кодирования команд в машинный код."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from uvm.asm_cli import main
from uvm.assembler import parse_program
from uvm.encoder import assemble, format_bytes

SPEC_BYTES = {
    "load,23,985": [0xFD, 0x92, 0x3D, 0x00],
    "read,4,490,111": [0x90, 0xA0, 0xFE, 0x0D],
    "write,29,11,105": [0xA2, 0xB3, 0x48, 0x03],
    "abs,817,22": [0x29, 0x66, 0x00, 0x00, 0xC0, 0x02],
}
EXAMPLE = Path(__file__).parent.parent / "examples" / "spec_tests.csv"


class EncoderTest(unittest.TestCase):
    """Сверка с байтовыми тестами из спецификации."""

    def test_each_command(self):
        """Каждая команда кодируется в ожидаемые байты."""
        for source, expected in SPEC_BYTES.items():
            with self.subTest(source=source):
                data = assemble(parse_program(source))
                self.assertEqual(list(data), expected)

    def test_format_bytes(self):
        """Формат вывода байтов как в спецификации."""
        self.assertEqual(
            format_bytes(bytes([0xFD, 0x92, 0x3D, 0x00])),
            "0xFD, 0x92, 0x3D, 0x00",
        )


class CliTest(unittest.TestCase):
    """Проверка консольного приложения целиком."""

    def test_example_file(self):
        """Файл-пример даёт все тестовые последовательности подряд."""
        expected = b"".join(bytes(v) for v in SPEC_BYTES.values())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nested" / "spec.bin"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main([str(EXAMPLE), str(out), "--test"])
            self.assertEqual(code, 0)
            self.assertEqual(out.read_bytes(), expected)
        self.assertIn(f"{len(expected)} байт", buffer.getvalue())
        self.assertIn("0x29, 0x66, 0x00, 0x00, 0xC0, 0x02", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
