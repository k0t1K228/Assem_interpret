"""Декодирование машинного кода УВМ во внутреннее представление."""

from uvm.assembler import Instruction
from uvm.errors import DecodeError
from uvm.isa import (
    BY_OPCODE, BYTE_ORDER, OPCODE_NAME, OPCODE_OFFSET, OPCODE_WIDTH, Field,
    bit_mask,
)


def extract_field(value: int, field: Field) -> int:
    """Достаёт поле из числа команды; знаковое поле расширяет знаком."""
    raw = (value >> field.offset) & bit_mask(field.width)
    if field.signed and raw >> (field.width - 1):
        raw -= 1 << field.width
    return raw


def decode_instruction(code: bytes, pc: int) -> Instruction:
    """Декодирует команду, начинающуюся с байта по смещению pc."""
    opcode = (code[pc] >> OPCODE_OFFSET) & bit_mask(OPCODE_WIDTH)
    spec = BY_OPCODE.get(opcode)
    if spec is None:
        raise DecodeError(f"неизвестный код операции {opcode} (байт {pc})")
    chunk = code[pc:pc + spec.size]
    if len(chunk) < spec.size:
        raise DecodeError(f"команда по смещению {pc} обрезана")
    value = int.from_bytes(chunk, BYTE_ORDER)
    fields = {OPCODE_NAME: opcode}
    for field in spec.operands:
        fields[field.name] = extract_field(value, field)
    return Instruction(spec, fields)
