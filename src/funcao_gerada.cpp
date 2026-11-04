#include <array>
#include <cstdint>
#include <cassert>
#include <iostream>

uint32_t funcao() {
    std::array<uint32_t,32> r{};
    // 00100400: 3C020035
    r[2] = 0x0035u << 16;
    // 00100404: JR RA
    // 00100408: delay slot
    r[2] = r[2] + uint32_t(14864);
    return r[2];
}

int main() {
    assert(funcao() == 0x00353A10u);
    std::cout << "TRADUTOR DE FUNCOES PS2\n";
    std::cout << "Resultado: 0x"
              << std::hex << funcao() << "\n";
    std::cout << "TESTE APROVADO\n";
}
