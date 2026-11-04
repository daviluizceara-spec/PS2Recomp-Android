#!/usr/bin/env python3
"""Bomba Patch PS2: demonstração de tradução estática de um bloco LUI/ADDIU/LW.
Lê somente o ELF local do usuário; não altera a ISO nem o executável.
"""
from pathlib import Path
import struct

ROOT = Path.home() / 'PS2Recomp-Android'
ELF = Path.home() / 'analise_ps2' / 'game.elf'
OUTPUT = ROOT / 'src' / 'bloco_memoria.cpp'
START = 0x1001FC

def u16signed(value):
    return value - 0x10000 if value & 0x8000 else value

def main():
    data = ELF.read_bytes()
    if len(data) < 52 or data[:4] != b'\x7fELF' or data[4] != 1 or data[5] != 1:
        raise RuntimeError('Esperado ELF32 little-endian')
    if struct.unpack_from('<H', data, 18)[0] != 8:
        raise RuntimeError('Esperado ELF MIPS')
    phoff = struct.unpack_from('<I', data, 28)[0]
    phsize, phnum = struct.unpack_from('<HH', data, 42)
    if phsize != 32 or phoff + phnum * phsize > len(data):
        raise RuntimeError('Tabela de segmentos invalida')

    def read_instruction(pc):
        for i in range(phnum):
            pos = phoff + i * phsize
            typ, off, addr, _, fs, ms, _, _ = struct.unpack_from('<8I', data, pos)
            if typ == 1 and addr <= pc and pc + 4 <= addr + fs and off + fs <= len(data):
                return struct.unpack_from('<I', data, off + pc - addr)[0]
        raise RuntimeError(f'Endereco nao encontrado: {pc:08X}')

    lines = []
    for i, expected_opcode in enumerate((15, 9, 35)):
        pc = START + i * 4
        ins = read_instruction(pc)
        op = (ins >> 26) & 63
        rs, rt, imm = (ins >> 21) & 31, (ins >> 16) & 31, ins & 0xFFFF
        if op != expected_opcode or rt == 0:
            raise RuntimeError(f'Instrucao inesperada em {pc:08X}: {ins:08X}')
        if op == 15:
            if rs:
                raise RuntimeError('LUI com campo rs inesperado')
            statement = f'r[{rt}] = 0x{imm:04X}u << 16;'
        elif op == 9:
            statement = f'r[{rt}] = r[{rs}] + uint32_t({u16signed(imm)});'
        else:
            statement = f'r[{rt}] = m.lw(r[{rs}] + uint32_t({u16signed(imm)}));'
        lines.append(f'    // 0x{pc:08X}: 0x{ins:08X}\n    {statement}')

    if (read_instruction(START + 12) >> 26) != 3:
        raise RuntimeError('Esperado JAL depois do bloco')

    cpp = r'''#include <array>
#include <vector>
#include <cstdint>
#include <cassert>
#include <iostream>
#include <stdexcept>
struct Memoria {
    std::vector<uint8_t> ram;
    Memoria(): ram(32 * 1024 * 1024, 0) {}
    void sw(uint32_t a, uint32_t v) {
        if ((a & 3u) || uint64_t(a) + 4 > ram.size())
            throw std::runtime_error("SW invalido");
        for (int i=0; i<4; ++i) ram[a+i] = uint8_t(v >> (8*i));
    }
    uint32_t lw(uint32_t a) const {
        if ((a & 3u) || uint64_t(a) + 4 > ram.size())
            throw std::runtime_error("LW invalido");
        uint32_t v = 0;
        for (int i=0; i<4; ++i) v |= uint32_t(ram[a+i]) << (8*i);
        return v;
    }
};
uint32_t bloco(Memoria& m) {
    std::array<uint32_t,32> r{};
'''
    cpp += '\n'.join(lines)
    cpp += r'''
    return r[4];
}
int main() {
    Memoria m;
    constexpr uint32_t endereco = 0x003CAE80;
    m.sw(endereco, 0x12345678);
    assert(bloco(m) == 0x12345678);
    m.sw(endereco, 0xDEADBEEF);
    assert(bloco(m) == 0xDEADBEEF);
    std::cout << "PS2 RECOMP - ETAPA 35\n"
              << "LUI: OK\nADDIU: OK\nLW: OK\n"
              << "Memoria integrada: OK\nTESTES APROVADOS\n";
}
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(cpp)
    print('3 instrucoes traduzidas')
    print('C++ gerado:', OUTPUT)
    print('Proxima instrucao: JAL')

if __name__ == '__main__':
    main()
