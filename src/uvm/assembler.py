"""Ассемблер УВМ: разбор CSV-текста во внутреннее представление."""

import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple

from uvm.isa import BY_MNEMONIC, OPCODE_NAME, CommandSpec, Field

COMMENT_PREFIX = "#"
MIN_VALUE = 0
AUTO_BASE = 0


class AsmError(Exception):
    """Ошибка разбора программы на языке ассемблера."""


@dataclass
class Instruction:
    """Команда во внутреннем представлении: спецификация и поля."""

    spec: CommandSpec
    fields: Dict[str, int]


def format_instruction(instr: Instruction) -> str:
    """Возвращает поля команды в виде 'A=29, B=23, C=985'."""
    return ", ".join(f"{k}={v}" for k, v in instr.fields.items())


def value_range(field: Field) -> Tuple[int, int]:
    """Допустимый диапазон значений поля (знаковый или беззнаковый)."""
    if field.signed:
        half = 1 << (field.width - 1)
        return -half, half - 1
    return MIN_VALUE, (1 << field.width) - 1


def parse_operand(field: Field, text: str) -> int:
    """Преобразует текст операнда в число и проверяет диапазон поля."""
    try:
        value = int(text, AUTO_BASE)
    except ValueError:
        raise AsmError(f"'{text}' не является числом") from None
    low, high = value_range(field)
    if not low <= value <= high:
        raise AsmError(
            f"значение {value} вне диапазона поля {field.name} "
            f"({low}..{high})"
        )
    return value


def parse_row(cells: List[str]) -> Instruction:
    """Разбирает одну CSV-строку: мнемоника и операнды."""
    mnemonic, *operands = cells
    spec = BY_MNEMONIC.get(mnemonic.lower())
    if spec is None:
        raise AsmError(f"неизвестная команда '{mnemonic}'")
    if len(operands) != len(spec.operands):
        raise AsmError(
            f"команда {spec.mnemonic} ожидает операндов: "
            f"{len(spec.operands)}, получено: {len(operands)}"
        )
    fields = {OPCODE_NAME: spec.opcode}
    for field, text in zip(spec.operands, operands):
        fields[field.name] = parse_operand(field, text)
    return Instruction(spec, fields)


def is_skipped(cells: List[str]) -> bool:
    """Пустые строки и строки-комментарии пропускаются."""
    return not cells or cells[0].startswith(COMMENT_PREFIX)


def parse_program(text: str) -> List[Instruction]:
    """Преобразует CSV-текст программы в список команд."""
    reader = csv.reader(text.splitlines(), skipinitialspace=True)
    program = []
    for row in reader:
        cells = [cell.strip() for cell in row]
        if is_skipped(cells):
            continue
        try:
            program.append(parse_row(cells))
        except AsmError as err:
            raise AsmError(f"строка {reader.line_num}: {err}") from None
    return program
