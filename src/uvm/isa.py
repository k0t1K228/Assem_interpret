"""Спецификация системы команд УВМ (вариант 21).

Все команды хранятся в little-endian. Поля задаются смещением
(номер младшего бита) и шириной в битах.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

OPCODE_NAME = "A"
OPCODE_OFFSET = 0
OPCODE_WIDTH = 5


@dataclass(frozen=True)
class Field:
    """Битовое поле команды."""

    name: str
    offset: int
    width: int


@dataclass(frozen=True)
class CommandSpec:
    """Описание команды: мнемоника, код операции, размер и операнды."""

    mnemonic: str
    opcode: int
    size: int
    operands: Tuple[Field, ...]


COMMANDS = (
    CommandSpec(
        "load", 29, 4,
        (Field("B", 5, 7), Field("C", 12, 18)),
    ),
    CommandSpec(
        "read", 16, 4,
        (Field("B", 5, 7), Field("C", 12, 9), Field("D", 21, 7)),
    ),
    CommandSpec(
        "write", 2, 4,
        (Field("B", 5, 7), Field("C", 12, 7), Field("D", 19, 9)),
    ),
    CommandSpec(
        "abs", 9, 6,
        (Field("B", 5, 32), Field("C", 37, 7)),
    ),
)

BY_MNEMONIC: Dict[str, CommandSpec] = {c.mnemonic: c for c in COMMANDS}
BY_OPCODE: Dict[int, CommandSpec] = {c.opcode: c for c in COMMANDS}
