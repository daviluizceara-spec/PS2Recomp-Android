#include <array>
#include <cstdint>
#include <iostream>
#include <cassert>
using Regs = std::array<uint32_t, 32>;
struct Result {
    uint32_t called_target;
    uint32_t ra_at_call;
    uint32_t a1_at_call;
    uint32_t next_pc;
};
// Funcao simulada, nao o codigo original do Bomba Patch.
uint32_t stub_called_function(uint32_t target, const Regs& r) {
    assert(target == 0x0011FE60u);
    assert(r[31] == 0x00100210u);
    assert(r[5] == 0x1234567Cu);
    return r[31];
}
Result test_jal(Regs& r) {
    r[31] = 0x00100210u; // JAL define RA=PC+8
    // Delay slot original executado antes de entrar na funcao.
    r[5] = r[2] + uint32_t(4);
    const uint32_t ra = r[31];
    const uint32_t a1 = r[5];
    const uint32_t next_pc = stub_called_function(0x0011FE60u, r);
    return {0x0011FE60u, ra, a1, next_pc};
}
int main() {
    Regs r{};
    r[2] = 0x12345678u;
    Result x = test_jal(r);
    assert(x.called_target == 0x0011FE60u);
    assert(x.ra_at_call == 0x00100210u);
    assert(x.a1_at_call == 0x1234567Cu);
    assert(x.next_pc == 0x00100210u);
    std::cout << "ETAPA 36 - JAL + DELAY SLOT\n";
    std::cout << "Alvo da chamada: OK\n";
    std::cout << "RA (PC+8): OK\n";
    std::cout << "Delay slot ADDIU: OK\n";
    std::cout << "Retorno simulado: OK\n";
    std::cout << "TESTES APROVADOS\n";
}
