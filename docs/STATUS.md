# Marco atual — Base Image Hub e workflows

**Revisão:** 10 de novembro de 2026. Este é um ponto de retomada: o que foi observado, o que pode ser reproduzido neste repositório e o que continua aberto.

## Em uma leitura

A POC local mostrou que é possível vincular **digest da plataforma → pacote instalado → correção Debian → decisão registrada** no caso testado. Isso ainda não está encaixado na cadeia de imagens base já existente. O protótipo visual deste repositório não executa a POC. O workflow completo com BMAD ainda é desenho; houve provas sintéticas de partes dele.

| Frente | Estado | Evidência e limite |
|---|---|---|
| Processo atual de imagens base | **Descrito, a validar no ambiente de destino.** | Há matriz diária de CI, ingestão/certificação, imagem de arquitetura, publicação e consumo. O ponto exato da nova informação e os gates reais precisam de validação com os responsáveis. [Arquitetura](ARCHITECTURE.md). |
| Caso histórico de pacote | **Comprovado localmente.** | Dois digests da mesma variante contêm `libexpat1` antes/depois da correção. Manifestos e arquivos selecionados estão em [`poc/`](../poc/EVIDENCE.md); isso não é uma troca observada hoje na tag pública. |
| Imagem pública | **Captura pontual.** | O laboratório vinculou digest estável, manifesto da plataforma, 34 camadas, pacote e advisory. Os 34 blobs completos não estão publicados aqui; não houve mudança pública de tag nem certificação. [Resultados](POC.md). |
| Entradas A/B e correlação C | **Provas locais, sem escolha de ferramenta.** | A e B detectaram a mesma troca histórica; C registrou decisão sem duplicação. Neste repositório, os scripts A/B e o núcleo C podem ser repetidos pelo [runbook](RUNBOOK.md). A matriz arquivada tem 44 casos (6 completos, 38 parciais), mas seus dados brutos integrais não estão aqui. |
| BMAD e Loop | **Instalação, desenho e provas sintéticas.** | A fixture de estado passou em 13 testes; uma história sintética chegou a `done` com recibo e retomada em duas invocações. O ciclo completo com história real de imagem base não foi executado. [Workflows](WORKFLOWS.md). |
| Protótipo visual | **Demonstrativo.** | `index.html` não tem backend nem integração com CI, registry, proxy, scanners ou ECR. |

## O que esta entrega permite fazer

- Entender [o processo informado e o encaixe proposto](ARCHITECTURE.md).
- Ler [resultados e limites da POC](POC.md), conferir [as evidências incluídas](../poc/EVIDENCE.md) e repetir as partes executáveis pelo [runbook](RUNBOOK.md).
- Revisar [o contrato dos workflows](WORKFLOWS.md) e seguir uma [próxima etapa ordenada](NEXT-STEPS.md).

## Decisões que **não** foram tomadas

Não foi aprovada ferramenta nova, arquitetura de implantação, certificação de imagem nem adoção geral do BMad Loop. Menos requisições numa amostra local não escolhem A em vez de B. O valor de Diun/Vunnel deve ser avaliado **contra a matriz diária já existente**, quando o encaixe for discutido. Os resultados sintéticos do Loop não autorizam chamá-lo de workflow de domínio pronto.
