from pathlib import Path
import struct

elf_path = Path.home() / 'analise_ps2' / 'game.elf'
elf = elf_path.read_bytes()
if elf[:4] != b'\x7fELF' or elf[4] != 1 or elf[5] != 1:
    raise SystemExit('ELF32 little-endian esperado')
phoff = struct.unpack_from('<I', elf, 28)[0]
phentsize, phnum = struct.unpack_from('<HH', elf, 42)
if phentsize != 32 or phoff + phentsize * phnum > len(elf):
    raise SystemExit('Tabela ELF invalida')

def read32(pc):
    for i in range(phnum):
        p = phoff + i * phentsize
        ty, off, va, _, fsize, msize, _, _ = struct.unpack_from('<8I', elf, p)
        if ty == 1 and va <= pc and pc+4 <= va+fsize:
            pos = off + pc-va
            if pos+4 > len(elf):
                raise SystemExit('Arquivo truncado')
            return struct.unpack_from('<I', elf, pos)[0]
    raise SystemExit(f'Endereco nao mapeado: {pc:08X}')

pc = 0x100208
jal = read32(pc)
slot = read32(pc + 4)
if (jal >> 26) != 3:
    raise SystemExit('JAL nao encontrada')
# ADDIU rt, rs, imm
if slot >> 26 != 9:
    raise SystemExit('Delay slot nao e ADDIU')
rs = (slot >> 21) & 31
rt = (slot >> 16) & 31
imm = slot & 0xffff
signed_imm = imm if imm < 0x8000 else imm-0x10000
target = ((pc+4) & 0xF0000000) | ((jal & 0x03ffffff) << 2)
ret = pc + 8
assert (rs, rt, signed_imm) == (2, 5, 4)
assert target == 0x11fe60

cpp = f'''#include <array>
#include <cstdint>
#include <iostream>
#include <cassert>
using Regs = std::array<uint32_t, 32>;
struct Result {{
    uint32_t called_target;
    uint32_t ra_at_call;
    uint32_t a1_at_call;
    uint32_t next_pc;
}};
// Funcao simulada, nao o codigo original do Bomba Patch.
uint32_t stub_called_function(uint32_t target, const Regs& r) {{
    assert(target == 0x{target:08X}u);
    assert(r[31] == 0x{ret:08X}u);
    assert(r[5] == 0x1234567Cu);
    return r[31];
}}
Result test_jal(Regs& r) {{
    r[31] = 0x{ret:08X}u; // JAL define RA=PC+8
    // Delay slot original executado antes de entrar na funcao.
    r[{rt}] = r[{rs}] + uint32_t({signed_imm});
    const uint32_t ra = r[31];
    const uint32_t a1 = r[5];
    const uint32_t next_pc = stub_called_function(0x{target:08X}u, r);
    return {{0x{target:08X}u, ra, a1, next_pc}};
}}
int main() {{
    Regs r{{}};
    r[2] = 0x12345678u;
    Result x = test_jal(r);
    assert(x.called_target == 0x{target:08X}u);
    assert(x.ra_at_call == 0x{ret:08X}u);
    assert(x.a1_at_call == 0x1234567Cu);
    assert(x.next_pc == 0x{ret:08X}u);
    std::cout << "ETAPA 36 - JAL + DELAY SLOT\\n";
    std::cout << "Alvo da chamada: OK\\n";
    std::cout << "RA (PC+8): OK\\n";
    std::cout << "Delay slot ADDIU: OK\\n";
    std::cout << "Retorno simulado: OK\\n";
    std::cout << "TESTES APROVADOS\\n";
}}
'''
out = Path.home() / 'PS2Recomp-Android' / 'src' / 'etapa36.cpp'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(cpp)
print('JAL real identificada:', hex(pc))
print('Destino:', hex(target))
print('Retorno:', hex(ret))
print('C++ gerado:', out)
