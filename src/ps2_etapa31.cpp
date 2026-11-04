
#include <cstdint>
#include <cassert>
#include <iostream>

uint32_t func_100400() {
    uint32_t v0 = 0x0035u << 16;

    // JR RA: retorno apos executar o delay slot
    v0 = v0 + static_cast<uint32_t>(14864);

    return v0;
}

int main() {
    uint32_t resultado = func_100400();

    assert(resultado == 0x00353A10u);

    std::cout << "PS2 RECOMP - ETAPA 31\n";
    std::cout << "Funcao original: 0x100400\n";
    std::cout << "Resultado: 0x"
              << std::hex << resultado << "\n";
    std::cout << "Delay slot: OK\n";
    std::cout << "FUNCAO NATIVA APROVADA\n";
}
