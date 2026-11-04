"""Carregador experimental ELF32 MIPS para RAM linear, sem dispositivos PS2.

Política: RAM começa zerada, depois dados PT_LOAD são copiados na ordem
dos cabeçalhos. BSS não apaga dados de outros segmentos. Quando dados de
arquivo se sobrepõem, o último segmento prevalece.
"""
import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class UnmappedReservation:
    header_index: int
    vaddr: int
    size: int


@dataclass(frozen=True)
class LoadedElf:
    entry: int
    ram: bytearray
    unresolved: tuple = ()


def load_elf(data: bytes, ram_size: int = 32 * 1024 * 1024, *,
             allow_unmapped_reservations: bool = False) -> LoadedElf:
    """Carrega RAM; modo opt-in devolve reservas externas como pendentes.

    Uma reserva pendente não foi alocada nem inicializada e impede considerar
    o carregamento completo. Não habilita execução do programa.
    """
    if ram_size <= 0:
        raise ValueError('Tamanho de RAM invalido')
    if len(data) < 52:
        raise ValueError('Cabecalho ELF truncado')
    ident = data[:16]
    if ident[:4] != b'\x7fELF' or ident[4:7] != b'\x01\x01\x01':
        raise ValueError('Esperado ELF32 little-endian versao 1')
    fields = struct.unpack_from('<HHIIIIIHHHHHH', data, 16)
    _, machine, version, entry, phoff, _, _, ehsize, phentsize, phnum, _, _, _ = fields
    if machine != 8 or version != 1 or ehsize != 52 or phentsize != 32:
        raise ValueError('Cabecalho ELF MIPS invalido ou nao suportado')
    if phnum == 0xffff or phoff + phentsize * phnum > len(data):
        raise ValueError('Tabela de segmentos invalida ou nao suportada')
    segments = []
    unresolved = []
    for i in range(phnum):
        kind, offset, addr, _, filesz, memsz, _, _ = struct.unpack_from(
            '<8I', data, phoff + i * phentsize)
        if kind != 1:
            continue
        if filesz > memsz or (filesz and offset + filesz > len(data)) or addr + memsz > 0x100000000:
            raise ValueError('Segmento PT_LOAD invalido ou fora da RAM')
        if addr + memsz > ram_size:
            if allow_unmapped_reservations and not filesz and memsz and addr >= ram_size:
                unresolved.append(UnmappedReservation(i, addr, memsz))
                continue
            raise ValueError('Segmento PT_LOAD invalido ou fora da RAM')
        segments.append((offset, addr, filesz))
    ram = bytearray(ram_size)
    for offset, addr, filesz in segments:
        ram[addr:addr + filesz] = data[offset:offset + filesz]
    return LoadedElf(entry, ram, tuple(unresolved))
