"""Тесты АЛУ: команда abs и знаковые константы."""

import unittest
from pathlib import Path

from uvm.assembler import AsmError, parse_program
from uvm.decoder import decode_instruction
from uvm.encoder import assemble
from uvm.errors import VmError
from uvm.vm import Machine

EXAMPLES = Path(__file__).parent.parent / "examples"
LOAD_MAX = 131071
LOAD_MIN = -131072


def run_source(text: str) -> Machine:
    """Ассемблирует текст программы и выполняет её на новой УВМ."""
    machine = Machine(assemble(parse_program(text)))
    machine.run()
    return machine


def abs_result(value: int) -> int:
    """Кладёт value в память, применяет abs и возвращает регистр."""
    machine = run_source(
        f"load,1,{value}\nwrite,0,1,30\nabs,30,2"
    )
    return machine.registers[2]


class AbsTest(unittest.TestCase):
    """Выполнение команды abs."""

    def test_negative(self):
        """abs отрицательного числа."""
        self.assertEqual(abs_result(-7), 7)

    def test_positive(self):
        """abs положительного числа не меняет его."""
        self.assertEqual(abs_result(25), 25)

    def test_zero(self):
        """abs нуля."""
        self.assertEqual(abs_result(0), 0)

    def test_bounds(self):
        """Граничные значения знаковой константы."""
        self.assertEqual(abs_result(LOAD_MIN), -LOAD_MIN)
        self.assertEqual(abs_result(LOAD_MAX), LOAD_MAX)

    def test_address_out_of_memory(self):
        """Адрес B за пределами памяти данных."""
        with self.assertRaises(VmError):
            run_source("abs,70000,1")

    def test_spec_bytes(self):
        """Декодирование abs из теста спецификации."""
        code = bytes([0x29, 0x66, 0x00, 0x00, 0xC0, 0x02])
        instr = decode_instruction(code, 0)
        self.assertEqual(instr.fields, {"A": 9, "B": 817, "C": 22})

    def test_demo_program(self):
        """Демонстрационная программа записывает модули чисел."""
        text = (EXAMPLES / "abs_demo.csv").read_text(encoding="utf-8")
        machine = run_source(text)
        self.assertEqual(machine.data[30:33], [-7, 25, -1000])
        self.assertEqual(machine.data[40:43], [7, 25, 1000])


class SignedConstantTest(unittest.TestCase):
    """Знаковая константа команды load."""

    def test_roundtrip(self):
        """Отрицательная константа кодируется и декодируется."""
        data = assemble(parse_program("load,1,-5"))
        self.assertEqual(decode_instruction(data, 0).fields["C"], -5)

    def test_out_of_range(self):
        """Константа вне знакового диапазона отвергается."""
        for value in (LOAD_MAX + 1, LOAD_MIN - 1):
            with self.subTest(value=value):
                with self.assertRaises(AsmError):
                    parse_program(f"load,1,{value}")


if __name__ == "__main__":
    unittest.main()
