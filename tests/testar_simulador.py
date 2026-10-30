import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import simulador
from src.tipos import IdentificacaoRodada, ResultadoPremiado


class TestesDaMaquina(unittest.TestCase):
    def test_combinacao_igual_paga_premio_bruto_e_lucro(self) -> None:
        rodada = simulador.montar_rodada([0, 0, 0])

        self.assertEqual(rodada["centro"], ["B", "B", "B"])
        self.assertEqual(rodada["premio"], 10)
        self.assertEqual(rodada["lucro"], 9)

    def test_rolo_circular_volta_do_ultimo_simbolo_ao_primeiro(self) -> None:
        rodada = simulador.montar_rodada([4, 4, 4])

        self.assertEqual(rodada["tabuleiro"], [
            ["E", "E", "E"],
            ["A", "A", "A"],
            ["B", "B", "B"],
        ])

    def test_mesma_semente_repete_as_rodadas(self) -> None:
        primeira = simulador.simular_rodadas(10, 2026)
        segunda = simulador.simular_rodadas(10, 2026)

        self.assertEqual(primeira, segunda)

    def test_semente_2026_preserva_sequencia_original(self) -> None:
        rodadas = simulador.simular_rodadas(10, 2026)

        self.assertEqual([rodada["combinacao"] for rodada in rodadas], [
            "B-D-A", "A-B-C", "A-A-A", "E-A-A", "E-A-E",
            "C-B-A", "B-B-D", "B-E-B", "E-D-C", "E-D-D",
        ])

    def test_gerador_das_sessoes_continua_entre_participantes(self) -> None:
        sessoes, trajetorias = simulador.simular_sessoes(
            quantidade=3, saldo_inicial=10, max_rodadas=30, semente=42,
        )

        self.assertEqual([sessao["rodadas"] for sessao in sessoes], [25, 10, 10])
        self.assertEqual([sessao["saldo_final"] for sessao in sessoes], [0, 0, 0])
        self.assertTrue(all(len(trajetoria["saldos"]) == 31 for trajetoria in trajetorias))

    def test_importacao_e_calculos_dispensam_matplotlib(self) -> None:
        processo = subprocess.run(
            [sys.executable, "-c", (
                "import sys; sys.modules['matplotlib'] = None; "
                "import simulador; "
                "assert simulador.montar_rodada([0, 0, 0])['premio'] == 10"
            )],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True, text=True,
        )

        self.assertEqual(processo.returncode, 0, processo.stderr)

    def test_experimento_1_tem_dez_mil_resultados(self) -> None:
        rodadas = simulador.simular_rodadas(10000, 2026)
        frequencias = simulador.contar_frequencias(rodadas)
        resumo = simulador.calcular_resumo(rodadas)

        self.assertEqual(sum(linha["contagem"] for linha in frequencias), 10000)
        self.assertEqual(resumo["quantidade"], 10000)
        self.assertIn("lucro_teorico", resumo)
        self.assertTrue(math.isclose(resumo["lucro_teorico"], -0.16))
        self.assertGreaterEqual(resumo["desvio_padrao"], 0)

    def test_experimento_3_tem_cem_participantes_e_no_maximo_500_rodadas(self) -> None:
        sessoes, trajetorias = simulador.simular_sessoes()

        self.assertEqual(len(sessoes), 100)
        self.assertEqual(len(trajetorias), 100)
        self.assertTrue(all(sessao["rodadas"] <= 500 for sessao in sessoes))
        self.assertTrue(all(not sessao["esgotou"] or sessao["saldo_final"] < 1
                            for sessao in sessoes))
        self.assertEqual(sum(sessao["resultado"] in ("ganho", "empate", "perda")
                             for sessao in sessoes), 100)

    def test_experimento_4_usa_9999_pares(self) -> None:
        rodadas = simulador.simular_rodadas(10000, 2026)
        tabela = simulador.analisar_pares(rodadas)

        self.assertEqual(sum(linha["total_pares"] for linha in tabela), 9999)

    def test_grupo_sem_pares_nao_divide_por_zero(self) -> None:
        rodadas: list[ResultadoPremiado] = [{"premiada": False} for _ in range(4)]
        tabela = simulador.analisar_pares(rodadas)

        grupo_apos_premio = tabela[0]
        self.assertEqual(grupo_apos_premio["total_pares"], 0)
        self.assertIsNone(grupo_apos_premio["proporcao_premiada"])

    def test_experimento_5_confere_rtp_teorico(self) -> None:
        rodadas = simulador.simular_rodadas(10000, 2026)
        comparacao = simulador.comparar_pagamentos(rodadas)["resumo"]

        self.assertTrue(math.isclose(comparacao[0]["rtp_teorico"], 0.84))
        self.assertTrue(math.isclose(comparacao[1]["rtp_teorico"], 0.924))
        self.assertIn("lucro_teorico", comparacao[0])
        self.assertIn("lucro_teorico", comparacao[1])
        self.assertTrue(math.isclose(comparacao[0]["lucro_teorico"], -0.16))
        self.assertTrue(math.isclose(comparacao[1]["lucro_teorico"], -0.076))

    def test_pagamentos_preservam_ordem_e_identificadores_das_rodadas(self) -> None:
        rodadas: list[IdentificacaoRodada] = [
            {"rodada": 20, "combinacao": "A-A-A"},
            {"rodada": -3, "combinacao": "B-C-D"},
            {"rodada": 20, "combinacao": "E-E-E"},
        ]

        comparacao = simulador.comparar_pagamentos(rodadas)

        self.assertEqual(comparacao["rodadas"], [
            {"rodada": 20, "linha_central": "A-A-A", "premio_base": 5,
             "lucro_base": 4, "premio_mais_10": 5.5, "lucro_mais_10": 4.5},
            {"rodada": -3, "linha_central": "B-C-D", "premio_base": 0,
             "lucro_base": -1, "premio_mais_10": 0, "lucro_mais_10": -1},
            {"rodada": 20, "linha_central": "E-E-E", "premio_base": 50,
             "lucro_base": 49, "premio_mais_10": 50 * 1.10, "lucro_mais_10": 50 * 1.10 - 1},
        ])
        self.assertEqual(list(comparacao["rodadas"][0]), [
            "rodada", "linha_central", "premio_base", "lucro_base",
            "premio_mais_10", "lucro_mais_10",
        ])

    def test_layout_dos_arquivos_por_experimento(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            pastas = [raiz / f"experimento_{numero}" for numero in range(1, 6)]
            def criar_png(pasta: Path, nome: str, *_args: object) -> None:
                (pasta / nome).touch()

            with (
                patch("src.exportacao.salvar_grafico_frequencias", side_effect=lambda pasta, dados: criar_png(pasta, "experimento1_frequencias.png", dados)),
                patch("src.exportacao.salvar_grafico_medias", side_effect=lambda pasta, dados: criar_png(pasta, "experimento2_medias_acumuladas.png", dados)),
                patch("src.exportacao.salvar_grafico_trajetorias", side_effect=lambda pasta, dados: criar_png(pasta, "experimento3_trajetorias.png", dados)),
                patch("simulador.registrar_ambiente", side_effect=lambda pasta: simulador.escrever_csv(pasta / "ambiente.csv", [{"python": "teste"}])),
                patch("simulador.mostrar_resultados"),
            ):
                simulador.executar_experimentos(raiz)

            self.assertTrue((pastas[0] / "experimento1_rodadas.csv").is_file())
            self.assertTrue((pastas[0] / "experimento1_frequencias.png").is_file())
            self.assertTrue((pastas[1] / "experimento2_medias_acumuladas.png").is_file())
            self.assertTrue((pastas[2] / "experimento3_trajetorias.png").is_file())
            self.assertTrue((pastas[3] / "experimento4_pares.csv").is_file())
            self.assertTrue((pastas[4] / "experimento5_rodadas.csv").is_file())
            self.assertEqual([arquivo.name for arquivo in raiz.iterdir() if arquivo.is_file()], ["ambiente.csv"])



if __name__ == "__main__":
    unittest.main()
