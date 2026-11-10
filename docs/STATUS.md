# Marco atual — Base Image Hub e workflows

**Revisão:** 10 de novembro de 2026. Este é um ponto de retomada: o que foi observado, o que pode ser reproduzido neste repositório e o que continua aberto. **Prioridade atual:** reproduzir e aceitar as provas publicadas nesta cópia, no computador de trabalho. Depois, confrontar o resultado com o AS-IS documentado. Integração e evolução operacional do Hub vêm depois dessa revisão.

## Em uma leitura

A POC local mostrou que é possível vincular **digest da plataforma → pacote instalado → correção Debian → decisão registrada** no caso testado. Nesta cópia, **A** repete a detecção OCI e **C** repete a correlação sobre entradas históricas arquivadas; **B** é a alternativa Diun à detecção de A e **V** recolhe o feed pelo Vunnel. Essas provas são separadas e não formam uma execução A/B/V→C alimentada por saídas novas. O protótipo visual não executa a POC. O workflow completo com BMAD ainda é desenho; houve provas sintéticas de partes dele.

| Frente | Estado | Evidência e limite |
|---|---|---|
| Processo atual de imagens base | **Descrito, a validar no ambiente de destino.** | Há matriz diária de CI, ingestão/certificação, imagem de arquitetura, publicação e consumo. O ponto exato da nova informação e os gates reais precisam de validação com os responsáveis. [Arquitetura](ARCHITECTURE.md). |
| Caso histórico de pacote | **Comprovado localmente.** | Dois digests da mesma variante contêm `libexpat1` antes/depois da correção. Manifestos e arquivos selecionados estão em [`poc/`](../poc/EVIDENCE.md); isso não é uma troca observada hoje na tag pública. |
| Imagem pública | **Captura pontual.** | O laboratório vinculou digest estável, manifesto da plataforma, 34 camadas, pacote e advisory. Os 34 blobs completos não estão publicados aqui; não houve mudança pública de tag nem certificação. [Resultados](POC.md). |
| Entradas A/B e correlação C | **Provas locais, sem escolha de ferramenta.** | A e B detectaram a mesma troca histórica; C registrou decisão sem duplicação. Neste repositório, os scripts A/B e o núcleo C podem ser repetidos pelo [runbook](RUNBOOK.md). A matriz arquivada tem 44 casos (6 completos, 38 parciais), mas seus dados brutos integrais não estão aqui. |
| BMAD e Loop | **Instalação, desenho e provas sintéticas no acervo original.** | Há relato de 13 testes da fixture e de uma história sintética `done` com retomada. Os comandos, fixtures, logs e recibos dessa frente **não estão neste repositório**; ela não pode ser repetida por este runbook. O ciclo completo com história real de imagem base não foi executado. [Workflows](WORKFLOWS.md) e [fontes](SOURCES.md). |
| Protótipo visual | **Demonstrativo.** | `index.html` apresenta três runs DEMO coerentes em Visão geral, Imagens, Automações e Adoção: um concluído com gate e publicação ilustrativos, um build bloqueado e uma fonte indisponível. Pedidos geram apenas recibos locais no navegador. O Roadmap continua a separar descoberta, validação e evolução proposta. O [HTML independente da POC](../poc/overview.html) permanece artefato de consulta. Não há backend ou integração com scripts, CI, registry, proxy, scanners, ECR ou EKS; digests e artefatos exibidos são sintéticos. |

## Validação da prévia operacional

A revisão independente no Chrome percorreu as seis telas, oito fichas de imagem, três execuções DEMO, cinco tipos de artefato, confirmações e cancelamentos de pedidos, filtros, detalhes da Arquitetura e do Roadmap. Também verificou a navegação móvel em 390 × 844 px. A rodada inicial encontrou seis defeitos; eles foram corrigidos e os percursos afetados foram repetidos na prévia republicada.

As correções conferidas foram: atualização imediata do histórico de pedidos; retorno do foco ou foco no recibo; contador singular de execução; plataforma desconhecida sem valor presumido; navegação entre base e derivada; e ausência de certificação positiva nas imagens sem execução/evidência vinculada. Não foram observados novos defeitos nesses percursos de regressão. Isso valida a interação do cenário demonstrativo, não a integração com os sistemas corporativos.

Para conferir a interface por conta própria, abra [`index.html`](../index.html) no navegador e siga:

1. Em **Visão geral**, abra a fase Segunda camada, a execução bloqueada e sua imagem. Confira motivo, gate não avaliado e ausência de publicação.
2. Na ficha da derivada, abra a base de origem e volte à derivada. Os vínculos são sintéticos e devem permanecer identificados como DEMO.
3. Na execução, simule um pedido: primeiro cancele, depois confirme. Confira o recibo, o retorno do foco e o histórico atualizado sem trocar de tela. Nenhum workflow externo é executado.
4. Em **Imagens**, filtre certificadas e registros sem evidência. A imagem sem execução vinculada não pode apresentar certificação concluída; a fonte desconhecida não pode afirmar plataforma resolvida.

## O que fazer com esta entrega agora

1. Conferir [as evidências incluídas](../poc/EVIDENCE.md), repetir A e C pelo [runbook](RUNBOOK.md) e comparar com [resultados e limites da POC](POC.md). B e V podem ser repetidos como ensaios adicionais de detecção e de fonte de correção, sem tratá-los como dependências de C.
2. Registrar o que bateu, o que diferiu e o que não pode ser refeito nesta cópia, seguindo o [checklist](EXECUCAO.md). Essa aceitação é do **material reproduzido**, não da imagem ou ferramenta para produção.
3. Só então reler [o processo informado e o encaixe proposto](ARCHITECTURE.md) para identificar aproveitamento no AS-IS. O [plano posterior](NEXT-STEPS.md) separa integração e produto dessa tarefa imediata.

**Para reproduzir agora:** comece pelas provas separadas A e C no [runbook](RUNBOOK.md); B e V estão disponíveis como ensaios adicionais de detecção e de fonte de correção. **Para apenas auditar registros anteriores:** leia a matriz de 44 casos, o recibo integrado histórico e o resumo BMAD, sabendo que suas capturas ou executores completos não foram publicados. O leitor não deve somar essas duas classes como se formassem uma única execução portátil.

## Decisões que **não** foram tomadas

Não foi aprovada ferramenta nova, arquitetura de implantação, certificação de imagem nem adoção geral do BMad Loop. Menos requisições numa amostra local não escolhem A em vez de B. O valor de Diun/Vunnel deve ser avaliado **contra a matriz diária já existente**, quando o encaixe for discutido. Os resultados sintéticos do Loop não autorizam chamá-lo de workflow de domínio pronto.
