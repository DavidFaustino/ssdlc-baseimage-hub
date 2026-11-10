# Procedência e migração dos materiais

Este índice evita duas confusões: documento antigo com status desatualizado e arquivo de prova confundido com decisão aprovada. Parte dos scripts, fixtures e recibos foi migrada para [`poc/`](../poc/EVIDENCE.md). O acervo operacional bruto de 44 casos ainda não foi copiado. Os dois primeiros materiais são identificados somente pelo título, pois pertencem a um acervo privado.

| Material local | Uso nesta síntese | Estado de importação |
|---|---|---|
| Acervo privado: `Gerenciamento end-to-end de imagens-base.md` | Cadeia AS-IS informada, rebuild diário, gates e consumidores. | Resumido sem nomes de organização. Original permanece no acervo local. |
| Acervo privado: `Visões de processo e decisão.md` | Separação AS-IS/TO-BE e papel proposto da inteligência. | Resumido em `ARCHITECTURE.md`; não tratado como implantação aprovada. |
| `2_pocs/base_image_hub/experiments/historical-image-case-20261107/RESULTS.md` | Par de digests e pacote corrigido no caso histórico. | Resumido em `POC.md`; evidência bruta permanece local. |
| `2_pocs/base_image_hub/experiments/operational-abc-comparison-20261108/COMPARISON.md` | Comparação final das rotas direta e com ferramentas, com 44 casos e limites. | Resumido em `POC.md`; linhas e recibos permanecem locais. |
| `2_pocs/base_image_hub/experiments/operational-abc-comparison-20261108/PUBLIC-PIPELINE-REVIEW.md` | Revisão independente da extensão pública. | Limites incorporados em `STATUS.md` e `POC.md`. |
| `2_pocs/base_image_hub/experiments/bmad-toolchain-20261107/RESULTS.md` | Instalação e inventário BMAD/CIS/TEA/Loop. | Resumido em `WORKFLOWS.md`. |
| `2_pocs/base_image_hub/experiments/workflow-design-20261107/RESULTS-v0.2.md` | Desenho e revisão dos fluxos SSDLC. | Resumido como proposta, não execução. |
| `2_pocs/base_image_hub/experiments/bmad-loop-context-options-20261107/PLAN.md` | Checkpoint, escopo e execução sintética; limites semânticos. | Resumido em `WORKFLOWS.md`. |
| `2_pocs/base_image_hub/workflows/ssdlc-local/WORKFLOW.md` | Contrato detalhado de arquivos, gates e handoffs. | Referência de desenho; não copiado como workflow funcional. |

## Regra de atualização

Antes de mudar um estado de **proposto** para **provado**, vincule entrada, comando, saída, teste e recibo da execução. Para publicar evidência bruta aqui, faça revisão de dados internos e de licenças. A documentação pública deve continuar legível mesmo sem acesso ao acervo local.
