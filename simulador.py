"""Entrada do simulador e organização dos cinco experimentos.

As funções de cálculo e exportação continuam acessíveis por ``import simulador``.
"""

import platform
from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path

from src.calculos import (APOSTA, MAX_RODADAS_SESSAO, PREMIOS,
                          QUANTIDADE_PARTICIPANTES, QUANTIDADE_REPRODUCAO,
                          QUANTIDADE_RODADAS, QUANTIDADE_TRAJETORIAS,
                          SALDO_INICIAL, SEMENTE_PRINCIPAL, SEMENTE_SESSOES,
                          SEMENTES_MEDIAS, SIMBOLOS, TOTAL_RESULTADOS_TEORICOS)
from src.calculos import analisar_pares as analisar_pares
from src.calculos import \
    calcular_medias_acumuladas as calcular_medias_acumuladas
from src.calculos import calcular_resumo as calcular_resumo
from src.calculos import comparar_pagamentos as comparar_pagamentos
from src.calculos import contar_frequencias as contar_frequencias
from src.calculos import fazer_rodada as fazer_rodada
from src.calculos import montar_rodada as montar_rodada
from src.calculos import resumir_sessoes as resumir_sessoes
from src.calculos import simular_rodadas as simular_rodadas
from src.calculos import simular_sessoes as simular_sessoes
from src.exportacao import escrever_csv, salvar_graficos
from src.tipos import (Frequencia, ResumoRodadas, ResumoSessoes,
                       RodadaNumerada, Trajetoria)


def executar_experimento_frequencias(
    pasta_resultados: Path, rodadas_2026: Sequence[RodadaNumerada],
) -> tuple[list[Frequencia], ResumoRodadas]:
    """E1: exporta as rodadas, frequências e o resumo da sequência principal."""
    frequencias = contar_frequencias(rodadas_2026)
    resumo_e1 = calcular_resumo(rodadas_2026)

    linhas_e1 = []
    for rodada in rodadas_2026:
        linhas_e1.append({
            "rodada": rodada["rodada"],
            "linha_central": rodada["combinacao"],
            "premio_bruto": rodada["premio"],
            "lucro_liquido": rodada["lucro"],
            "premiada": rodada["premiada"],
        })
    escrever_csv(pasta_resultados / "experimento1_rodadas.csv", linhas_e1)
    escrever_csv(pasta_resultados / "experimento1_frequencias.csv", frequencias)
    escrever_csv(pasta_resultados / "experimento1_resumo.csv", [resumo_e1])

    return frequencias, resumo_e1


def executar_experimento_medias(
    pasta_resultados: Path, rodadas_2026: Sequence[RodadaNumerada],
) -> dict[int, list[float]]:
    """E2: compara sementes e confere a reprodução da sequência principal."""
    medias_por_semente: dict[int, list[float]] = {}
    medias_e2 = []
    trajetorias_e2: list[Mapping[str, object]] = []
    for semente in SEMENTES_MEDIAS:
        if semente == SEMENTE_PRINCIPAL:
            rodadas = rodadas_2026
        else:
            rodadas = simular_rodadas(QUANTIDADE_RODADAS, semente)
        medias = calcular_medias_acumuladas(rodadas)
        medias_por_semente[semente] = [linha["lucro_medio_acumulado"] for linha in medias]

        medias_e2.append({
            "semente": semente,
            "media_100": medias[99]["lucro_medio_acumulado"],
            "media_1000": medias[999]["lucro_medio_acumulado"],
            "media_10000": medias[9999]["lucro_medio_acumulado"],
        })
        for linha in medias:
            trajetorias_e2.append({"semente": semente, **linha})

    escrever_csv(pasta_resultados / "experimento2_medias.csv", medias_e2)
    escrever_csv(pasta_resultados / "experimento2_trajetorias.csv", trajetorias_e2)

    repeticao_2026 = simular_rodadas(QUANTIDADE_REPRODUCAO, SEMENTE_PRINCIPAL)
    reproducao = []
    for indice in range(QUANTIDADE_REPRODUCAO):
        resultado_original = rodadas_2026[indice]["combinacao"]
        resultado_repetido = repeticao_2026[indice]["combinacao"]
        reproducao.append({
            "rodada": indice + 1,
            "resultado_original": resultado_original,
            "resultado_repetido": resultado_repetido,
            "igual": resultado_original == resultado_repetido,
        })
    escrever_csv(pasta_resultados / "experimento2_reproducao.csv", reproducao)

    return medias_por_semente


def executar_experimento_sessoes(
    pasta_resultados: Path,
) -> tuple[ResumoSessoes, list[Trajetoria]]:
    """E3: usa um gerador contínuo entre os participantes e exporta os saldos."""
    sessoes, trajetorias = simular_sessoes()
    resumo_e3 = resumir_sessoes(sessoes)
    escrever_csv(pasta_resultados / "experimento3_sessoes.csv", sessoes)
    escrever_csv(pasta_resultados / "experimento3_resumo.csv", [resumo_e3])
    linhas_trajetorias = []
    for trajetoria in trajetorias[:QUANTIDADE_TRAJETORIAS]:
        for numero, saldo in enumerate(trajetoria["saldos"]):
            linhas_trajetorias.append({
                "participante": trajetoria["participante"],
                "rodada": numero,
                "saldo": saldo,
            })
    escrever_csv(pasta_resultados / "experimento3_trajetorias.csv", linhas_trajetorias)

    return resumo_e3, trajetorias


def executar_experimento_pares(
    pasta_resultados: Path, rodadas_2026: Sequence[RodadaNumerada],
) -> None:
    """E4: examina os pares consecutivos da sequência principal."""
    tabela_e4 = analisar_pares(rodadas_2026)
    escrever_csv(pasta_resultados / "experimento4_pares.csv", tabela_e4)


def executar_experimento_pagamentos(
    pasta_resultados: Path, rodadas_2026: Sequence[RodadaNumerada],
) -> None:
    """E5: compara os pagamentos nas mesmas combinações do E1."""
    comparacao_e5 = comparar_pagamentos(rodadas_2026)
    escrever_csv(pasta_resultados / "experimento5_comparacao.csv", comparacao_e5["resumo"])
    escrever_csv(pasta_resultados / "experimento5_rodadas.csv", comparacao_e5["rodadas"])


def registrar_ambiente(pasta_resultados: Path) -> None:
    """Registra as versões usadas na execução e as sementes dos experimentos."""
    import matplotlib

    ambiente = [{
        "python": platform.python_version(),
        "sistema_operacional": platform.platform(),
        "gerador": "random.Random (Mersenne Twister)",
        "matplotlib": matplotlib.__version__, # type: ignore
        "semente_e1": SEMENTE_PRINCIPAL,
        "sementes_e2": ", ".join(str(semente) for semente in SEMENTES_MEDIAS),
        "semente_e3": SEMENTE_SESSOES,
    }]
    escrever_csv(pasta_resultados / "ambiente.csv", ambiente)


def mostrar_resultados(
    pasta_resultados: Path, resumo_e1: ResumoRodadas, resumo_e3: ResumoSessoes,
) -> None:
    """Mostra um tabuleiro de exemplo e os principais totais da execução."""
    exemplo = montar_rodada([1, 3, 4])
    print("Simulador acadêmico - somente créditos fictícios")
    print("Exemplo de tabuleiro (linha central avaliada):")
    for linha in exemplo["tabuleiro"]:
        print(" | ".join(linha))
    print(f"Linha central: {exemplo['combinacao']}")
    print(f"Prêmio bruto: {exemplo['premio']} crédito(s); lucro líquido: {exemplo['lucro']} crédito(s)")
    print(f"E1: lucro médio {resumo_e1['lucro_medio']:.4f}; RTP observado {resumo_e1['rtp_observado']:.4%}")
    print(f"E3: {resumo_e3['ganhos']} ganhos, {resumo_e3['empates']} empates e {resumo_e3['perdas']} perdas")
    print(f"Arquivos salvos em: {pasta_resultados}")


def executar_experimentos(pasta_resultados: str | PathLike[str] | None = None) -> None:
    """Executa os cinco experimentos e salva as tabelas e os gráficos."""
    if pasta_resultados is None:
        pasta = Path(__file__).resolve().parent / "resultados"
    else:
        pasta = Path(pasta_resultados)
    pasta.mkdir(parents=True, exist_ok=True)
    pastas_experimentos = {
        numero: _criar_pasta_experimento(pasta, numero)
        for numero in range(1, 6)
    }

    # A sequência principal é compartilhada por E1, E2, E4 e E5.
    rodadas_2026 = simular_rodadas(QUANTIDADE_RODADAS, SEMENTE_PRINCIPAL)
    frequencias, resumo_e1 = executar_experimento_frequencias(pastas_experimentos[1], rodadas_2026)
    medias_por_semente = executar_experimento_medias(pastas_experimentos[2], rodadas_2026)
    resumo_e3, trajetorias = executar_experimento_sessoes(pastas_experimentos[3])
    executar_experimento_pares(pastas_experimentos[4], rodadas_2026)
    executar_experimento_pagamentos(pastas_experimentos[5], rodadas_2026)
    registrar_ambiente(pasta)
    salvar_graficos(pasta, frequencias, medias_por_semente, trajetorias)
    mostrar_resultados(pasta, resumo_e1, resumo_e3)


def _criar_pasta_experimento(pasta_resultados: Path, numero: int) -> Path:
    """Cria e retorna a pasta dos arquivos de um experimento."""
    pasta = pasta_resultados / f"experimento_{numero}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


if __name__ == "__main__":
    executar_experimentos()
