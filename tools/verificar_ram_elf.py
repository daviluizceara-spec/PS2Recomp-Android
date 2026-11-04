"""Carregamento parcial para análise local; não executa o ELF."""
import argparse
from pathlib import Path
import sys
from elf_loader import load_elf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('elf', type=Path)
    args = parser.parse_args()
    try:
        image = load_elf(args.elf.read_bytes(), allow_unmapped_reservations=True)
    except (OSError, ValueError) as exc:
        print(f'Erro: {exc}', file=sys.stderr)
        return 1
    print(f'Entrada: {image.entry:#010x}')
    print(f'RAM linear preparada: {len(image.ram)} bytes')
    for segment in image.unresolved:
        print(f'PENDENTE: program header {segment.header_index}, '
              f'endereco={segment.vaddr:#010x}, tamanho={segment.size:#x}')
    if image.unresolved:
        print('Carregamento incompleto: reservas pendentes nao estao mapeadas nem inicializadas.')
    else:
        print('Nenhuma reserva externa pendente; mapa de dispositivos nao verificado.')
    print('Analise apenas: codigo do jogo nao foi executado.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
