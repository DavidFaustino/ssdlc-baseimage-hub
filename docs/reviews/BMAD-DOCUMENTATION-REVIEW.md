# Revisão BMAD da documentação e das provas

**Escopo.** Revisão de `README.md`, todos os Markdown em `docs/` e `poc/`, scripts Python publicados, fixtures e recibos selecionados desta branch. A leitura considera o Base Image Hub como produto ligado ao processo de imagens base existente. Não houve alteração dos documentos revisados nem do protótipo visual.

**Método.** Skill instalada `bmad-review`, configuração resolvida para as lentes `adversarial`, `edge-case-hunter`, `verification-gap`, `structure` e `prose`. O conteúdo é documentação de arquitetura, especificação de comportamento, runbook e código de POC. Leitor: engenheiro humano que precisa entender, auditar e repetir a prova. A estrutura foi avaliada como **explicação conceitual** (`ARCHITECTURE.md` e `WORKFLOWS.md`), **relatório de contexto** (`STATUS.md`, `POC.md`, `SOURCES.md`) e **guia linear** (`RUNBOOK.md`).

## Conclusão factual

O pacote **explica corretamente que as provas A, B, Vunnel e C publicadas são separadas** e que o ensaio integrado antigo não pode ser regenerado integralmente daqui. A detecção controlada, a correlação sobre fixture e os limites de evidência têm referências localizáveis. Isso sustenta uma revisão da POC. Ainda não sustenta dizer que existe um Base Image Hub funcional, um encaixe aprovado no CI existente, nem um workflow BMAD reproduzível neste repositório. Essas fronteiras já aparecem em vários textos; os achados abaixo indicam o que falta especificar ou demonstrar para a próxima afirmação.

## Lente adversarial — achados

Os itens marcados **condição para alegação** impedem uma afirmação específica de completude ou reprodução. Os marcados **melhoria** tornam o material mais útil sem invalidar o resultado local descrito.

### A1 — Ligação operacional entre as peças

- **Localização:** [runbook, escopo e mapa](../RUNBOOK.md#escopo-e-estado-das-provas), [resultados, limites](../POC.md#limites-de-reprodução-e-procedência), [script C](../../poc/experiments/integrated-update-poc-20261108/run_local.py).
- **Condição:** A e B produzem sinais novos, Vunnel coleta feed novo, mas C carrega quatro fontes arquivadas por `load_archived_case()`.
- **Correção:** definir contrato e adaptador que transformem saídas novas em entradas de C, com identidade, hashes, erro seguro e teste de replay; manter o recibo antigo como histórico.
- **Consequência:** **condição para alegação** de fluxo de observação até decisão. Repetir os comandos atuais não reproduz uma decisão a partir dos sinais recém-coletados.

### A2 — Destino da decisão no processo atual

- **Localização:** [arquitetura, TO-BE](../ARCHITECTURE.md#3-to-be-encaixe-proposto-sem-integração-implantada), [próxima etapa](../NEXT-STEPS.md).
- **Condição:** `validate_candidate` chega a “revisão e entrada no CI existente”, mas não há contrato de job, payload, aprovador, retorno do gate ou vínculo ao digest certificado.
- **Correção:** especificar um handoff de candidata para o CI já existente: produtor, consumidor, artefato, identidade de execução, decisão humana, resposta, falha e rastreio até publicação.
- **Consequência:** **condição para alegação** de encaixe funcional. Um recibo da POC ainda não pode acionar nem provar o gate real.

### A3 — Segunda camada desenhada com promoção antes da aprovação equivalente

- **Localização:** [arquitetura, diagrama AS-IS](../ARCHITECTURE.md#1-as-is-da-imagem-upstream-à-aplicação).
- **Condição:** o diagrama traça `Scans e controles da segunda camada → ECR` diretamente, enquanto liga a aprovação equivalente a um nó lateral “pendente”. O texto afirma a pendência, mas a seta principal permite ler promoção como fluxo normal.
- **Correção:** representar a saída para ECR como estado **atual informado e ainda sem gate equivalente**, e separar explicitamente o gate proposto; não desenhar a aprovação pendente como se condicionasse a seta atual.
- **Consequência:** **melhoria** de precisão arquitetural. Um leitor pode assumir que os dois gates já têm a mesma autoridade.

### A4 — Identidade ao atravessar o proxy

- **Localização:** [arquitetura, fronteira JFrog](../ARCHITECTURE.md#3-to-be-encaixe-proposto-sem-integração-implantada), [decisões abertas](../ARCHITECTURE.md#5-decisões-para-uma-integração-real).
- **Condição:** o texto propõe consultar a origem e adquirir por digest no proxy, mas ainda não define a prova de equivalência `digest de origem → bytes recebidos → digest certificado` nem o tratamento de tag em cache.
- **Correção:** registrar o protocolo de aquisição e verificação por digest, incluindo índice, filho da plataforma, falha de cache, autenticação e recibo do build.
- **Consequência:** **condição para alegação** de correspondência da candidata upstream com o artefato certificado.

### A5 — Resultado `wait` e reavaliação por advisory sem rota de produto

- **Localização:** [arquitetura, TO-BE](../ARCHITECTURE.md#3-to-be-encaixe-proposto-sem-integração-implantada), [workflow, estados](../WORKFLOWS.md#estado-e-retomada).
- **Condição:** o texto menciona `wait`, duplicata e advisory novo, mas o diagrama e o contrato de handoff só desenham “evidência suficiente” ou `unknown`; não mostram quem reabre `wait`, com qual nova revisão de advisory, nem o que aparece para o operador.
- **Correção:** acrescentar transições distintas para `wait`, duplicata e reavaliação do mesmo digest, com gatilho, estado persistido, ação humana e condição de encerramento.
- **Consequência:** **condição para alegação** de controle contínuo de candidatas; o estado pode ficar sem próximo passo operacional definido.

### A6 — Repetição de C2 não demonstra a falha anunciada

- **Localização:** [runbook, cenário C2](../RUNBOOK.md#cenário-c2--recuperação-após-commit), [teste de recuperação](../../poc/experiments/integrated-update-poc-20261108/tests/test_recovery.py).
- **Condição:** o runbook chama `--recover` logo após C1, com os JSON já íntegros; o código os compara e preserva. O teste automatizado simula JSON ausente/parcial, mas o roteiro manual não.
- **Correção:** em cópia descartável do diretório C1, registrar hash e contagem do SQLite, remover ou truncar um recibo, executar `--recover` e comparar recibo reexportado, arquivo `.corrupt` e contagem inalterada.
- **Consequência:** **condição para alegação** de recuperação reproduzida pelo leitor; a sequência atual só prova reexecução idempotente sobre recibos existentes.

### A7 — Pré-requisito Python impreciso

- **Localização:** [runbook, preparação](../RUNBOOK.md#preparação-e-cadeia-de-custódia), [estado Python](../../poc/experiments/integrated-update-poc-20261108/src/state.py).
- **Condição:** o runbook pede “Python 3”, mas o código usa `dict | None` e `dict[str, dict]`, sintaxe que requer Python 3.10 ou posterior.
- **Correção:** declarar e conferir `python3 --version` com mínimo 3.10; manter Python 3.13 como requisito adicional do cenário V.
- **Consequência:** **melhoria** de portabilidade. Um executor com Python 3.9 falha antes dos testes.

### A8 — Verificação do Diun não confronta o manifesto baixado

- **Localização:** [runbook, cenário B](../RUNBOOK.md#cenário-b--observar-a-tag-com-diun).
- **Condição:** o roteiro baixa `checksums.txt` e apenas o exibe com `grep`; a verificação executada compara o arquivo a um hash literal no próprio documento, sem afirmar que a linha baixada coincide com esse valor.
- **Correção:** validar programaticamente a linha exata do artefato no `checksums.txt` baixado e só então extrair/executar; manter a versão e o hash literal como referência auditável.
- **Consequência:** **melhoria** de cadeia de custódia. O leitor pode acreditar que comparou binário e manifesto oficial quando só executou a comparação com o valor impresso no runbook.

### A9 — Resultados BMAD/Loop sem prova portátil

- **Localização:** [workflow, resultados](../WORKFLOWS.md#o-que-foi-realmente-testado), [status](../STATUS.md#em-uma-leitura), [fontes](../SOURCES.md).
- **Condição:** são citados 13 testes, história sintética `done`, Trial12 e compactação, mas o repositório não inclui os comandos, fixtures, testes, logs ou recibos correspondentes; `SOURCES.md` aponta apenas para material local ausente.
- **Correção:** anexar um pacote mínimo saneado de prova e runbook específico ou classificar essas afirmações como registro histórico não reexecutável aqui, com versão, hash, comando e limite por item.
- **Consequência:** **condição para alegação** de replicabilidade do workflow; o leitor só consegue auditar o relato, não repetir esses resultados.

### A10 — Contrato de produto ainda não liga dados a ações da interface

- **Localização:** [arquitetura, contratos](../ARCHITECTURE.md#contratos-entre-etapas), [status, protótipo](../STATUS.md#em-uma-leitura), [README](../../README.md#protótipo-visual).
- **Condição:** os documentos definem observação, inspeção e decisão da POC; não definem quais entidades, estados, evidências, permissões e ações o Hub deve mostrar para cada papel. O HTML é assumidamente demonstrativo e separado da POC.
- **Correção:** criar matriz curta `necessidade do processo → dado/estado → ação/autoridade → tela → origem da evidência → lacuna`, validada contra o AS-IS. A auditoria própria da interface pode preencher os detalhes das telas.
- **Consequência:** **condição para alegação** de alinhamento do produto. O protótipo pode parecer completo sem sustentar o controle operacional esperado.

### A11 — A comparação de ferramentas carece de critério de valor no AS-IS

- **Localização:** [POC, comparação A/B](../POC.md#comparação-ab-resultado-e-alcance), [arquitetura, alternativas](../ARCHITECTURE.md#4-alternativas-de-entrada-ainda-abertas).
- **Condição:** a medição de requisições é relatada corretamente como local, mas os documentos não enumeram quais capacidades do CI atual já cobrem agenda, inventário, estado e aviso. Sem essa linha de base, não se pode concluir que Diun/Vunnel acrescentem operação útil.
- **Correção:** no inventário AS-IS, confrontar necessidade por necessidade com o que já existe e apontar apenas a lacuna a preencher; usar a POC como prova de viabilidade de componentes.
- **Consequência:** **condição para alegação** de escolha arquitetural. Adotar ou descartar ferramenta com base apenas nas métricas locais repetiria uma decisão sem relação com o processo real.

### A12 — O runbook do feed atual não define qual mudança seria aceitável

- **Localização:** [runbook, cenário V](../RUNBOOK.md#cenário-v--consultar-a-fonte-de-correção-atual), [script Vunnel](../../poc/experiments/operational-abc-comparison-20261108/scripts/B/measure_vunnel.py).
- **Condição:** o roteiro imprime três versões de fix do feed vivo e valida apenas que há três hashes; não define como interpretar advisory ausente, fix alterado ou DSA mais recente. O script tem `timeout=180` segundos e não recebe uma revisão congelada como entrada.
- **Correção:** explicitar que o critério desse cenário é **coleta e identidade da linha atual**, não equivalência ao snapshot; registrar data/revisão, versão e resultado `unknown` quando a linha não existir, com diagnóstico do timeout.
- **Consequência:** **melhoria** de interpretação. Um feed que mudou pode parecer reprovação do caso histórico ou prova de fix atual sem vínculo suficiente.

## Lente de casos de borda — caminhos sem tratamento especificado

| Localização | Condição que expõe o caminho | Guarda necessária | Consequência |
|---|---|---|---|
| [Arquitetura, TO-BE](../ARCHITECTURE.md#3-to-be-encaixe-proposto-sem-integração-implantada) | `wait` persiste após fix sem digest novo. | Definir reobservação/reavaliação, dono, prazo e estado terminal. | Candidata permanece sem transição operacional. |
| [Arquitetura, handoff](../ARCHITECTURE.md#contratos-entre-etapas) | Digest visto na origem não é servido pelo proxy. | Impedir handoff e registrar divergência com ambos os digests. | CI pode avaliar conteúdo diferente do observado. |
| [Workflow, bloqueio](../WORKFLOWS.md#estado-e-retomada) | Uma história bloqueada coexiste com outra independente. | Identificar dependências e estado por história, preservando decisão G0. | Retomada pode repetir ou avançar trabalho dependente. |
| [Runbook, cenário C2](../RUNBOOK.md#cenário-c2--recuperação-após-commit) | Recibo ausente após commit do SQLite. | Simular ausência em cópia e exigir contagem igual após recuperação. | Leitor não observa a garantia de recuperação anunciada. |

## Lente de verificação — código adicionado

| Localização | Forma da lacuna | Consumidor, evidência lida e verificação que falta | Consequência |
|---|---|---|---|
| [carregador da captura pública](../../poc/experiments/integrated-update-poc-20261108/src/public_inputs.py) e [pipeline público](../../poc/experiments/integrated-update-poc-20261108/src/pipeline.py) | `regression-gap` | `Pipeline._verified_public()` chama `load_public_case()`. Busquei `load_public_case`, `process_public_stable` e `reassess_public_stable` em todos os testes publicados em `poc/experiments/integrated-update-poc-20261108/tests/`: nenhum os chama ou verifica a cadeia de bytes pública. O recibo arquivado em `poc/experiments/operational-abc-comparison-20261108/evidence/C/public-pipeline-20261108-verified/receipt.json` não é teste executável nesta suíte. Acrescentar fixture pública mínima e asserção de rejeição quando manifesto, camada, pacote ou feed divergir. | Uma regressão na validação da captura pública não falharia nos 18 testes de fixture histórica. |

## Lentes editoriais — organização e expressão

O conjunto existe para que um engenheiro **entenda o processo, separe proposta de prova e repita o que foi publicado**. A ordem de leitura atual é útil e deve ser preservada. `RUNBOOK.md` tem **2.231 palavras** pela ferramenta da skill; os demais documentos somam **6.376**, num total de **8.607 palavras** de Markdown. As recomendações abaixo acrescentam orientação curta em vez de cortar explicações necessárias.

| Pass | Original Text | Revised Text | Changes |
|---|---|---|---|
| structure | [Runbook, “Contratos nas fronteiras”](../RUNBOOK.md#contratos-nas-fronteiras), ~334 palavras, antes do setup e dos comandos | **PRESERVE** a tabela; acrescente uma frase de navegação no início: “Use a tabela para interpretar os recibos; para executar, comece em Preparação.” | O contrato serve à auditoria, mas o leitor do guia linear precisa de rota imediata. Impacto: ~15 palavras adicionais; sem corte. |
| structure | [Status](../STATUS.md) e [POC](../POC.md) repetem os limites A/B/C e BMAD em formatos diferentes | **PRESERVE** o resumo no Status e a prova detalhada na POC; mantenha uma única lista canônica de lacunas executáveis em [Próxima etapa](../NEXT-STEPS.md). | A repetição serve a públicos diferentes; o risco é atualizar só uma página. Impacto estimado: 0 palavras cortadas; menor deriva editorial. |
| prose | “Fonte de correção: `unknown` ou espera explícita” em [Arquitetura](../ARCHITECTURE.md#contratos-entre-etapas) | “Sem versão corrigida confiável, registrar `unknown`; quando a fonte declarar ausência de fix, registrar `wait` com condição de reavaliação.” | Distingue indisponibilidade da fonte de ausência de correção sem alterar o contrato pretendido; requer confirmar a regra com o dono. |
| prose | “B emite um aviso na troca e nenhum na repetição” em [Resultados](../POC.md#afirmações-e-cadeia-de-evidências) | “No registry local controlado, B emite um aviso na troca e nenhum na repetição.” | Aproxima o limite do enunciado e evita leitura como observação de registry público. |

**Resumo editorial:** quatro recomendações; nenhuma redução estimada, pois as duas passagens duplicadas são reforço funcional para leitores diferentes. A única adição estimada é de cerca de 15 palavras. A clareza melhora sem remover o mapa, a tabela de contratos ou as ressalvas de procedência.

## Verificações desta revisão

- A resolução de configuração da skill foi executada com cache `uv` isolado; as cinco lentes acima são as lentes habilitadas aplicáveis ao conjunto.
- Foram encontrados **143 links locais** nos 12 Markdown existentes e **nenhum caminho local quebrado** na checagem de existência. Os links deste relatório também foram checados abaixo. Existência do alvo não prova a renderização de âncoras em todos os renderizadores.
- Uma busca textual em Markdown, JSON, scripts e arquivos não binários por identificadores pessoais/organizacionais, endereços locais e padrões óbvios de segredo não mostrou nome de organização privada nem token real. O `Basic` encontrado em `probe.py` é credencial fictícia do registry local. Isso não substitui inspeção binária antes de publicar novas evidências.
- Tentei executar a suíte com o Python disponível **sem** preparar a venv do runbook; ela parou na importação de `jsonschema`. Isso confirma o pré-requisito, não é falha dos testes. Não reivindico nova execução verde da suíte nesta revisão.
