#include <iostream>
#include <vector>
#include <cstdint>
#include <stdexcept>
#include <cassert>

class Memoria {
    std::vector<uint8_t> ram;

    void verificar(uint32_t addr, uint32_t tamanho) {
        if (uint64_t(addr) + tamanho > ram.size())
            throw std::out_of_range("Endereco invalido");
    }

public:
    Memoria() : ram(32 * 1024 * 1024, 0) {}

    void sw(uint32_t addr, uint32_t valor) {
        if (addr & 3)
            throw std::runtime_error("SW desalinhado");

        verificar(addr, 4);

        for (int i = 0; i < 4; i++)
            ram[addr+i] =
                uint8_t(valor >> (8*i));
    }

    uint32_t lw(uint32_t addr) {
        if (addr & 3)
            throw std::runtime_error("LW desalinhado");

        verificar(addr, 4);

        uint32_t valor = 0;
        for (int i = 0; i < 4; i++)
            valor |= uint32_t(ram[addr+i]) << (8*i);

        return valor;
    }

    void sb(uint32_t addr, uint8_t valor) {
        verificar(addr, 1);
        ram[addr] = valor;
    }

    int32_t lb(uint32_t addr) {
        verificar(addr, 1);
        uint32_t v = ram[addr];
        return v < 128 ? int32_t(v) : int32_t(v)-256;
    }
};

int main() {
    Memoria m;
    constexpr uint32_t endereco = 0x100000;

    m.sw(endereco, 0x12345678);
    assert(m.lw(endereco) == 0x12345678);

    m.sb(endereco, 0xAB);
    assert(m.lw(endereco) == 0x123456AB);

    assert(m.lb(endereco) == -85);
    assert(m.lb(endereco+1) == 0x56);

    bool erro = false;
    try {
        m.sw(0x100001, 123);
    } catch (const std::runtime_error&) {
        erro = true;
    }
    assert(erro);

    erro = false;
    try {
        m.lw(0x2000000);
    } catch (const std::out_of_range&) {
        erro = true;
    }
    assert(erro);

    std::cout << "PS2 RECOMP - ETAPA 34\n";
    std::cout << "LW: OK\n";
    std::cout << "SW: OK\n";
    std::cout << "SB: OK\n";
    std::cout << "LB: OK\n";
    std::cout << "Alinhamento: OK\n";
    std::cout << "Protecao de memoria: OK\n";
    std::cout << "TESTES APROVADOS\n";
}
