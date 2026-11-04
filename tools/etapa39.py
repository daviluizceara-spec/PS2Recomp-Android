from pathlib import Path
import re

origem = Path.home() / 'PS2Recomp-Android/reports/funcao_11FF40.txt'
if not origem.exists():
    raise SystemExit(f'Relatorio nao encontrado: {origem}')

linhas = []
chamadas = []
correcoes = []
for linha in origem.read_text().splitlines():
    p = linha.split(maxsplit=2)
    if len(p) < 2:
        continue
    try:
        pc, palavra = int(p[0], 16), int(p[1], 16)
    except ValueError:
        continue
    if not (0x11FF40 <= pc <= 0x1200E8):
        continue
    op = palavra >> 26
    reg = (palavra >> 16) & 31
    base = (palavra >> 21) & 31
    imediato = palavra & 0xffff
    offset = imediato - 0x10000 if imediato & 0x8000 else imediato
    nomes = {16:'s0', 17:'s1', 29:'sp', 31:'ra'}
    if op in (0x1e, 0x1f):
        instr = 'LQ' if op == 0x1e else 'SQ'
        forma = f'{instr} ${nomes.get(reg, str(reg))}, {offset}(${nomes.get(base, str(base))})'
        correcoes.append(f'{pc:08X} {palavra:08X} {forma}')
    if op == 3:
        alvo = ((pc + 4) & 0xf0000000) | ((palavra & 0x03ffffff) << 2)
        chamadas.append((pc, alvo))
    linhas.append(pc)

assert len(linhas) == 107, f'Esperadas 107 instrucoes, encontradas {len(linhas)}'
assert len(chamadas) == 45, f'Esperadas 45 chamadas, encontradas {len(chamadas)}'
assert len(set(alvo for _, alvo in chamadas)) == 37
assert len(correcoes) == 4, f'Esperadas 4 instrucoes SQ/LQ, encontradas {len(correcoes)}'

saida = Path.home() / 'PS2Recomp-Android/reports/etapa39_resumo.txt'
saida.parent.mkdir(parents=True, exist_ok=True)
resumo = [
    'ETAPA 39 - ANALISE E CORRECAO DE OPCODES PS2',
    f'Instrucoes da funcao: {len(linhas)}',
    f'Chamadas JAL: {len(chamadas)}',
    f'Destinos distintos: {len(set(a for _, a in chamadas))}',
    '', 'Instrucoes PS2 de 128 bits:'
] + correcoes + ['', 'Chamadas encontradas:'] + [f'{pc:08X} -> {alvo:08X}' for pc, alvo in chamadas]
saida.write_text('\n'.join(resumo) + '\n')
print('\n'.join(resumo[:11]))
print('Resumo completo:', saida)
print('TESTES APROVADOS')
