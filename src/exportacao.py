"""Exportação das tabelas e figuras; Matplotlib só é carregado ao gerar gráficos."""

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType

from src.calculos import QUANTIDADE_TRAJETORIAS
from src.tipos import Frequencia, Trajetoria


def carregar_graficos() -> ModuleType:
    """Seleciona o backend sem janela antes de carregar pyplot."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as grafico

    return grafico


def escrever_csv(caminho: Path, linhas: Sequence[Mapping[str, object]]) -> None:
    """Grava uma lista de dicionários em CSV separado por ponto e vírgula."""
    if not linhas:
        return

    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=linhas[0].keys(), delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)


def salvar_grafico_frequencias(pasta: Path, frequencias: Sequence[Frequencia]) -> None:
    """E1: compara a probabilidade teórica com a frequência observada."""
    grafico = carregar_graficos()
    nomes = [linha["resultado"] for linha in frequencias]
    teoria = [linha["probabilidade_teorica"] * 100 for linha in frequencias]
    observacao = [linha["frequencia_relativa"] * 100 for linha in frequencias]
    posicoes = list(range(len(nomes)))
    largura = 0.38

    grafico.figure(figsize=(10, 5))
    grafico.bar(
        [posicao - largura / 2 for posicao in posicoes], teoria,
        largura, label="Probabilidade teórica",
    )
    grafico.bar(
        [posicao + largura / 2 for posicao in posicoes], observacao,
        largura, label="Frequência observada",
    )
    grafico.xticks(posicoes, nomes, rotation=20)
    grafico.ylabel("Porcentagem (%)")
    grafico.legend()
    grafico.tight_layout()
    grafico.savefig(pasta / "experimento1_frequencias.png", dpi=160)
    grafico.close()



def salvar_grafico_medias(
    pasta: Path, medias_por_semente: Mapping[int, Sequence[float]],
) -> None:
    """E2: mostra a evolução da média acumulada para cada semente."""
    grafico = carregar_graficos()
    grafico.figure(figsize=(10, 5))
    for semente, medias in medias_por_semente.items():
        grafico.plot(range(1, len(medias) + 1), medias, label=f"Semente {semente}")
    grafico.axhline(-0.16, color="black", linestyle="--", label="Referência: -0,16")
    grafico.xlabel("Número de rodadas")
    grafico.ylabel("Lucro médio acumulado (créditos)")
    grafico.legend()
    grafico.tight_layout()
    grafico.savefig(pasta / "experimento2_medias_acumuladas.png", dpi=160)
    grafico.close()



def salvar_grafico_trajetorias(pasta: Path, trajetorias: Sequence[Trajetoria]) -> None:
    """E3: mostra os saldos dos primeiros participantes."""
    grafico = carregar_graficos()
    grafico.figure(figsize=(10, 5))
    for trajetoria in trajetorias[:QUANTIDADE_TRAJETORIAS]:
        grafico.plot(
            range(len(trajetoria["saldos"])), trajetoria["saldos"],
            label=f"Participante {trajetoria['participante']}",
        )
    grafico.xlabel("Rodada")
    grafico.ylabel("Saldo (créditos)")
    grafico.legend()
    grafico.tight_layout()
    grafico.savefig(pasta / "experimento3_trajetorias.png", dpi=160)
    grafico.close()


def salvar_graficos(
    pasta: Path, frequencias: Sequence[Frequencia],
    medias_por_semente: Mapping[int, Sequence[float]], trajetorias: Sequence[Trajetoria],
) -> None:
    """Cria os três gráficos nas pastas correspondentes aos experimentos."""
    pastas = {numero: pasta / f"experimento_{numero}" for numero in range(1, 4)}
    for pasta_experimento in pastas.values():
        pasta_experimento.mkdir(parents=True, exist_ok=True)

    salvar_grafico_frequencias(pastas[1], frequencias)
    salvar_grafico_medias(pastas[2], medias_por_semente)
    salvar_grafico_trajetorias(pastas[3], trajetorias)
