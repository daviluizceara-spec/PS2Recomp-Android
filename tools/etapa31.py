from pathlib import Path
import struct

elf = Path("analise_ps2/game.elf").read_bytes()

if elf[:4] != b"\x7fELF":
    raise RuntimeError("ELF invalido")

phoff = struct.unpack_from("<I", elf, 28)[0]
phsize, phnum = struct.unpack_from("<HH", elf, 42)

def ler(pc):
    for i in range(phnum):
        p = phoff + i * phsize
        tipo, off, addr, _, fs, ms, _, _ = \
            struct.unpack_from("<8I", elf, p)

        if tipo == 1 and addr <= pc and pc+4 <= addr+fs:
            pos = off + pc - addr
            return struct.unpack_from("<I", elf, pos)[0]

    raise RuntimeError("Endereco nao encontrado")

inicio = 0x100400
a = ler(inicio)
b = ler(inicio + 4)
c = ler(inicio + 8)

# Validar a estrutura da funcao
if (a >> 26) != 15:
    raise RuntimeError("LUI inesperado")

if ((a >> 16) & 31) != 2:
    raise RuntimeError("Destino LUI inesperado")

if b != 0x03E00008:
    raise RuntimeError("Retorno JR RA inesperado")

if (c >> 26) != 9:
    raise RuntimeError("Delay slot inesperado")

rs = (c >> 21) & 31
rt = (c >> 16) & 31

if rs != 2 or rt != 2:
    raise RuntimeError("ADDIU inesperado")

alto = a & 0xFFFF
baixo = c & 0xFFFF

if baixo >= 0x8000:
    baixo -= 0x10000

resultado = ((alto << 16) + baixo) & 0xFFFFFFFF

codigo = f"""
#include <cstdint>
#include <cassert>
#include <iostream>

uint32_t func_100400() {{
    uint32_t v0 = 0x{alto:04X}u << 16;

    // JR RA: retorno apos executar o delay slot
    v0 = v0 + static_cast<uint32_t>({baixo});

    return v0;
}}

int main() {{
    uint32_t resultado = func_100400();

    assert(resultado == 0x{resultado:08X}u);

    std::cout << "PS2 RECOMP - ETAPA 31\\n";
    std::cout << "Funcao original: 0x100400\\n";
    std::cout << "Resultado: 0x"
              << std::hex << resultado << "\\n";
    std::cout << "Delay slot: OK\\n";
    std::cout << "FUNCAO NATIVA APROVADA\\n";
}}
"""

Path("ps2_etapa31.cpp").write_text(codigo)

print("FUNCAO MIPS IDENTIFICADA")
print("Instrucoes:", 3)
print("Resultado esperado:", hex(resultado))
print("C++ gerado: ps2_etapa31.cpp")
