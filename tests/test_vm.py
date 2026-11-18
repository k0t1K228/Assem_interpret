"""Тесты интерпретатора УВМ: декодер, память, команды, дамп."""

import csv
import tempfile
import unittest
from pathlib import Path

from uvm.assembler import parse_program
from uvm.decoder import decode_instruction
from uvm.encoder import assemble
from uvm.errors import DecodeError, VmError
from uvm.interp_cli import main as interp_main
from uvm.vm import Machine, write_dump

EXAMPLES = Path(__file__).parent.parent / "examples"
SOURCE_VALUES = [11, 22, 33, 44, 55]
SPEC_DECODE = [
    ([0xFD, 0x92, 0x3D, 0x00], {"A": 29, "B": 23, "C": 985}),
    ([0x90, 0xA0, 0xFE, 0x0D], {"A": 16, "B": 4, "C": 490, "D": 111}),
    ([0xA2, 0xB3, 0x48, 0x03], {"A": 2, "B": 29, "C": 11, "D": 105}),
]


def run_source(text: str) -> Machine:
    """Ассемблирует текст программы и выполняет её на новой УВМ."""
    machine = Machine(assemble(parse_program(text)))
    machine.run()
    return machine


class DecoderTest(unittest.TestCase):
    """Декодирование байтов из тестов спецификации."""

    def test_spec_bytes(self):
        """Байты из спецификации дают исходные поля."""
        for data, expected in SPEC_DECODE:
            with self.subTest(data=data):
                instr = decode_instruction(bytes(data), 0)
                self.assertEqual(instr.fields, expected)

    def test_unknown_opcode(self):
        """Неизвестный код операции."""
        with self.assertRaises(DecodeError):
            decode_instruction(bytes([0x1F, 0, 0, 0]), 0)

    def test_truncated(self):
        """Команда обрезана."""
        with self.assertRaises(DecodeError):
            decode_instruction(bytes([0xFD, 0x92]), 0)


class CommandsTest(unittest.TestCase):
    """Выполнение команд загрузки, чтения и записи."""

    def test_load(self):
        """load кладёт константу в регистр."""
        machine = run_source("load,5,300")
        self.assertEqual(machine.registers[5], 300)

    def test_read(self):
        """read берёт значение по адресу регистр + смещение."""
        machine = Machine(assemble(parse_program(
            "load,1,10\nread,1,5,2"
        )))
        machine.data[15] = 77
        machine.run()
        self.assertEqual(machine.registers[2], 77)

    def test_write(self):
        """write кладёт регистр в память по адресу регистр + смещение."""
        machine = run_source("load,1,10\nload,2,99\nwrite,1,2,3")
        self.assertEqual(machine.data[13], 99)

    def test_address_out_of_memory(self):
        """Обращение за пределы памяти данных даёт ошибку."""
        with self.assertRaises(VmError):
            run_source("load,1,70000\nread,1,0,2")

    def test_memories_are_separate(self):
        """Запись в память данных не меняет память команд."""
        source = "load,1,0\nload,2,99\nwrite,1,2,0"
        machine = Machine(assemble(parse_program(source)))
        before = bytes(machine.code)
        machine.run()
        self.assertEqual(machine.code, before)


class CopyArrayTest(unittest.TestCase):
    """Тестовая программа копирования массива."""

    def test_copy(self):
        """Массив 10..14 скопирован на адреса 20..24."""
        text = (EXAMPLES / "copy_array.csv").read_text(encoding="utf-8")
        machine = run_source(text)
        self.assertEqual(machine.data[10:15], SOURCE_VALUES)
        self.assertEqual(machine.data[20:25], SOURCE_VALUES)


class DumpTest(unittest.TestCase):
    """Дамп памяти в CSV и консольное приложение."""

    def test_dump_file(self):
        """Дамп содержит заголовок и строки адрес,значение."""
        machine = Machine(b"")
        machine.data[2] = 5
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "dump.csv"
            write_dump(machine, 1, 3, str(path))
            with open(path, encoding="utf-8", newline="") as file:
                rows = list(csv.reader(file))
        self.assertEqual(
            rows,
            [["address", "value"], ["1", "0"], ["2", "5"], ["3", "0"]],
        )

    def test_bad_range(self):
        """Обратный диапазон адресов отвергается."""
        with self.assertRaises(VmError):
            write_dump(Machine(b""), 5, 1, "unused.csv")

    def test_cli(self):
        """Интерпретатор из командной строки выполняет программу."""
        code = assemble(parse_program("load,1,4\nload,2,9\nwrite,1,2,0"))
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "p.bin"
            dump = Path(tmp) / "d.csv"
            binary.write_bytes(code)
            result = interp_main([str(binary), str(dump), "4", "4"])
            lines = dump.read_text(encoding="utf-8").splitlines()
        self.assertEqual(result, 0)
        self.assertEqual(lines, ["address,value", "4,9"])


if __name__ == "__main__":
    unittest.main()
