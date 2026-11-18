"""Кодирование команд УВМ в машинный код."""

from typing import List

from uvm.assembler import Instruction
from uvm.isa import BYTE_ORDER, OPCODE_NAME, OPCODE_OFFSET, bit_mask


def encode_instruction(instr: Instruction) -> bytes:
    """Собирает поля команды в число и переводит его в байты."""
    value = instr.fields[OPCODE_NAME] << OPCODE_OFFSET
    for field in instr.spec.operands:
        raw = instr.fields[field.name] & bit_mask(field.width)
        value |= raw << field.offset
    return value.to_bytes(instr.spec.size, BYTE_ORDER)


def assemble(program: List[Instruction]) -> bytes:
    """Кодирует всю программу в последовательность байтов."""
    return b"".join(encode_instruction(instr) for instr in program)


def format_bytes(data: bytes) -> str:
    """Возвращает байты в виде '0xFD, 0x92, 0x3D, 0x00'."""
    return ", ".join(f"0x{byte:02X}" for byte in data)
