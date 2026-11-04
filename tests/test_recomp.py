import subprocess
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
codigo = raiz / "src/ps2_etapa31.cpp"
saida = raiz / "build/teste_funcao"

saida.parent.mkdir(exist_ok=True)

print("PS2RECOMP ANDROID - TESTES")

compilar = subprocess.run([
    "clang++",
    "-std=c++17",
    "-O2",
    "-Wall",
    "-Wextra",
    str(codigo),
    "-o",
    str(saida)
], capture_output=True, text=True)

if compilar.returncode != 0:
    print(compilar.stderr)
    raise SystemExit("FALHA NA COMPILACAO")

print("Compilacao ARM64: OK")

teste = subprocess.run(
    [str(saida)],
    capture_output=True,
    text=True
)

print(teste.stdout)

if teste.returncode != 0:
    print(teste.stderr)
    raise SystemExit("TESTE FALHOU")

if "FUNCAO NATIVA APROVADA" not in teste.stdout:
    raise SystemExit("RESULTADO INESPERADO")

print("REGRESSAO: APROVADA")
