#include <array>
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
    // 0x001001FC: 0x3C02003D
    r[2] = 0x003Du << 16;
    // 0x00100200: 0x2442AE80
    r[2] = r[2] + uint32_t(-20864);
    // 0x00100204: 0x8C440000
    r[4] = m.lw(r[2] + uint32_t(0));
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
