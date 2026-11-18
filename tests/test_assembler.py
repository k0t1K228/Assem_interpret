"""Тесты ассемблера на примерах из спецификации УВМ."""

import unittest

from uvm.assembler import AsmError, format_instruction, parse_program


class SpecExamplesTest(unittest.TestCase):
    """Проверка полей команд из тестов спецификации."""

    def assert_fields(self, source, expected):
        """Ассемблирует одну строку и сравнивает поля."""
        program = parse_program(source)
        self.assertEqual(len(program), 1)
        self.assertEqual(program[0].fields, expected)

    def test_load(self):
        """Загрузка константы: A=29, B=23, C=985."""
        self.assert_fields("load,23,985", {"A": 29, "B": 23, "C": 985})

    def test_read(self):
        """Чтение из памяти: A=16, B=4, C=490, D=111."""
        self.assert_fields(
            "read,4,490,111", {"A": 16, "B": 4, "C": 490, "D": 111}
        )

    def test_write(self):
        """Запись в память: A=2, B=29, C=11, D=105."""
        self.assert_fields(
            "write,29,11,105", {"A": 2, "B": 29, "C": 11, "D": 105}
        )

    def test_abs(self):
        """Унарная операция abs: A=9, B=817, C=22."""
        self.assert_fields("abs,817,22", {"A": 9, "B": 817, "C": 22})

    def test_format(self):
        """Вывод полей в формате спецификации."""
        program = parse_program("load,23,985")
        self.assertEqual(format_instruction(program[0]), "A=29, B=23, C=985")


class ErrorsTest(unittest.TestCase):
    """Проверка диагностики ошибок."""

    def test_unknown_command(self):
        """Неизвестная мнемоника."""
        with self.assertRaises(AsmError):
            parse_program("jump,1")

    def test_wrong_operand_count(self):
        """Неверное число операндов."""
        with self.assertRaises(AsmError):
            parse_program("load,1")

    def test_out_of_range(self):
        """Значение не помещается в поле (B у load — 7 бит)."""
        with self.assertRaises(AsmError):
            parse_program("load,128,1")

    def test_not_a_number(self):
        """Операнд не число."""
        with self.assertRaises(AsmError):
            parse_program("load,x,1")

    def test_comments_and_blank_lines(self):
        """Комментарии и пустые строки пропускаются."""
        self.assertEqual(len(parse_program("# c\n\nload,1,2\n")), 1)


if __name__ == "__main__":
    unittest.main()
