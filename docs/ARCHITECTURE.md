# Arquitetura: processo atual e encaixe da POC

**Estado em 10/11/2026.** O AS-IS abaixo vem da documentação do processo de imagens base e de esclarecimentos do responsável. Esta POC não inspecionou os jobs corporativos nem se conectou a JFrog, ECR ou EKS. O TO-BE é uma proposta de encaixe, sem ferramenta ou implantação aprovada.

## 1. AS-IS: da imagem upstream à aplicação

```mermaid
flowchart LR
  U[Imagem upstream] --> J[JFrog: proxy da imagem solicitada]
  J --> M1[Matriz diária: GitHub Actions]
  M1 --> C[Ingestão e imagem certificada]
  C --> G1[Gates e aprovação da primeira camada]
  G1 -->|aprovada| M2[Reconstrução diária]
  G1 -->|reprovada| X1[Não promover; registrar motivo]
  M2 --> A[Imagem de arquitetura]
  A --> V[Scans e controles da segunda camada]
  V --> E[ECR: versão, alias e digest]
  V -.-> GAP[Fluxo equivalente de aprovação: pendente]
  E --> P[CI da aplicação: Dockerfile FROM]
  P --> R[Imagem da aplicação: release, commit e digest]
  R --> D[Argo CD e implantação]
  D --> K[EKS]
```

A primeira camada aplica hardening e políticas; a segunda cria bases por plataforma. Ambas têm rebuild diário. A matriz da primeira já tem aprovação; a segunda ainda precisa receber o mesmo fluxo. Foram informados scans com Trivy, Wiz, Checkov e Hadolint. A modalidade exata da aprovação, os thresholds e a implementação dos jobs **não foram verificados** nesta POC.

**Como ler a lacuna no desenho:** a seta da segunda camada para o ECR representa o percurso informado hoje, não uma aprovação automática. O ramo pontilhado indica que o fluxo equivalente de aprovação ainda não está definido. O Hub não pode preencher essa lacuna por conta própria.

`latest-stable` é um ponteiro para uma versão aprovada; digest é a identidade para evidência e rollback. Uma aplicação já construída não incorpora mudança posterior da base: seu CI precisa reconstruí-la e implantar novo digest.

| Ponto | Responsável informado | Limite de autoridade da POC |
|---|---|---|
| Ingestão e imagem certificada | Segurança/engenharia da base: hardening, política, build e evidência. | Não aprova certificação nem move alias. |
| Imagem de arquitetura | Plataforma: composição e compatibilidade da stack. | Não aprova a segunda camada. |
| Gates e workflows | Mantenedores do CI e das políticas existentes. | Não altera gate ou exceção. |
| Aplicação | Time consumidor: rebuild, testes e implantação. | Não autoriza deploy nem aceita risco. |

Esses donos são funções descritas pela fonte. RACI, jobs e modo de aprovação devem ser confirmados com os responsáveis antes de integrar a POC.

## 2. Informação que falta à cadeia atual

O rebuild diário não liga, por si só, **correção aplicável → digest upstream → plataforma → pacote instalado → versão corrigida** com evidência verificável. Recompilar uma Distroless antiga também não instala automaticamente um pacote Debian atualizado. A POC investigou essa ligação para justificar uma *candidata* que ainda passaria pelos gates existentes.

O caso histórico usa Distroless Java 21/Debian 13 e `libexpat1` antes e depois de uma correção. Uma imagem pública estável foi inspecionada para um advisory específico. Isso não certifica a imagem inteira nem define regra para outras distribuições. Veja [resultados e limites](POC.md) e [evidências](../poc/EVIDENCE.md).

## 3. TO-BE: encaixe proposto, sem integração implantada

```mermaid
flowchart LR
  R[Registry de origem] --> O[Observar tag; resolver digest e plataforma]
  F[Advisory e versão corrigida] --> C[Correlação verificável]
  O --> I[Inspecionar conteúdo por digest]
  I --> C
  C --> S[Estado e recibo da candidata]
  S -->|evidência suficiente| H[Revisão e entrada no CI existente]
  S -->|unknown ou divergência| B[Investigar; sem promoção]
  H --> J[JFrog: proxy da imagem escolhida]
  J --> Q[Conferir digest e bytes recebidos]
  Q -->|equivalente| G[Build, scans e gates existentes]
  Q -->|divergente| B
  G -->|aprovada pelo processo atual| E[ECR e consumidores]
```

O registro da POC pode indicar `validate_candidate`, `wait`, duplicata ou `unknown`. **Nenhum desses estados aprova uma imagem.** O gate de certificação continua no CI atual. O ponto exato de handoff e seu aprovador ainda precisam ser definidos com os donos dos workflows.

| Resultado da correlação | Leitura operacional proposta | O que fica proibido |
|---|---|---|
| `validate_candidate` | Há evidência suficiente para pedir avaliação de uma candidata identificada por digest e plataforma. | Certificar, publicar ou mover alias sem os gates existentes. |
| `wait` | Ainda não há correção aplicável confirmada, ou a imagem oficial necessária ainda não chegou; conservar o baseline e reavaliar quando a fonte mudar. | Declarar a imagem corrigida ou encerrar o acompanhamento sem motivo. |
| `unknown` | Uma entrada obrigatória é ausente, ambígua, divergente ou velha; abrir bloqueio com a fonte e a última evidência válida. | Inferir resultado favorável, aprovar ou promover. |
| Duplicata | Evento já processado para a mesma identidade e revisão; apontar ao recibo existente. | Criar segunda decisão ou repetir efeito externo. |

Um advisory novo exige reavaliação mesmo com **digest estável**. Uma tag que aponta a outro digest exige nova inspeção de conteúdo. São gatilhos independentes e não devem ser contados como duas imagens candidatas quando se referem ao mesmo conteúdo.

**Fronteira JFrog.** O proxy fornece a imagem solicitada e pode servir manifesto em cache. Agendar um script ou Diun não força atualização desse cache. Para descobrir uma mudança upstream sem depender do cache, o desenho propõe consultar o registry de origem; depois obter a candidata pelo proxy **por digest** e conferir o conteúdo recebido. Conectividade, autenticação, política de cache e equivalência dos digests precisam de validação no ambiente real. A POC não testou esse percurso via JFrog.

### Contratos entre etapas

| Etapa | Entrada | Saída verificável | Falha segura |
|---|---|---|---|
| Observação | Registry, imagem, tag, plataforma e horário. | Digest do índice e do manifesto filho, tipo, bytes/hash e evento com identidade estável. | Fonte inacessível ou plataforma ausente/ambígua: `unknown`. |
| Inspeção | Digest filho e conteúdo verificável. | Distribuição/suite, arquitetura, pacote fonte e binário, versão instalada e prova ligada ao digest. | Conteúdo ou vínculo ausente: não inferir patch. |
| Fonte de correção | CVE/advisory, pacote, suite e revisão da fonte. | Versão corrigida, base de comparação e hash da revisão. | Fix ausente, dado velho ou divergente: `unknown` ou espera explícita. |
| Correlação | Entradas verificadas e baseline persistido. | Decisão, razão, evidências e recibo idempotente com `image_approved=false`. | Entrada incoerente: nenhuma promoção; registrar motivo. |
| Handoff ao CI **proposto** | Digest candidato e recibo verificável. | Pedido de avaliação e, se aprovado nos gates, vínculo ao digest corporativo. | Falha de gate/autorização: não mover alias estável. |

Digest novo e advisory novo são gatilhos diferentes: o mesmo digest pode precisar de reavaliação quando surge um fix. O protótipo local persiste estado e recibos em SQLite e retorna `unknown` em falhas relevantes; não implementa o handoff corporativo. Veja [correlação](../poc/experiments/integrated-update-poc-20261108/src/pipeline.py) e [adaptadores de replay](../poc/experiments/integrated-update-poc-20261108/src/adapters.py).

### Handoff e autoridade — contrato proposto, ainda não implantado

1. **Descoberta e inspeção upstream** registram origem, tag, horário, digest do índice, manifesto filho, plataforma e pacote observado; consulta ao proxy não substitui a prova do estado atual da origem.
2. **Correlação provisória** junta conteúdo inspecionado, distribuição/suite, advisory e revisão da fonte; produz razão e recibo idempotente para uma candidata. O componente da POC não possui autoridade para certificar.
3. **Revisão do pedido** decide se a candidata deve entrar no CI existente. Responsável e forma de autorização ainda precisam ser definidos; `validate_candidate` por si só não libera a imagem.
4. **Aquisição pelo JFrog** solicita o digest escolhido e confere bytes, tipo de manifesto, plataforma e digest recebido contra a origem. Sem equivalência demonstrada, o handoff é bloqueado e o resultado fica `unknown`.
5. **CI existente** recebe digest e recibo verificados. Os gates de build, scan, política e aprovação da primeira camada continuam no processo atual. A aprovação equivalente da segunda camada precisa ser desenhada e validada separadamente.
6. **Publicação e consumo** só registram digest certificado, alias aprovado e, depois, digest efetivamente usado pela aplicação e ambiente. Publicação no ECR não prova adoção; o build da aplicação deve ser refeito para incorporar a nova base.

Antes da integração, devem ser nomeados **job receptor, aprovador, política de exceção, limite de acesso, contrato de recibo e regra de rollback**. Não há esses detalhes corporativos confirmados na POC; a sequência acima é uma proposta para revisão com os donos do processo.

### Capacidades do Hub e sua situação

| Controle que o operador precisa | Situação conhecida | Papel proposto do Hub |
|---|---|---|
| Rebuild, scans e aprovação da base certificada | Existem no processo informado; jobs e regras não foram inspecionados. | Mostrar estado e prova do gate; não substituí-lo. |
| Aprovação da imagem de arquitetura | Fluxo equivalente é lacuna informada. | Exibir pendência e bloqueio; não marcar como aprovada. |
| Mudança upstream e correção aplicável | POC local provou partes com OCI, pacote e advisory Debian. | Exibir candidata, identidade, fonte, razão e ação segura. |
| Frescor do proxy e digest efetivamente certificado | Fronteira JFrog não testada. | Tornar visível origem → proxy → certificado, com equivalência verificável. |
| Estado, retomada e duplicação | Protótipo local de correlação testado; integração operacional ausente. | Exibir último estado válido, recibo, bloqueio e reavaliação. |
| Publicação e consumo por ambiente | Cadeia descrita, sem conexão da POC com ECR/EKS. | Separar “certificado”, “publicado” e “consumido” por digest e evidência. |

O [protótipo navegável](../index.html) hoje usa dados fixos e não implementa essas capacidades. Seus painéis de catálogo, jornada e automações são vistas demonstrativas; a próxima versão precisa ligar cada estado a uma identidade e evidência, sem apresentar decisão da POC como aprovação.

## 4. Alternativas de entrada ainda abertas

| Capacidade | Consulta direta | Ferramenta avaliada | Exigência comum |
|---|---|---|---|
| Mudança da imagem | OCI consultado por código, agendado no CI existente. | Diun emite aviso da referência cadastrada. | Resolver manifesto filho, validar bytes e plataforma; tratar cache, erros e reconciliação. |
| Dados de correção | Fonte de segurança da distribuição lida diretamente. | Vunnel coleta e normaliza o feed. | Conferir pacote fonte, suite, versão, advisory e frescor contra o digest inspecionado. |

**Diun, Vunnel e o correlator não formam uma pipeline integrada única neste repositório.** Os scripts publicados são provas separadas ou replays com capturas fixadas. No caso histórico, as entradas alcançaram a mesma decisão; isso não demonstra benefício de acrescentar ferramentas à matriz diária. Veja o [runbook](RUNBOOK.md).

Outra decisão, independente da ferramenta de entrada, é **aguardar a imagem oficial ou avaliar uma composição interna já homologada** quando o fix existe antes da imagem do fornecedor. Esta POC não implementou nem homologou composição própria.

## 5. Decisões para uma integração real

1. Qual job recebe a observação e qual responsável revisa a candidata.
2. Se o upstream deve ser consultado além da matriz diária, com que frequência e como acessar a origem sem confundir cache do proxy.
3. Como provar a cadeia `upstream digest → conteúdo entregue pelo proxy → digest certificado`.
4. Como atender bases não Debian com fonte de segurança e comparação de versão específicas.
5. Como registrar baseline, advisory novo, falha de fonte, decisão e retomada sem duplicação.

O [status do marco](STATUS.md) separa as provas locais do que ainda falta integrar.
