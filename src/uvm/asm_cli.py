"""Консольное приложение ассемблера УВМ."""

import argparse
import sys
from typing import List, Optional

from uvm.assembler import AsmError, format_instruction, parse_program

EXIT_OK = 0
EXIT_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="asm_cli", description="Ассемблер учебной виртуальной машины"
    )
    parser.add_argument("source", help="путь к файлу с программой (CSV)")
    parser.add_argument("output", help="путь к двоичному файлу-результату")
    parser.add_argument(
        "--test", action="store_true", help="режим тестирования"
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа: читает программу, ассемблирует, выводит результат."""
    args = build_parser().parse_args(argv)
    try:
        with open(args.source, encoding="utf-8") as file:
            program = parse_program(file.read())
    except (OSError, AsmError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    if args.test:
        for instr in program:
            print(format_instruction(instr))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
