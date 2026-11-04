"""Decodificador parcial R5900. Não executa instruções."""
from dataclasses import dataclass


class UnsupportedInstruction(ValueError):
    """Instrução fora do subconjunto implementado."""


@dataclass(frozen=True)
class QuadwordMemoryInstruction:
    mnemonic: str
    base: int
    register: int
    offset: int


def decode(word: int) -> QuadwordMemoryInstruction:
    if not isinstance(word, int) or not 0 <= word <= 0xffffffff:
        raise ValueError("Esperada palavra inteira de 32 bits")

    opcode = word >> 26
    if opcode not in (0x1e, 0x1f):
        raise UnsupportedInstruction(
            f"Instrucao nao suportada: {word:08X}"
        )

    imm = word & 0xffff
    return QuadwordMemoryInstruction(
        "LQ" if opcode == 0x1e else "SQ",
        (word >> 21) & 31,
        (word >> 16) & 31,
        imm - 0x10000 if imm & 0x8000 else imm,
    )
