"""Генератор программ УВМ: abs() над вектором из 8 элементов.

Исходный вектор записывается по адресам SOURCE_BASE.., а результат
abs() над каждым элементом - в новый вектор по адресам RESULT_BASE..
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

VECTOR_LENGTH = 8
SOURCE_BASE = 10
RESULT_BASE = 20
ZERO_REGISTER = 0
VALUE_REGISTER = 1
RESULT_REGISTER = 2


def build_program(values: List[int]) -> List[str]:
    """Возвращает строки CSV-программы для заданного вектора."""
    zero, value, result = ZERO_REGISTER, VALUE_REGISTER, RESULT_REGISTER
    lines = [
        f"# Вектор из {len(values)} чисел по адресам {SOURCE_BASE}..",
        f"# abs() каждого элемента -> новый вектор по адресам {RESULT_BASE}..",
        f"load,{zero},0",
    ]
    for index, number in enumerate(values):
        lines.append(f"load,{value},{number}")
        lines.append(f"write,{zero},{value},{SOURCE_BASE + index}")
    for index in range(len(values)):
        lines.append(f"abs,{SOURCE_BASE + index},{result}")
        lines.append(f"write,{zero},{result},{RESULT_BASE + index}")
    return lines


def build_parser() -> argparse.ArgumentParser:
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Генератор программы abs() над вектором для УВМ"
    )
    parser.add_argument("output", help="путь к CSV-файлу программы")
    parser.add_argument(
        "values", type=int, nargs=VECTOR_LENGTH, help="элементы вектора"
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа: записывает сгенерированную программу в файл."""
    args = build_parser().parse_args(argv)
    text = "\n".join(build_program(args.values)) + "\n"
    Path(args.output).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
