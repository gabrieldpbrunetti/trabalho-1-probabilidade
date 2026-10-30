"""Contratos dos registros produzidos e consumidos pelos experimentos."""

from typing import Literal, TypedDict


class ResultadoPremiado(TypedDict):
    """Indica se uma rodada recebeu prêmio, informação usada na análise de pares."""

    premiada: bool


class CombinacaoRodada(TypedDict):
    """Representa a sequência de símbolos da linha central avaliada para pagamento."""

    combinacao: str


class IdentificacaoRodada(CombinacaoRodada):
    """Associa a combinação central ao número que identifica a rodada na simulação."""

    rodada: int


class ResultadoRodada(CombinacaoRodada, ResultadoPremiado):
    """Reúne o tabuleiro e o resultado financeiro de uma rodada, ainda sem numeração."""

    tabuleiro: list[list[str]]
    centro: list[str]
    premio: float
    lucro: float


class Rodada(ResultadoRodada, total=False):
    """Representa uma rodada cujo número é opcional, pois o sorteio precede a numeração."""

    rodada: int


class RodadaNumerada(ResultadoRodada, IdentificacaoRodada):
    """Representa o resultado completo de uma rodada já identificada na simulação."""



class Frequencia(TypedDict):
    """Compara a probabilidade teórica de um resultado com sua frequência observada."""

    resultado: str
    premio_bruto: float
    lucro_liquido: float
    probabilidade_teorica: float
    contagem: int
    frequencia_relativa: float


class ResumoRodadas(TypedDict):
    """Resume o retorno, o lucro e a dispersão dos resultados de um conjunto de rodadas."""

    quantidade: int
    lucro_teorico: float
    lucro_medio: float
    rtp_observado: float
    proporcao_premiada: float
    desvio_padrao: float


class MediaAcumulada(TypedDict):
    """Registra o lucro médio desde o início da simulação até a rodada indicada."""

    rodada: int
    lucro_medio_acumulado: float


class Sessao(TypedDict):
    """Representa a participação de um jogador até esgotar o saldo ou atingir o limite de rodadas."""

    participante: int
    saldo_final: float
    rodadas: int
    esgotou: bool
    resultado: Literal["ganho", "empate", "perda"]


class Trajetoria(TypedDict):
    """Registra a evolução do saldo de um participante, começando pelo saldo inicial."""

    participante: int
    saldos: list[float]


class ResumoSessoes(TypedDict):
    """Consolida ganhos, empates, perdas, esgotamentos e saldos finais dos participantes."""

    participantes: int
    ganhos: int
    empates: int
    perdas: int
    proporcao_ganho: float
    proporcao_empate: float
    proporcao_perda: float
    esgotamentos: int
    proporcao_esgotamento: float
    proporcao_esgotamento_entre_perdas: float
    saldo_medio: float
    saldo_mediano: float
    saldo_inicial: float


class AnalisePares(TypedDict):
    """Resume a ocorrência de prêmio na rodada seguinte, agrupada pelo resultado anterior."""

    resultado_anterior: str
    total_pares: int
    premios_na_rodada_seguinte: int
    proporcao_premiada: float | None


class PagamentoRodada(TypedDict):
    """Compara os prêmios e lucros da mesma rodada nas tabelas base e com aumento de 10%."""

    rodada: int
    linha_central: str
    premio_base: float
    lucro_base: float
    premio_mais_10: float
    lucro_mais_10: float


class ResumoPagamento(TypedDict):
    """Resume o retorno teórico e observado de uma configuração da tabela de prêmios."""

    configuracao: str
    probabilidade_teorica_premio: float
    proporcao_premiada_observada: float
    premio_medio_observado: float
    lucro_medio_observado: float
    rtp_teorico: float
    lucro_teorico: float
    rtp_observado: float


class ComparacaoPagamentos(TypedDict):
    """Reúne a comparação entre tabelas de prêmios, por configuração e por rodada."""

    resumo: list[ResumoPagamento]
    rodadas: list[PagamentoRodada]
