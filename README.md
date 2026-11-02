# Parte 1 — Simulador da Máquina Estatística

Este pacote contém o simulador em Python, as tabelas CSV, os gráficos e testes automáticos. Não inclui o relatório.

## Integrantes

- Programação e simulação: Enzo Hubner Moura de Andrade, Kaio Marroque e Gabriel Brunetti.

## Como executar

É necessário ter Python 3.10 ou superior. Para executar os experimentos completos e gerar os gráficos, instale também a biblioteca Matplotlib. Os cálculos e testes podem ser executados sem ela.

No Windows, pelo PowerShell, execute:

```bash
py -m pip install -r requirements.txt
py simulador.py
```

No Linux ou WSL, abra um terminal na pasta do projeto e crie um ambiente virtual para instalar as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python simulador.py
```

Em novos terminais, ative novamente o ambiente com `source .venv/bin/activate` antes de executar o simulador. Para sair do ambiente virtual, use `deactivate`.

Se a criação do ambiente informar que o módulo `venv` ou `ensurepip` não está disponível, no Ubuntu ou Debian instale o pacote e repita o comando de criação:

```bash
sudo apt install python3-venv
```

O programa mostra uma rodada de exemplo e salva os arquivos em `resultados/`. Cada experimento tem sua própria pasta; `ambiente.csv` fica na raiz.

Para executar as verificações automáticas:

```bash
py -m unittest discover -s tests -v
```

No Linux ou WSL, com o ambiente virtual ativo, use `python -m unittest discover -s tests -v`.

## Regras implementadas

- Cada rolo usa a sequência circular A, B, C, D, E.
- Cada rodada sorteia uma parada independente para cada um dos três rolos.
- A aposta é de 1 crédito fictício; somente a linha central pode pagar.
- O prêmio é bruto. O lucro líquido é calculado como prêmio menos a aposta.
- O programa não usa dinheiro real, não altera as chances e não tenta prever resultados.

## Experimentos e arquivos

| Experimento                        | Arquivos principais                                                                                                                                     |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1 — 10.000 rodadas, semente 2026  | `resultados/experimento_1/experimento1_rodadas.csv`, `experimento1_frequencias.csv`, `experimento1_resumo.csv`, `experimento1_frequencias.png`          |
| E2 — sementes 10, 2026 e 123456    | `resultados/experimento_2/experimento2_medias.csv`, `experimento2_trajetorias.csv`, `experimento2_reproducao.csv`, `experimento2_medias_acumuladas.png` |
| E3 — 100 participantes, semente 42 | `resultados/experimento_3/experimento3_sessoes.csv`, `experimento3_resumo.csv`, `experimento3_trajetorias.csv`, `experimento3_trajetorias.png`          |
| E4 — pares consecutivos do E1      | `resultados/experimento_4/experimento4_pares.csv`                                                                                                       |
| E5 — pagamentos base e +10%        | `resultados/experimento_5/experimento5_comparacao.csv`, `experimento5_rodadas.csv`                                                                      |
| Ambiente                           | `resultados/ambiente.csv`                                                                                                                               |

Os nomes dos arquivos são preservados dentro de cada pasta de experimento. Os CSVs usam ponto e vírgula como separador. No E2, a sequência de 2026 é a mesma do E1. No E3, o gerador iniciado em 42 continua entre os participantes. O E4 usa os 9.999 pares da sequência de 10.000 rodadas do E1. O E5 reaplica as duas tabelas de pagamentos às mesmas rodadas. Executar o simulador mais de uma vez sobrescreve os arquivos existentes.

## Figuras no relatório

Os gráficos exportados contêm apenas eixos, unidades, categorias e legendas de identificação.

- Figura 1 — Probabilidades teóricas e frequências observadas em 10.000 rodadas (semente 2026).
- Figura 2 — Evolução do lucro médio acumulado para as sementes 10, 2026 e 123456, com referência teórica de −0,16 crédito por rodada.
- Figura 3 — Evolução do saldo dos cinco primeiros participantes, incluindo o saldo inicial e sua manutenção após o encerramento da sessão.

Fonte para as três figuras: elaboração própria, com dados do simulador da Máquina Estatística.

## Estrutura do código

O código é procedural, com funções em português e três responsabilidades. As funções têm anotações de tipos; os registros continuam sendo dicionários comuns em execução:

| Arquivo                     | Responsabilidade                                                                                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/tipos.py`              | Contratos dos registros com `TypedDict`, usados nas anotações de tipos.                                                                                                                                    |
| `src/calculos.py`           | Constantes, regras da máquina, sorteios, sessões e análises dos cinco experimentos. Não lê nem grava arquivos e não depende de Matplotlib.                                                                 |
| `src/exportacao.py`         | Escrita dos CSVs e geração dos três gráficos. Matplotlib é carregado somente ao gerar gráficos.                                                                                                            |
| `simulador.py`              | Entrada do programa e organização da execução, com uma função por experimento, registro do ambiente e apresentação dos resultados. Também mantém disponíveis as funções anteriores via `import simulador`. |
| `tests/testar_simulador.py` | Testes de regras, sementes, sessões, análises, layout dos resultados e importação sem Matplotlib.                                                                                                          |

Para estudar, comece pelas constantes e por `montar_rodada`, `fazer_rodada` e `simular_rodadas` em `src/calculos.py`. Depois leia as funções de análise e de sessões nesse mesmo arquivo. Em `simulador.py`, leia `executar_experimentos` para entender a ordem dos cinco experimentos e, em seguida, a função de cada experimento. Termine com `escrever_csv` e `salvar_graficos` em `src/exportacao.py` e com os testes.

A sequência principal é sorteada uma vez e compartilhada por E1, E2, E4 e E5. A comparação de pagamentos percorre os resultados na ordem recebida; o identificador de uma rodada não precisa corresponder à sua posição na lista.

## Uso de inteligência artificial

A inteligência artificial foi usada como apoio na elaboração inicial do código, do README e dos testes. O grupo conferiu as regras da máquina, os pagamentos e o cálculo do lucro, a reprodução dos resultados pelas sementes e os resultados dos testes automáticos.
