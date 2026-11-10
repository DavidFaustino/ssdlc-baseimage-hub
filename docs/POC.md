# Resultados técnicos da POC

## Resposta curta

A POC mostrou que é possível **detectar uma troca controlada de digest**, relacionar o manifesto `linux/amd64` ao pacote `libexpat1` e à correção Debian, persistir uma decisão de **validar candidata** e retomá-la sem duplicação. Ela **não** implantou um monitor, certificou uma imagem ou decidiu adotar Diun/Vunnel. As execuções reproduzíveis deste repositório são separadas; o ensaio integrado anterior e a matriz de 44 casos são registros auditáveis, não uma execução integral portátil.

**Como ler as provas:** “reexecutável” abaixo significa que o comando e os insumos necessários estão publicados; “registro histórico” significa que há recibo ou resumo, mas não todos os insumos/executores para recalcular o resultado. O sucesso separado de A, B, Vunnel e C não demonstra que suas saídas já percorrem uma pipeline única.

O [runbook](RUNBOOK.md) explica as entradas, comandos, asserções e falhas. O [inventário](../poc/EVIDENCE.md) diz exatamente o que foi publicado e o que falta para repetir cada afirmação.

## Qual problema foi exercitado

Uma tag de imagem pode mudar, mas a correção está no **conteúdo da variante da plataforma**, não no nome da tag. O caso congelado usa dois manifestos históricos da mesma variante Distroless Java 21/Debian 13: `libexpat1` aparece antes e depois da versão corrigida para `CVE-2026-24515`. A tag `local-replay` foi servida por um registry local para simular a troca. **Não foi observada uma troca da tag pública.**

| Peça | Papel testado | Não faz sozinha |
|---|---|---|
| **A — OCI direto** | Consulta a tag, valida o índice e o filho `linux/amd64`, compara o digest com o baseline. | Não interpreta advisory nem aprova imagem. |
| **B — Diun** | Consulta a mesma tag local, persiste estado próprio e emite aviso na mudança. | O aviso ainda precisa ser resolvido e validado por plataforma; não prova pacote. |
| **Fonte Debian / Vunnel** | Entrega a versão de correção do pacote para a CVE selecionada. | Não observa nem inspeciona imagem. |
| **C — consumidor** | Confere identidade, fontes e versões, grava decisão e recibo em SQLite. | O script público atual não recebe saídas novas de A/B/Vunnel. |

## Afirmações e cadeia de evidências

| Cenário / afirmação | Entrada fixada | Executor / versão | Saída observável e limite |
|---|---|---|---|
| Par histórico contém `libexpat1` antes/depois do fix. | [Seleção](../poc/experiments/historical-image-case-20261107/evidence/digests/selection.json), [manifestos e status do pacote](../poc/experiments/historical-image-case-20261107/evidence/digests/). | Captura histórica preservada; a inspeção dirigida é verificada pelo [consumidor de contrato](../poc/experiments/tool-architecture-evaluation-20261108/evidence/A3-H4/consumer-contract.py). | [Prova de suite](../poc/experiments/tool-architecture-evaluation-20261108/evidence/A3-H4/suite-proof.json): 34 digests de camada únicos verificados; 33 camadas por manifesto. É inspeção **dirigida**, não inventário completo de pacotes ou certificação. |
| A detecta troca e repetição sem segundo evento. | Índices e filhos históricos da [fixture local](../poc/experiments/tool-architecture-evaluation-20261108/evidence/A3-H2/replay/). | [`probe.py`](../poc/experiments/operational-abc-comparison-20261108/scripts/A/probe.py) + [observador OCI](../poc/experiments/oci-observation-20261108/observe.py). | Execução nova gera `summary.json`, `events.jsonl`, `result.json` e `hashes.json`; 36 execuções, incluindo 3 ciclos principais. Registry apenas em `127.0.0.1`; não prova monitoramento contínuo ou tag pública mudando. |
| B emite um aviso na troca e nenhum na repetição. | Os mesmos índices/filhos, mais blobs de configuração históricos. | [`run_retained_b.py`](../poc/experiments/operational-abc-comparison-20261108/scripts/B/run_retained_b.py) + Diun **4.33.1** oficial conferido por checksum. | Execução nova gera `results.json`, `notifications.jsonl`, `receipt.json`, `diun.db` e corpos servidos; novos avisos `[0,1,0]`. Também usa loopback; aviso não equivale a decisão. |
| C relaciona evento, pacote, advisory e retoma sem duplicar. | Quatro fontes com hashes no [manifesto](../poc/experiments/integrated-update-poc-20261108/evidence/I0-H1/manifest.json). | [`run_local.py`](../poc/experiments/integrated-update-poc-20261108/run_local.py), [pipeline](../poc/experiments/integrated-update-poc-20261108/src/pipeline.py) e [schema](../poc/experiments/tool-architecture-evaluation-20261108/evidence/A3-H1/contract.schema.json). | Execução nova gera `state.sqlite`, `run.json`, `receipt.json`, `advisory-receipt.json`: baseline → uma decisão `validate_candidate` → repetição inalterada; reavaliação `already_satisfies_fix`; `image_approved=false`. O comando lê observações **arquivadas**, não as saídas recém-geradas de A/B. |
| Dados Debian direto e Vunnel coincidiram para a CVE/advisory selecionados no ensaio anterior. | Revisão de feed congelada e registro `CVE-2026-24515`/`DSA-6404-1` no [caso comparativo](../poc/experiments/operational-abc-comparison-20261108/evidence/C/rows.json). | Registro histórico de consulta Debian e Vunnel; o [script Vunnel publicado](../poc/experiments/operational-abc-comparison-20261108/scripts/B/measure_vunnel.py) fixa Vunnel **0.66.0**. | A coleta nova gera `receipt.json` e `workspace/` para o **feed atual**. Pode ter bytes e fix diferentes do snapshot antigo; não alimenta C automaticamente. |
| Digest público estável foi reavaliado sem decidir troca de imagem. | Captura pública selecionada com duas revisões de feed. | [pipeline público](../poc/experiments/integrated-update-poc-20261108/src/pipeline.py) no laboratório. | [Recibo arquivado](../poc/experiments/operational-abc-comparison-20261108/evidence/C/public-pipeline-20261108-verified/receipt.json): 1 observação, 2 reavaliações, 0 decisões de imagem, `image_approved=false`. Não há prova de troca pública nem de todas as CVEs da imagem. |
| A e B chegaram à mesma ação no ensaio integrado anterior. | Caso histórico e feed/ledger do laboratório original. | Execução anterior registrada em [`pipeline-replay.json`](../poc/experiments/operational-abc-comparison-20261108/evidence/C/pipeline-replay.json). | Em A e B: `decision_count=1`, `action=validate_candidate`, `image_approved=false`. O executor integrado e todas as entradas brutas não estão publicados, portanto este recibo é **auditável, não regenerável** pelos comandos deste PR. |

**Leitura do recibo:** `validate_candidate` encaminha a imagem para uma etapa posterior de validação. `already_satisfies_fix` é uma reavaliação do **mesmo digest** diante de uma revisão de advisory. Nenhuma das duas ações aprova ou publica uma imagem.

## Comparação A/B: resultado e alcance

A [matriz arquivada de 44 linhas](../poc/experiments/operational-abc-comparison-20261108/evidence/C/rows.json) classifica **6 completas e 38 parciais**; nenhuma falha ou bloqueio na classificação final. “Parcial” significa que a própria linha declara uma fronteira não equivalente ou uma prova incompleta. Não leia “44” como 44 decisões fim a fim reproduzíveis.

Nos [três pares locais com feed e ledger já em cache](../poc/experiments/operational-abc-comparison-20261108/evidence/C/cost-pairs.json), A e B registraram a mesma ação, uma vez por rodada. A fez **7 requisições por par**, B **16**; A também teve menor tempo total nos três pares. B inclui buscas de configuração pelo Diun e os custos de início não são idênticos. Esses números descrevem **essa carga local**, não custo de implementação, manutenção, operação corporativa ou um vencedor de arquitetura.

O resultado útil para o processo existente é o **contrato de evidência**: fixar digest e plataforma, vincular pacote e fonte Debian, rejeitar dados faltantes como `unknown`, e registrar recibo/estado sem aprovar a imagem. O valor adicional de Diun/Vunnel deve ser julgado frente aos agendamentos e gates que já existem no processo atual, conforme a [arquitetura](ARCHITECTURE.md).

## Limites de reprodução e procedência

- Os comandos A, B, Vunnel e C do runbook são **execuções separadas**. Não há comando publicado que pegue uma observação nova de A ou B, uma revisão nova de Vunnel e percorra C até a decisão.
- O ledger de camadas publicado foi saneado para remover caminhos locais; os hashes derivados da fixture C foram recalculados. O recibo integrado histórico tem hashes do **acervo original**, diferentes dos bytes públicos. O resultado semântico pode coincidir, mas não há cadeia criptográfica contínua entre ambos. Veja a [explicação no inventário](../poc/EVIDENCE.md).
- As capturas brutas que originaram as 44 linhas somam aproximadamente **211 MB** e não estão publicadas. Os 34 blobs brutos de camadas da leitura pública também não estão aqui.
- Não foram testados neste pacote o registry proxy corporativo, publicação, certificação, consumidores, operação contínua ou todas as distribuições/CVEs.

**Próxima lacuna técnica:** construir e testar a ligação entre produtores e C com entradas novas e recibos verificáveis, ou manter os ensaios separados como evidência de componentes. Isso é trabalho futuro, não resultado desta POC.
