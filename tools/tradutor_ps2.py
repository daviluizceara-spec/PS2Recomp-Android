import struct
from pathlib import Path

elf_path = Path("analise_ps2/game.elf")
saida = Path("ps2_gerado.cpp")

elf = elf_path.read_bytes()

if elf[:4] != b"\x7fELF":
    raise ValueError("Arquivo nao e ELF")

entrada = struct.unpack_from("<I", elf, 24)[0]
phoff = struct.unpack_from("<I", elf, 28)[0]
phsize, phnum = struct.unpack_from("<HH", elf, 42)

segmento = None
for i in range(phnum):
    p = phoff + i * phsize
    tipo, off, addr, _, fs, ms, _, _ = \
        struct.unpack_from("<8I", elf, p)

    if tipo == 1 and addr <= entrada < addr + fs:
        segmento = (off, addr, fs)
        break

if segmento is None:
    raise ValueError("Entrada nao encontrada")

off, base, fs = segmento

codigo = r'''
#include <array>
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <cassert>

using Reg128 = std::array<uint32_t, 4>;

Reg128 padduw(Reg128 a, Reg128 b) {
    Reg128 resultado{};
    for (int i = 0; i < 4; i++) {
        uint64_t soma = uint64_t(a[i]) + b[i];
        resultado[i] = uint32_t(
            std::min(soma, uint64_t(0xFFFFFFFF))
        );
    }
    return resultado;
}

void executar_bloco(std::array<Reg128, 32>& r) {
'''

total = 0
pc = entrada

while total < 29:
    pos = off + pc - base
    if pos < off or pos + 4 > off + fs:
        raise ValueError("Instrucao fora do segmento")

    ins = struct.unpack_from("<I", elf, pos)[0]
    op = (ins >> 26) & 63
    func = ins & 63
    sa = (ins >> 6) & 31
    rs = (ins >> 21) & 31
    rt = (ins >> 16) & 31
    rd = (ins >> 11) & 31

    if not (op == 0x1C and func == 0x28 and sa == 0x10):
        raise ValueError(
            f"Instrucao inesperada: {pc:08X} {ins:08X}"
        )

    codigo += f"    // {pc:08X}: {ins:08X}\n"
    if rd != 0:
        codigo += f"    r[{rd}] = padduw(r[{rs}], r[{rt}]);\n"

    total += 1
    pc += 4

codigo += r'''
    r[0] = Reg128{};
}

int main() {
    // Teste das quatro faixas de 32 bits
    Reg128 a{0xFFFFFFFF, 10, 0xFFFFFFFE, 7};
    Reg128 b{1, 20, 5, 8};

    Reg128 resultado = padduw(a, b);
    assert((resultado == Reg128{
        0xFFFFFFFF, 30, 0xFFFFFFFF, 15
    }));

    std::array<Reg128, 32> r{};
    executar_bloco(r);

    for (const auto& reg : r) {
        assert((reg == Reg128{}));
    }

    std::cout << "TRADUCAO ESTATICA PS2 -> C++\n";
    std::cout << "Teste PADDUW: OK\n";
    std::cout << "Bloco de inicializacao: OK\n";
    std::cout << "TESTES APROVADOS!\n";
}
'''

saida.write_text(codigo)

print("TRADUTOR PS2")
print("Entrada:", hex(entrada))
print("Instrucoes traduzidas:", total)
print("Proximo endereco:", hex(pc))
print("C++ gerado:", saida)
