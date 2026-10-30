"""Regras da máquina, sorteios e análises, sem acesso a arquivos ou gráficos."""

import random
import statistics
from collections.abc import Mapping, Sequence
from typing import Literal

from src.tipos import (
    AnalisePares, ComparacaoPagamentos, Frequencia, IdentificacaoRodada,
    MediaAcumulada, PagamentoRodada, ResultadoPremiado, ResumoPagamento,
    ResumoRodadas, ResumoSessoes, ResultadoRodada, Rodada, RodadaNumerada, Sessao, Trajetoria,
)

SIMBOLOS = ["A", "B", "C", "D", "E"]
PREMIOS = {
    "A-A-A": 5,
    "B-B-B": 10,
    "C-C-C": 15,
    "D-D-D": 25,
    "E-E-E": 50,
}
APOSTA = 1
TOTAL_RESULTADOS_TEORICOS = 125
QUANTIDADE_RODADAS = 10000
SEMENTE_PRINCIPAL = 2026
SEMENTES_MEDIAS = (10, SEMENTE_PRINCIPAL, 123456)
QUANTIDADE_PARTICIPANTES = 100
SALDO_INICIAL = 100
MAX_RODADAS_SESSAO = 500
SEMENTE_SESSOES = 42
QUANTIDADE_REPRODUCAO = 10
QUANTIDADE_TRAJETORIAS = 5


def montar_rodada(
    paradas: Sequence[int], tabela_premios: Mapping[str, float] | None = None,
) -> Rodada:
    """Monta o tabuleiro a partir das três posições sorteadas."""
    if tabela_premios is None:
        tabela_premios = PREMIOS

    colunas = []
    for parada in paradas:
        coluna = []
        for deslocamento in range(3):
            posicao = (parada + deslocamento) % len(SIMBOLOS)
            coluna.append(SIMBOLOS[posicao])
        colunas.append(coluna)

    tabuleiro = [
        [colunas[0][0], colunas[1][0], colunas[2][0]],
        [colunas[0][1], colunas[1][1], colunas[2][1]],
        [colunas[0][2], colunas[1][2], colunas[2][2]],
    ]
    centro = tabuleiro[1]
    combinacao = "-".join(centro)
    premio = tabela_premios.get(combinacao, 0)

    return {
        "tabuleiro": tabuleiro,
        "centro": centro,
        "combinacao": combinacao,
        "premio": premio,
        "lucro": premio - APOSTA,
        "premiada": premio > 0,
    }


def fazer_rodada(
    gerador: random.Random, tabela_premios: Mapping[str, float] | None = None,
) -> Rodada:
    """Sorteia uma posição para cada rolo e calcula o resultado."""
    paradas = []
    for _ in range(3):
        paradas.append(gerador.randrange(len(SIMBOLOS)))
    return montar_rodada(paradas, tabela_premios)


def simular_rodadas(quantidade: int, semente: int) -> list[RodadaNumerada]:
    """Executa rodadas com um gerador iniciado uma única vez pela semente."""
    gerador = random.Random(semente)
    rodadas: list[RodadaNumerada] = []

    for numero in range(1, quantidade + 1):
        rodada = fazer_rodada(gerador)
        rodada_numerada: RodadaNumerada = {**rodada, "rodada": numero}
        rodadas.append(rodada_numerada)

    return rodadas


def contar_frequencias(rodadas: Sequence[ResultadoRodada]) -> list[Frequencia]:
    """Conta as cinco triplas premiadas e reúne as demais em Sem prêmio."""
    contagens = {combinacao: 0 for combinacao in PREMIOS}
    contagens["Sem prêmio"] = 0

    for rodada in rodadas:
        if rodada["premiada"]:
            contagens[rodada["combinacao"]] += 1
        else:
            contagens["Sem prêmio"] += 1

    linhas: list[Frequencia] = []
    for combinacao, premio in PREMIOS.items():
        linhas.append({
            "resultado": combinacao,
            "premio_bruto": premio,
            "lucro_liquido": premio - APOSTA,
            "probabilidade_teorica": 1 / TOTAL_RESULTADOS_TEORICOS,
            "contagem": contagens[combinacao],
            "frequencia_relativa": contagens[combinacao] / len(rodadas),
        })

    linhas.append({
        "resultado": "Sem prêmio",
        "premio_bruto": 0,
        "lucro_liquido": -APOSTA,
        "probabilidade_teorica": 120 / TOTAL_RESULTADOS_TEORICOS,
        "contagem": contagens["Sem prêmio"],
        "frequencia_relativa": contagens["Sem prêmio"] / len(rodadas),
    })
    return linhas


def calcular_resumo(rodadas: Sequence[ResultadoRodada]) -> ResumoRodadas:
    """Calcula lucro médio, RTP observado, frequência de prêmio e desvio-padrão."""
    premios = [rodada["premio"] for rodada in rodadas]
    lucros = [rodada["lucro"] for rodada in rodadas]

    return {
        "quantidade": len(rodadas),
        "lucro_teorico": sum(PREMIOS.values()) / TOTAL_RESULTADOS_TEORICOS - APOSTA,
        "lucro_medio": statistics.mean(lucros),
        "rtp_observado": statistics.mean(premios),
        "proporcao_premiada": sum(rodada["premiada"] for rodada in rodadas) / len(rodadas),
        "desvio_padrao": statistics.stdev(lucros) if len(lucros) > 1 else 0,
    }


def calcular_medias_acumuladas(rodadas: Sequence[ResultadoRodada]) -> list[MediaAcumulada]:
    """Calcula a média do lucro após cada rodada."""
    linhas: list[MediaAcumulada] = []
    soma_lucros: float = 0

    for numero, rodada in enumerate(rodadas, start=1):
        soma_lucros += rodada["lucro"]
        linhas.append({
            "rodada": numero,
            "lucro_medio_acumulado": soma_lucros / numero,
        })

    return linhas


def simular_sessoes(
    quantidade: int = QUANTIDADE_PARTICIPANTES, saldo_inicial: float = SALDO_INICIAL,
    max_rodadas: int = MAX_RODADAS_SESSAO, semente: int = SEMENTE_SESSOES,
) -> tuple[list[Sessao], list[Trajetoria]]:
    """Simula participantes usando um único gerador contínuo iniciado na semente."""
    gerador = random.Random(semente)
    sessoes: list[Sessao] = []
    trajetorias: list[Trajetoria] = []

    for participante in range(1, quantidade + 1):
        saldo = saldo_inicial
        numero_rodadas = 0
        saldos = [saldo]

        while numero_rodadas < max_rodadas and saldo >= APOSTA:
            rodada = fazer_rodada(gerador)
            saldo += rodada["lucro"]
            numero_rodadas += 1
            saldos.append(saldo)

        esgotou = saldo < APOSTA
        resultado: Literal["ganho", "empate", "perda"]
        if saldo > saldo_inicial:
            resultado = "ganho"
        elif saldo == saldo_inicial:
            resultado = "empate"
        else:
            resultado = "perda"

        while len(saldos) < max_rodadas + 1:
            saldos.append(saldo)

        sessoes.append({
            "participante": participante,
            "saldo_final": saldo,
            "rodadas": numero_rodadas,
            "esgotou": esgotou,
            "resultado": resultado,
        })
        trajetorias.append({"participante": participante, "saldos": saldos})

    return sessoes, trajetorias


def resumir_sessoes(
    sessoes: Sequence[Sessao], saldo_inicial: float = SALDO_INICIAL,
) -> ResumoSessoes:
    """Resume ganhos, empates, perdas, esgotamentos e saldos finais."""
    ganhos = sum(sessao["resultado"] == "ganho" for sessao in sessoes)
    empates = sum(sessao["resultado"] == "empate" for sessao in sessoes)
    perdas = sum(sessao["resultado"] == "perda" for sessao in sessoes)
    esgotamentos = sum(sessao["esgotou"] for sessao in sessoes)
    saldos = [sessao["saldo_final"] for sessao in sessoes]

    return {
        "participantes": len(sessoes),
        "ganhos": ganhos,
        "empates": empates,
        "perdas": perdas,
        "proporcao_ganho": ganhos / len(sessoes),
        "proporcao_empate": empates / len(sessoes),
        "proporcao_perda": perdas / len(sessoes),
        "esgotamentos": esgotamentos,
        "proporcao_esgotamento": esgotamentos / len(sessoes),
        "proporcao_esgotamento_entre_perdas": esgotamentos / perdas if perdas else 0,
        "saldo_medio": statistics.mean(saldos),
        "saldo_mediano": statistics.median(saldos),
        "saldo_inicial": saldo_inicial,
    }


def analisar_pares(rodadas: Sequence[ResultadoPremiado]) -> list[AnalisePares]:
    """Compara a chance observada após prêmio e após resultado sem prêmio."""
    grupos = {
        "Após prêmio": {"total_pares": 0, "premios_na_proxima": 0},
        "Após resultado sem prêmio": {"total_pares": 0, "premios_na_proxima": 0},
    }

    for indice in range(len(rodadas) - 1):
        if rodadas[indice]["premiada"]:
            grupo = grupos["Após prêmio"]
        else:
            grupo = grupos["Após resultado sem prêmio"]

        grupo["total_pares"] += 1
        if rodadas[indice + 1]["premiada"]:
            grupo["premios_na_proxima"] += 1

    linhas: list[AnalisePares] = []
    for nome, grupo in grupos.items():
        total = grupo["total_pares"]
        linhas.append({
            "resultado_anterior": nome,
            "total_pares": total,
            "premios_na_rodada_seguinte": grupo["premios_na_proxima"],
            "proporcao_premiada": grupo["premios_na_proxima"] / total if total else None,
        })
    return linhas


def comparar_pagamentos(rodadas: Sequence[IdentificacaoRodada]) -> ComparacaoPagamentos:
    """Aplica as tabelas base e +10% às mesmas combinações sorteadas."""
    tabela_com_aumento = {combinacao: premio * 1.10 for combinacao, premio in PREMIOS.items()}
    tabelas: list[tuple[str, Mapping[str, float]]] = [
        ("Base", PREMIOS),
        ("Prêmios +10%", tabela_com_aumento),
    ]
    resultados_por_rodada: list[PagamentoRodada] = []
    for rodada in rodadas:
        premio_base = PREMIOS.get(rodada["combinacao"], 0)
        premio_mais_10 = tabela_com_aumento.get(rodada["combinacao"], 0)
        resultados_por_rodada.append({
            "rodada": rodada["rodada"],
            "linha_central": rodada["combinacao"],
            "premio_base": premio_base,
            "lucro_base": premio_base - APOSTA,
            "premio_mais_10": premio_mais_10,
            "lucro_mais_10": premio_mais_10 - APOSTA,
        })
    resumos: list[ResumoPagamento] = []

    for nome, tabela in tabelas:
        premios: list[float] = []
        lucros: list[float] = []

        for linha in resultados_por_rodada:
            premio = tabela.get(linha["linha_central"], 0)
            lucro = premio - APOSTA
            premios.append(premio)
            lucros.append(lucro)

        rtp_teorico = sum(tabela.values()) / TOTAL_RESULTADOS_TEORICOS
        resumos.append({
            "configuracao": nome,
            "probabilidade_teorica_premio": 5 / TOTAL_RESULTADOS_TEORICOS,
            "proporcao_premiada_observada": sum(premio > 0 for premio in premios) / len(premios),
            "premio_medio_observado": statistics.mean(premios),
            "lucro_medio_observado": statistics.mean(lucros),
            "rtp_teorico": rtp_teorico,
            "lucro_teorico": rtp_teorico - APOSTA,
            "rtp_observado": statistics.mean(premios),
        })

    return {"resumo": resumos, "rodadas": resultados_por_rodada}

