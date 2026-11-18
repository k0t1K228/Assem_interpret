"""Модель УВМ: раздельные память команд и данных, регистры, цикл."""

import csv
from pathlib import Path
from typing import Callable, Dict, List

from uvm.decoder import decode_instruction
from uvm.errors import VmError

REGISTER_COUNT = 128
DATA_MEMORY_SIZE = 65536
MIN_ADDRESS = 0
DUMP_HEADER = ("address", "value")


def check_address(address: int) -> None:
    """Проверяет, что адрес лежит в пределах памяти данных."""
    if not MIN_ADDRESS <= address < DATA_MEMORY_SIZE:
        raise VmError(
            f"адрес {address} вне памяти данных "
            f"({MIN_ADDRESS}..{DATA_MEMORY_SIZE - 1})"
        )


class Machine:
    """Состояние УВМ: память команд, память данных, регистры, pc."""

    def __init__(self, code: bytes) -> None:
        self.code = code
        self.data: List[int] = [0] * DATA_MEMORY_SIZE
        self.registers: List[int] = [0] * REGISTER_COUNT
        self.pc = 0

    def read_data(self, address: int) -> int:
        """Читает ячейку памяти данных."""
        check_address(address)
        return self.data[address]

    def write_data(self, address: int, value: int) -> None:
        """Записывает значение в ячейку памяти данных."""
        check_address(address)
        self.data[address] = value

    def step(self) -> None:
        """Декодирует и выполняет одну команду, сдвигая pc."""
        instr = decode_instruction(self.code, self.pc)
        self.pc += instr.spec.size
        OPERATIONS[instr.spec.mnemonic](self, instr.fields)

    def run(self) -> int:
        """Выполняет программу до конца памяти команд."""
        executed = 0
        while self.pc < len(self.code):
            self.step()
            executed += 1
        return executed


def op_load(machine: Machine, fields: Dict[str, int]) -> None:
    """Регистр B <- константа C."""
    machine.registers[fields["B"]] = fields["C"]


def op_read(machine: Machine, fields: Dict[str, int]) -> None:
    """Регистр D <- память[регистр B + смещение C]."""
    address = machine.registers[fields["B"]] + fields["C"]
    machine.registers[fields["D"]] = machine.read_data(address)


def op_write(machine: Machine, fields: Dict[str, int]) -> None:
    """Память[регистр B + смещение D] <- регистр C."""
    address = machine.registers[fields["B"]] + fields["D"]
    machine.write_data(address, machine.registers[fields["C"]])


def op_abs(machine: Machine, fields: Dict[str, int]) -> None:
    """Регистр C <- abs(память[адрес B])."""
    value = machine.read_data(fields["B"])
    machine.registers[fields["C"]] = abs(value)


OPERATIONS: Dict[str, Callable[[Machine, Dict[str, int]], None]] = {
    "load": op_load,
    "read": op_read,
    "write": op_write,
    "abs": op_abs,
}


def check_range(first: int, last: int) -> None:
    """Проверяет диапазон адресов для дампа (границы включены)."""
    if not MIN_ADDRESS <= first <= last < DATA_MEMORY_SIZE:
        raise VmError(
            f"неверный диапазон дампа {first}..{last}, допустимо "
            f"{MIN_ADDRESS}..{DATA_MEMORY_SIZE - 1}"
        )


def write_dump(machine: Machine, first: int, last: int, path: str) -> None:
    """Сохраняет в CSV ячейки памяти данных от first до last."""
    check_range(first, last)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(DUMP_HEADER)
        for address in range(first, last + 1):
            writer.writerow([address, machine.data[address]])
