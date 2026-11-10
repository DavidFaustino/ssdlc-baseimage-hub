# Guia de leitura

Este repositório reúne um **protótipo visual** e um **registro de pesquisa e POC**. A página `index.html` usa dados demonstrativos; ela não consulta registries nem executa decisões.

Leia nesta ordem:

1. [Marco atual](STATUS.md) — o que foi feito, o que falta e o que não deve ser inferido.
2. [Processo atual e encaixe da POC](ARCHITECTURE.md) — onde a capacidade nova entraria, sem substituir a cadeia existente.
3. [Resultados técnicos](POC.md) — provas reproduzidas e limites de cada uma.
4. [Workflows e BMAD](WORKFLOWS.md) — trabalho paralelo de orquestração e sua maturidade real.
5. [Runbook reproduzível](RUNBOOK.md) — ambiente, hashes, testes, decisão e recuperação com os scripts incluídos.
6. [Roteiro de conferência](EXECUCAO.md) — checagem humana da entrega e da comparação histórica.
7. [Próxima etapa](NEXT-STEPS.md) — ordem para encaixar a capacidade no processo atual.

**Limite prático:** a pasta `poc/` contém o núcleo executável, fixtures selecionadas e recibos. Ela permite repetir a decisão principal. A comparação completa de 44 casos e a inspeção integral dos blobs públicos ainda dependem de arquivos grandes do acervo local; [veja exatamente o que foi migrado](../poc/EVIDENCE.md).

## Como ler os estados

- **Observado no processo atual:** informação descrita no mapa existente; sua posição exata ainda pode exigir validação com os donos do processo.
- **Provado na POC local:** houve execução com entradas, saída e evidência preservadas. O alcance está descrito no próprio resultado.
- **Proposto:** desenho que ainda não foi executado como fluxo completo.
- **Aberto:** precisa de decisão ou de uma prova nova. Não é falha automática da ferramenta.

## Nomes que causaram confusão

Há duas comparações diferentes na documentação de origem. **Rota direta** significa consultar OCI e dados Debian sem Diun/Vunnel. **Rota com ferramentas** significa usar Diun e Vunnel como entradas. Já **imagem oficial versus composição interna** são as duas possíveis vias para produzir a imagem corrigida. Uma comparação não decide a outra.

## Glossário rápido

| Termo | Em linguagem simples |
|---|---|
| Tag | Nome mutável de uma versão de imagem, por exemplo `latest`. |
| Digest | Identificador do conteúdo recebido; muda quando aquele conteúdo muda. |
| OCI | Padrão de registro e distribuição de imagens usado para consultar tags, manifestos e camadas. |
| Manifesto filho | Lista de conteúdo da imagem para uma plataforma específica, como Linux em x86-64. |
| Advisory | Comunicado da distribuição sobre uma falha e, quando existir, sua correção. |
| Recibo | Registro da entrada, execução e saída que permite conferir uma conclusão. |
| Matriz diária | Conjunto de jobs do CI que reconstrói as variantes de imagem a cada dia. |

## Procedência

Esta síntese foi preparada a partir dos documentos e recibos locais do projeto Base Image Hub, sem copiar logs extensos, nomes de empresa, credenciais ou artefatos internos para o repositório público. [Fontes e status de migração](SOURCES.md) identifica os materiais de origem. A versão pública é um **rascunho para revisão**, não aprovação de arquitetura ou implantação.
