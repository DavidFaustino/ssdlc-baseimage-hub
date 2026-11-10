# Base Image Hub — POC e arquitetura

Este repositório reúne a documentação e um pacote reproduzível da POC que relaciona **mudança de imagem**, **pacote instalado** e **correção de segurança**. Também contém um protótipo visual independente.

**Objetivo imediato:** baixar esta cópia no computador de trabalho, entender o que cada experimento publicado faz, reproduzir os cenários que o pacote permite e conferir os resultados. **Depois dessa conferência**, identificar que partes são úteis no processo de imagens base AS-IS já documentado. A integração com CI, registries e a evolução operacional da interface são etapas posteriores. O [checklist de revisão](docs/EXECUCAO.md) acompanha essa ordem; os comandos existentes estão no [runbook](docs/RUNBOOK.md).

**Estado:** pesquisa e provas locais. Nenhuma imagem, ferramenta ou arquitetura foi aprovada para produção. Os scripts publicados permitem repetir testes específicos; eles ainda não formam uma execução operacional única de A/B/Vunnel até a decisão C.

## Por onde começar

| Se você precisa... | Leia |
|---|---|
| Entender o que pode ser repetido nesta cópia | [Marco atual](docs/STATUS.md) e [inventário de evidências](poc/EVIDENCE.md) |
| Reproduzir os experimentos publicados | [Runbook técnico](docs/RUNBOOK.md) e [checklist de conferência](docs/EXECUCAO.md) |
| Comparar sua execução com as conclusões registradas | [Resultados da POC](docs/POC.md) |
| Só depois avaliar encaixe no processo existente | [Arquitetura AS-IS e proposta](docs/ARCHITECTURE.md) e [próximas etapas](docs/NEXT-STEPS.md) |
| Consultar o trabalho paralelo com BMAD | [Workflows](docs/WORKFLOWS.md) |

O [índice de documentação](docs/README.md) explica a ordem de leitura e os termos principais. A [lista de fontes](docs/SOURCES.md) distingue arquivos publicados de material que permanece no acervo local.

## O que o pacote executável cobre

Na pasta [`poc/`](poc/README.md) estão os scripts, fixtures selecionadas, testes e recibos para: **A**, observar uma troca de digest por consulta OCI direta; **B**, observar a mesma troca com Diun como alternativa de detecção; **V**, consultar um feed Debian atual com Vunnel; e **C**, repetir uma decisão de correlação sobre entradas históricas arquivadas. **C não é alternativa a A ou B** e sua execução publicada não recebe automaticamente as saídas recém-geradas por A, B e V. Os **55 arquivos de evidência incluídos** têm hashes conferíveis. A suíte pública tem **18 testes**.

A comparação original de **44 casos** está resumida em linhas e recibos selecionados. Suas capturas completas e os 34 blobs da inspeção pública não foram incluídos; portanto, ela **não pode ser integralmente recalculada** a partir deste repositório. O [runbook](docs/RUNBOOK.md) explicita essa fronteira antes dos comandos.

As provas sintéticas de BMAD/Loop também estão **relatadas, não empacotadas para reexecução** neste PR. O [status](docs/STATUS.md) separa essas provas históricas dos quatro cenários A/B/V/C que você consegue executar a partir desta cópia.

## Protótipo visual

[`index.html`](index.html) é uma interface demonstrativa do **Hub operacional**, com dados fictícios e sem backend. A Visão geral apresenta três runs de exemplo (concluído, bloqueado e desconhecido). Eles usam a mesma identidade em Imagens, Automações e Adoção e cobertura, para mostrar o percurso run → digest → gate → publicação → consumo. Pedidos de avaliação, atualização e reexecução geram somente recibos DEMO no navegador; não chamam o CI. O Roadmap organiza pesquisa, validação e evolução proposta, sem alimentar o estado operacional. Abra o Hub no navegador ou sirva a pasta localmente:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

O protótipo não executa os scripts da POC e não consulta GitHub Actions, registry, JFrog, ECR, EKS ou scanners. Digests e artefatos exibidos são sintéticos e não correspondem a bytes publicados. [Prévia](preview.png).
