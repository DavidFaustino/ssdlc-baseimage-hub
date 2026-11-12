# POC de detecção de mudanças e avaliação de correções

Esta pasta reúne a **documentação da POC existente**: detectar que uma tag passou a apontar para outro conteúdo e avaliar uma correção de segurança num caso histórico. O material foi reorganizado sem apagar provas nem repetir os experimentos de coleta. A relocação foi conferida pela suíte unitária offline existente e pelos hashes das evidências.

O novo piloto Distroless é uma frente separada. Reproduzir esta POC pode ajudar a entender ou reaproveitar suas provas, mas **não é pré-requisito obrigatório para o piloto**, nem caminho de produção.

## O que ela demonstra

| Parte | Função e prova publicada | Limite |
|---|---|---|
| **A — consulta OCI direta** | Observar uma tag num registry local controlado; detectar troca e repetição sem novo evento nos ciclos verificados. | Não decide se um pacote está corrigido e não prova uma troca real de tag pública. |
| **B — Diun** | Observar a mesma mudança controlada com a ferramenta real; um aviso na troca e nenhum na repetição. | É alternativa de detecção a A, não ferramenta adotada nem etapa obrigatória. |
| **V — Vunnel** | Coletar a fonte Debian e consultar o registro de correção do caso. | Não inspeciona a imagem; a coleta nova usa feed atual e pode diferir da captura histórica. |
| **C — correlação e estado** | Relacionar observações, pacote, advisory e prova de conteúdo arquivados; registrar decisão e recuperar recibos sem duplicação. | É uma capacidade transversal de avaliação, não concorrente de A/B. O comando publicado lê quatro fontes congeladas, sem consumir automaticamente saídas novas de A, B ou V. |

O resultado `validate_candidate` encaminha uma candidata para validação; **não aprova, certifica ou publica a imagem**. A UI do Hub usa outro cenário demonstrativo e não recebe os resultados desses scripts.

## Como começar

1. **Entender o alcance:** leia [Estado da rodada](STATUS.md) e [Resultados e limites](POC.md). A tabela de resultados liga as afirmações aos scripts, entradas e recibos.
2. **Preparar e reproduzir:** siga o [Runbook técnico](RUNBOOK.md). Ele contém os pré-requisitos, comandos, entradas, processamento, saídas esperadas e diagnóstico. A ordem publicada é preparação → C1 (avaliação histórica) → C2 (recuperação) → A (detecção). B e V são experimentos adicionais disponíveis.
3. **Conferir sua execução:** use o [Checklist](EXECUCAO.md), compare os arquivos produzidos com os resultados esperados e registre diferenças. Um comando terminar não substitui a conferência das asserções e evidências indicadas.

**Diretório de execução:** o pacote de código agora está em `poc/deteccao-e-correcao/`, com sua hierarquia interna preservada. O runbook prepara o ambiente a partir da raiz do repositório e entra nesse pacote; execute os comandos no diretório indicado por ele, **não nesta pasta de documentação**. Use saídas novas e preserve os resultados antes da limpeza.

## Onde estão código, dados e contexto

| Material | Local e finalidade |
|---|---|
| Scripts, fixtures e testes | [`poc/deteccao-e-correcao/`](../../poc/deteccao-e-correcao/README.md), relativo à raiz do repositório. A hierarquia interna `experiments/` e `evidence/` foi preservada como unidade. |
| Arquivos incluídos e procedência | [Inventário de evidências](../../poc/deteccao-e-correcao/EVIDENCE.md) e [Fontes desta rodada](SOURCES.md). |
| Processo e encaixe considerados | [Arquitetura da rodada](ARCHITECTURE.md). Registro histórico; não define o processo atual, mantido na [arquitetura compartilhada](../processo/ARQUITETURA.md). |
| Planejamento histórico | [Próximas etapas registradas](NEXT-STEPS.md). Não é a fila atual do novo piloto. |
| Trabalho paralelo de desenvolvimento | [Workflows e BMAD](../apoio-workflows/README.md). Contexto separado, sem se tornar requisito para executar A/C. |

## O que não está reproduzível integralmente

A comparação histórica tem **44 casos: 6 completos e 38 parciais**, com limites nas próprias linhas. As capturas brutas e parte do executor original não foram publicadas; a inspeção integral dos 34 blobs também não está empacotada. É possível consultar recibos selecionados, mas **não recalcular os 44 casos integralmente só com esta cópia**.

Os comandos publicados demonstram provas separadas. O recibo integrado histórico não transforma A/B/V → C em um fluxo único executável, nem comprova implantação contínua, acesso ao proxy corporativo ou certificação. Consulte o runbook antes de interpretar um recibo arquivado como resultado da sua nova execução.
