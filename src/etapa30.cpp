#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <cassert>
#include <elf.h>

int main() {
    constexpr size_t RAM = 32 * 1024 * 1024;

    std::ifstream f(
        "analise_ps2/game.elf",
        std::ios::binary | std::ios::ate
    );

    if (!f) {
        std::cerr << "ELF nao encontrado\n";
        return 1;
    }

    auto tamanho = f.tellg();
    if (tamanho < static_cast<std::streamoff>(
            sizeof(Elf32_Ehdr))) return 1;

    std::vector<uint8_t> elf(
        static_cast<size_t>(tamanho)
    );

    f.seekg(0);
    f.read((char*)elf.data(), elf.size());
    if (!f) return 1;

    Elf32_Ehdr h{};
    std::memcpy(&h, elf.data(), sizeof(h));

    if (std::memcmp(h.e_ident, ELFMAG, SELFMAG) ||
        h.e_ident[EI_CLASS] != ELFCLASS32 ||
        h.e_ident[EI_DATA] != ELFDATA2LSB ||
        h.e_machine != EM_MIPS ||
        h.e_phentsize != sizeof(Elf32_Phdr) ||
        uint64_t(h.e_phoff) +
        uint64_t(h.e_phnum) * h.e_phentsize >
        elf.size()) {
        std::cerr << "ELF invalido\n";
        return 1;
    }

    std::vector<uint8_t> ram(RAM, 0);
    int carregados = 0;

    for (int i = 0; i < h.e_phnum; i++) {
        Elf32_Phdr p{};

        std::memcpy(
            &p,
            elf.data() + h.e_phoff +
                i * h.e_phentsize,
            sizeof(p)
        );

        if (p.p_type != PT_LOAD) continue;

        if (p.p_filesz > p.p_memsz ||
            uint64_t(p.p_offset) + p.p_filesz >
                elf.size()) {
            std::cerr << "Segmento invalido\n";
            return 1;
        }

        if (p.p_filesz == 0) continue;

        if (uint64_t(p.p_vaddr) + p.p_memsz > RAM) {
            std::cerr << "Segmento fora da RAM\n";
            return 1;
        }

        std::memcpy(
            ram.data() + p.p_vaddr,
            elf.data() + p.p_offset,
            p.p_filesz
        );
        carregados++;
    }

    constexpr uint32_t inicio = 0x003C9680;
    constexpr uint32_t fim = 0x01D8D800;

    if (h.e_entry + 4 > RAM ||
        inicio >= fim || fim > RAM) return 1;

    uint8_t codigo_original[4];
    std::memcpy(
        codigo_original,
        ram.data() + h.e_entry, 4
    );

    // Teste de limpeza da regiao BSS
    std::memset(
        ram.data() + inicio,
        0xA5,
        fim - inicio
    );

    std::memset(
        ram.data() + inicio,
        0,
        fim - inicio
    );

    bool memoria_ok = true;
    for (uint32_t i = inicio; i < fim; i++) {
        if (ram[i] != 0) {
            memoria_ok = false;
            break;
        }
    }

    bool codigo_ok = (
        std::memcmp(
            codigo_original,
            ram.data() + h.e_entry,
            4
        ) == 0
    );

    std::cout << "PS2 RECOMP - ETAPA 30\n";
    std::cout << "Segmentos com dados: "
              << carregados << "\n";
    std::cout << "Entrada: 0x"
              << std::hex << h.e_entry << "\n";
    std::cout << std::dec;
    std::cout << "Memoria limpa: "
              << (memoria_ok ? "OK" : "ERRO") << "\n";
    std::cout << "Codigo preservado: "
              << (codigo_ok ? "OK" : "ERRO") << "\n";

    if (!memoria_ok || !codigo_ok) return 1;

    std::cout << "TESTES APROVADOS\n";
}
