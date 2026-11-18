"""Тесты тестовой задачи: abs() над вектором длины 8."""

import unittest
from pathlib import Path

from uvm.assembler import parse_program
from uvm.encoder import assemble
from uvm.vm import Machine

EXAMPLES = Path(__file__).parent.parent / "examples"
SOURCE_BASE = 10
RESULT_BASE = 20
VECTOR_LENGTH = 8
EXPECTED = {
    "vector_abs": (
        [-5, 12, -300, 0, 77, -1, 100000, -131072],
        [5, 12, 300, 0, 77, 1, 100000, 131072],
    ),
    "vector_abs_negative": (
        [-10, -20, -30, -40, -50, -60, -70, -80],
        [10, 20, 30, 40, 50, 60, 70, 80],
    ),
    "vector_abs_positive": (
        [3, 0, 14, 15, 92, 65, 35, 89],
        [3, 0, 14, 15, 92, 65, 35, 89],
    ),
    "vector_abs_limits": (
        [131071, -131071, 1, -1, 0, 0, -131072, 99999],
        [131071, 131071, 1, 1, 0, 0, 131072, 99999],
    ),
}


def run_example(name: str) -> Machine:
    """Выполняет программу из examples/<name>.csv."""
    text = (EXAMPLES / f"{name}.csv").read_text(encoding="utf-8")
    machine = Machine(assemble(parse_program(text)))
    machine.run()
    return machine


class VectorAbsTest(unittest.TestCase):
    """Проверка дампа памяти для каждой программы-примера."""

    def test_examples(self):
        """Исходный вектор цел, результат содержит модули элементов."""
        for name, (source, result) in EXPECTED.items():
            with self.subTest(name=name):
                data = run_example(name).data
                end = SOURCE_BASE + VECTOR_LENGTH
                self.assertEqual(data[SOURCE_BASE:end], source)
                end = RESULT_BASE + VECTOR_LENGTH
                self.assertEqual(data[RESULT_BASE:end], result)

    def test_result_is_abs_of_source(self):
        """Результат совпадает с abs() от исходного вектора."""
        for name, (source, _) in EXPECTED.items():
            with self.subTest(name=name):
                data = run_example(name).data
                end = RESULT_BASE + VECTOR_LENGTH
                self.assertEqual(
                    data[RESULT_BASE:end], [abs(x) for x in source]
                )


if __name__ == "__main__":
    unittest.main()
