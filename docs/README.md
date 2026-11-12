# Documentação — pontos de entrada

**Para levar o piloto ao trabalho, comece pela [especificação do piloto Distroless](piloto-distroless/ESPECIFICACAO.md).** Ela define o resultado a construir e aponta para contexto, tarefas e execução. Não é necessário percorrer toda a pesquisa anterior.

| Assunto | Documento | O que você encontra |
|---|---|---|
| Processo compartilhado | [Arquitetura](processo/ARQUITETURA.md) | Três camadas, responsáveis, controles, publicações, identidade e divergências nas fontes. Única referência atual do processo neste repositório. |
| Incremento Distroless | [Especificação](piloto-distroless/ESPECIFICACAO.md) | Objetivo, escopo, mudanças, reaproveitamento, entregas e critérios de aceite. |
| Trabalho a implementar | [Plano](piloto-distroless/PLANO.md) | Tarefas, dependências e comprovação de cada entrega do piloto. |
| Preparação e execução no trabalho | [Guia de execução](piloto-distroless/EXECUCAO.md) | Insumos reais necessários e condições para executar; distingue o disponível das etapas ainda não implementadas. |
| Produto Hub | [Especificação da interface](hub/ESPECIFICACAO.md) | Telas, casos de uso, regras demonstrativas e futuras integrações. |
| Correspondência UI/processo | [Revisão da arquitetura na UI](hub/REVISAO-ARQUITETURA.md) | Diferenças encontradas; propostas congeladas até revisar o processo. |
| Experimentos anteriores | [POC de detecção e correção](poc-deteccao-e-correcao/README.md) | Resultados, runbook, evidências e limites das provas publicadas. |
| Reaproveitamento dos experimentos | [Análise de aproveitamento](poc-deteccao-e-correcao/ANALISE-APROVEITAMENTO.md) | O que pode complementar o fluxo e o que pode duplicar controles existentes. Não substitui a especificação do piloto. |
| Estudos de desenvolvimento | [Workflows e BMAD](apoio-workflows/README.md) | Material de apoio; não é requisito para rodar a POC nem motor do processo de imagens. |

## Regra de manutenção

O processo é mantido em `processo/ARQUITETURA.md`. O piloto documenta seu incremento; o Hub documenta como o produto representa e administra esse processo. Os registros da POC preservam o contexto histórico e não prevalecem sobre a referência atual. Uma mudança aprovada deve atualizar a referência e seus consumidores, sem copiar a arquitetura inteira entre pastas.

**Estados distintos:** prova executável, registro histórico, especificação a implementar e integração real. Um documento ou tela existente não comprova que a automação correspondente exista.
