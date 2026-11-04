from pathlib import Path
import struct
import sys

ELF = Path.home() / "analise_ps2/game.elf"
SAIDA = Path("src/funcao_gerada.cpp")

dados = ELF.read_bytes()

if dados[:4] != b"\x7fELF":
    raise RuntimeError("ELF invalido")

phoff = struct.unpack_from("<I", dados, 28)[0]
phsize, phnum = struct.unpack_from("<HH", dados, 42)

def ler(pc):
    for i in range(phnum):
        p = phoff + i * phsize
        tipo, off, addr, _, fs, ms, _, _ = \
            struct.unpack_from("<8I", dados, p)

        if tipo == 1 and addr <= pc and pc+4 <= addr+fs:
            return struct.unpack_from(
                "<I", dados, off+pc-addr
            )[0]

    raise RuntimeError("Endereco fora do ELF")

def sinal16(v):
    return v-65536 if v & 0x8000 else v

def traduzir(instr, pc):
    op = instr >> 26
    rs = (instr >> 21) & 31
    rt = (instr >> 16) & 31
    imm = instr & 65535

    if instr == 0:
        return "// NOP"

    if op == 15 and rs == 0:
        if rt == 0:
            return "// Escrita em r0 ignorada"
        return f"r[{rt}] = 0x{imm:04X}u << 16;"

    if op == 9:
        if rt == 0:
            return "// Escrita em r0 ignorada"
        return (
            f"r[{rt}] = r[{rs}] + "
            f"uint32_t({sinal16(imm)});"
        )

    raise RuntimeError(
        f"Instrucao nao suportada: "
        f"{pc:08X} {instr:08X}"
    )

inicio = int(sys.argv[1], 0) if len(sys.argv)>1 \
    else 0x100400

pc = inicio
linhas = []
retorno = False

for passo in range(32):
    ins = ler(pc)

    if ins == 0x03E00008:
        slot = ler(pc+4)
        linhas.append(
            f"// {pc:08X}: JR RA"
        )
        linhas.append(
            f"// {pc+4:08X}: delay slot"
        )
        linhas.append(traduzir(slot, pc+4))
        retorno = True
        break

    linhas.append(f"// {pc:08X}: {ins:08X}")
    linhas.append(traduzir(ins, pc))
    pc += 4

if not retorno:
    raise RuntimeError(
        "Funcao nao terminada em JR RA"
    )

codigo = """\
#include <array>
#include <cstdint>
#include <cassert>
#include <iostream>

uint32_t funcao() {
    std::array<uint32_t,32> r{};
"""
codigo += "\n".join("    "+l for l in linhas)
codigo += """
    return r[2];
}

int main() {
    assert(funcao() == 0x00353A10u);
    std::cout << "TRADUTOR DE FUNCOES PS2\\n";
    std::cout << "Resultado: 0x"
              << std::hex << funcao() << "\\n";
    std::cout << "TESTE APROVADO\\n";
}
"""

SAIDA.parent.mkdir(exist_ok=True)
SAIDA.write_text(codigo)

print("Funcao:", hex(inicio))
print("Instrucoes:", len(linhas))
print("Saida:", SAIDA)
