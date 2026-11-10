# Procedência e migração dos materiais

Este índice evita duas confusões: documento antigo com status desatualizado e arquivo de prova confundido com decisão aprovada. Parte dos scripts, fixtures e recibos foi migrada para [`poc/`](../poc/EVIDENCE.md). O acervo operacional bruto de 44 casos ainda não foi copiado. Os títulos abaixo identificam materiais que permanecem no acervo privado; **eles não são caminhos nem arquivos disponíveis neste repositório**.

Para repetir **C arquivado** e **A local** no computador de trabalho, use os insumos publicados e o [runbook](RUNBOOK.md); não é necessário reconstruir o acervo privado nem redesenhar o processo empresarial já descrito em [Arquitetura](ARCHITECTURE.md). O material ausente limita a repetição integral dos 44 casos e das provas BMAD, sem invalidar os ensaios publicados. B/Diun e Vunnel permanecem alternativas estudadas, não decisões de adoção.

| Material local | Uso nesta síntese | Estado de importação |
|---|---|---|
| Acervo privado: `Gerenciamento end-to-end de imagens-base.md` | Cadeia AS-IS informada, rebuild diário, gates e consumidores. | Resumido sem nomes de organização. Original permanece no acervo local. |
| Acervo privado: `Visões de processo e decisão.md` | Separação AS-IS/TO-BE e papel proposto da inteligência. | Resumido em `ARCHITECTURE.md`; não tratado como implantação aprovada. |
| Relatório do caso histórico de imagem | Par de digests e pacote corrigido. | Relatório privado; [seleção dos digests e capturas](../poc/experiments/historical-image-case-20261107/evidence/digests/selection.json) publicada em `poc/`. |
| Comparação operacional A/B/C | Rotas direta e com ferramentas, 44 casos e limites. | Relatório e capturas completas privados; [44 linhas classificadas](../poc/experiments/operational-abc-comparison-20261108/evidence/C/rows.json), recibos selecionados e scripts A/B publicados. Não é replay integral. |
| Revisão do caso de digest público | Contestação da extensão pública. | Relatório privado; limites incorporados em [Status](STATUS.md) e [Resultados](POC.md), com [recibo selecionado](../poc/experiments/operational-abc-comparison-20261108/evidence/C/public-pipeline-20261108-verified/receipt.json) publicado. |
| Relatório da toolchain BMAD | Instalação e inventário BMAD/CIS/TEA/Loop. | Resumido em [Workflows](WORKFLOWS.md); comandos, logs e recibos não publicados. |
| Revisão do desenho de workflows | Desenho e contestação dos fluxos. | Resumida como proposta em [Workflows](WORKFLOWS.md), não como execução. |
| Plano de contexto e Loop sintético | Checkpoint, escopo, tentativa e limites. | Resumido em [Workflows](WORKFLOWS.md); provas de execução não incluídas neste pacote. |
| Contrato de workflow SSDLC | Arquivos, gates e handoffs propostos. | Referência de desenho em [Workflows](WORKFLOWS.md); não é workflow funcional publicado. |

## Regra de atualização

Antes de mudar um estado de **proposto** para **provado**, vincule entrada, comando, saída, teste e recibo da execução. Para publicar evidência bruta aqui, faça revisão de dados internos e de licenças. A documentação pública deve continuar legível mesmo sem acesso ao acervo local.
