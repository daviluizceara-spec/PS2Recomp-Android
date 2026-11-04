# Estado do projeto

Auditoria da branch main, commit 044b520c2f79700de8e158e7694de4959f4b6e62. Ambiente de verificação: Linux x86_64, Python 3 e g++; não Android. O ELF não foi disponibilizado.

## Inventário

- `tools/`: seis protótipos de tradução/análise e `etapa39.py`, que examina o relatório e conta instruções e chamadas.
- `src/`: cinco programas C++ independentes, incluindo um carregador experimental e amostras geradas.
- `tests/`: teste de memória C++ e teste Python de compilação de uma amostra.
- `reports/`: nove relatórios, incluindo as duas funções e o resumo da etapa 39.
- `.gitignore`: regras de exclusão. Nenhum ELF ou ISO está na árvore auditada.

## Comprovado nesta máquina

- Os programas `test_memoria.cpp`, `ps2_etapa31.cpp`, `funcao_gerada.cpp`, `bloco_memoria.cpp` e `etapa36.cpp` compilaram com g++ e passaram seus asserts. O primeiro testa memória isolada; os demais são exemplos fixos. A chamada na etapa 36 usa stub explícito.
- O novo decodificador reconhece os campos das quatro palavras LQ/SQ registradas no relatório, offsets negativos e rejeita outros opcodes. São testes de decodificação, não de execução.

## Parcial e limitações

- `tradutor_funcoes.py` trata NOP, LUI, ADDIU e JR RA com delay slot para uma amostra; usa registradores de 32 bits e inclui assert fixo para o resultado específico. Não é tradutor geral R5900.
- `tradutor_memoria.py` gera um bloco LUI/ADDIU/LW com memória de teste; `tradutor_ps2.py` gera uma amostra PADDUW; `etapa31.py` e `etapa36.py` são demonstrações específicas. A validade completa da semântica R5900 desses protótipos ainda precisa de verificação independente.
- `etapa30.cpp` inicializa RAM uma vez e copia segmentos, mas executa depois um teste destrutivo de limpeza sobre faixa fixa: pode apagar dados carregados. Não usar como carregador geral; sobreposição de segmentos e BSS exigem testes próprios. Ele também ignora validação de endereço para segmentos com filesz zero.
- Relatórios estudam BEQ/BNE, JAL/JR, MTHI/MTLO, MTC1, MMI, LQ/SQ e outras instruções; aparecer em relatório não implica implementação. A análise de `etapa39.py` depende de caminhos sob HOME e não executa as funções.
- Os exemplos `ps2_etapa31.cpp` e `funcao_gerada.cpp` duplicam a mesma função para fins históricos; implementações de memória também são duplicadas. Não foram removidos.
- `test_recomp.py` declara compilação ARM64 mesmo quando compila para a arquitetura hospedeira; nesta máquina falhou por falta de clang++. Os dados ELF informados não foram verificados sem o arquivo.
- A referência pública PCSX2 `pcsx2/R5900OpcodeTables.cpp` associa opcodes primários 0x1e e 0x1f a LQ e SQ; ainda falta confrontar a documentação oficial R5900 e validar a semântica de alinhamento, exceções e acesso de 128 bits. O módulo novo não executa memória e não constitui validação de semântica.

## Não iniciado como sistema integrado

Recompilação geral com fluxo de controle e delay slots, chamadas interligadas, estado completo de 128 bits/HI/LO/FPU, mapa de memória e dispositivos, IOP, gráficos, áudio, controles, seletor de ISO, aplicativo Android e equivalência com o jogo. Dependências de runtime serão necessárias; viabilidade e desempenho ainda não foram demonstrados.

## Próximos passos

Validar opcodes e semântica em documentação R5900, criar representação intermediária com 128 bits e erros explícitos, depois testar fluxo de controle e carregamento ELF com fixtures sintéticas e segmentos sobrepostos. O ELF local será necessário para conferir os relatórios e testar instruções reais; não incluí-lo no repositório. Em Android ARM64 real executar os testes de decodificação e amostras C++, depois testes de equivalência, integração, desempenho e aplicativo quando existirem.

## Continuação: memória e referências LQ/SQ

`tools/elf_loader.py` é um carregador experimental independente do protótipo C++: valida ELF32 MIPS little-endian e limites, zera a RAM uma vez e copia os dados dos PT_LOAD na ordem da tabela. As reservas BSS sobrepostas não apagam dados de arquivo; se dois dados de arquivo se sobrepõem, o último prevalece. Essa política é explícita e ainda não foi validada com o ELF do jogo, nem cobre mapa de dispositivos, relocação, permissões, endereços virtuais especiais ou todos os formatos ELF. Os testes sintéticos cobrem as duas ordens de BSS, sobreposição de dados, truncamento e limites, incluindo segmento sem dados fora da RAM.

Como referência secundária, a implementação [PCSX2 R5900OpcodeImpl.cpp](https://github.com/PCSX2/pcsx2/blob/1ccd6a8dc3574771c138849039d71951a3a1c175/pcsx2/R5900OpcodeImpl.cpp) calcula base mais offset e alinha o endereço para baixo com `& ~0xf` para LQ e SQ, acessando 128 bits. A [tabela de opcodes](https://github.com/PCSX2/pcsx2/blob/1ccd6a8dc3574771c138849039d71951a3a1c175/pcsx2/R5900OpcodeTables.cpp) associa os opcodes a essas instruções. Isso não substitui a especificação oficial nem valida o hardware. Ainda não há execução de LQ/SQ neste projeto.
