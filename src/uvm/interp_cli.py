"""Консольное приложение интерпретатора УВМ."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from uvm.errors import VmError
from uvm.vm import Machine, check_range, write_dump

EXIT_OK = 0
EXIT_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="interp_cli", description="Интерпретатор учебной УВМ"
    )
    parser.add_argument("program", help="путь к двоичному файлу программы")
    parser.add_argument("dump", help="путь к CSV-файлу дампа памяти")
    parser.add_argument("first", type=int, help="первый адрес дампа")
    parser.add_argument(
        "last", type=int, help="последний адрес дампа (включительно)"
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа: выполняет программу и сохраняет дамп памяти."""
    args = build_parser().parse_args(argv)
    try:
        check_range(args.first, args.last)
        machine = Machine(Path(args.program).read_bytes())
        executed = machine.run()
        write_dump(machine, args.first, args.last, args.dump)
    except (OSError, VmError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    print(f"Выполнено команд: {executed}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
