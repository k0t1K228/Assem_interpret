"""Консольное приложение ассемблера УВМ."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from uvm.assembler import AsmError, Instruction, parse_program
from uvm.encoder import assemble, encode_instruction, format_bytes

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


def load_program(path: str) -> List[Instruction]:
    """Читает файл с программой и разбирает его."""
    with open(path, encoding="utf-8") as file:
        return parse_program(file.read())


def write_binary(path: str, data: bytes) -> None:
    """Записывает машинный код в файл, создавая каталог при нужде."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа: ассемблирует программу и записывает результат."""
    args = build_parser().parse_args(argv)
    try:
        program = load_program(args.source)
        binary = assemble(program)
        write_binary(args.output, binary)
    except (OSError, AsmError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    print(f"Размер двоичного файла: {len(binary)} байт")
    if args.test:
        for instr in program:
            print(format_bytes(encode_instruction(instr)))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
