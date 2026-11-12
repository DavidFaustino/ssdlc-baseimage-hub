# DE/PARA — Arquitetura da UI e processo de imagens base

> **Revisão da arquitetura do produto — propostas congeladas.** O de/para está preservado para avaliação depois da discussão do [piloto Distroless](../piloto-distroless/README.md). Não altera o ciclo mostrado na interface nem define o novo processo aprovado.

**Referência AS-IS:** a [arquitetura compartilhada](../processo/ARQUITETURA.md) é a única descrição de processo de referência no repositório. Este arquivo preserva o confronto com a UI e as correções propostas, sem estabelecer um processo paralelo.

**Estado: PROPOSTA PARA REVISÃO.** Análise documental de 12/11/2026. Nenhuma correção da UI, sincronização do acervo, integração ou mudança de processo foi executada nesta rodada.

## 1. Síntese para a revisão

A tela **Arquitetura** explica duas coisas diferentes: o ciclo das imagens e uma proposta de chegada dos dados ao Hub. Essa separação é útil. O primeiro desenho, porém, simplifica etapas que o operador precisa distinguir: seleção pela whitelist, comparação de digest, imagem raw relatada, publicação da base certificada e sua utilização pela plataforma. O último nó também concentra construção da aplicação e implantação em EKS como se fossem uma única etapa e todo o universo de consumo.

Há duas divergências que não podem ser corrigidas escolhendo uma fonte silenciosamente:

- **Aprovação da base derivada:** os registros canônicos e o texto consolidado dizem que o fluxo equivalente ainda precisa ser aplicado; o relato atual informa certificação/aprovação e catálogo nessa camada.
- **Assinatura e attestation:** o texto consolidado mantém mecanismo KMS e verificação por Kyverno no TO-BE; o responsável informa que já gera assinatura, SBOM e attestation SLSA. Existência de artefatos não resolve, sozinha, qual mecanismo está implantado em cada camada.

**Recomendação para o desenho, sujeita à revisão:** apresentar três categorias — **imagem base certificada**, **imagem base derivada pela plataforma** e **imagem de aplicação** — com publicações e digests próprios. Separar aquisição/transformação/aprovação/publicação de consumo/implantação. Manter os conflitos acima visíveis até sua reconciliação, sem chamar scan de aprovação formal.

## 2. Fontes e critério de autoridade

As siglas abaixo identificam fontes sanitizadas para esta análise. Os documentos externos ao repositório foram consultados apenas para leitura; os caminhos privados não são necessários para compreender o DE/PARA.

| Fonte | Conteúdo utilizado | Data e limite de procedência |
|---|---|---|
| **UI** | [`index.html`](../../index.html): `archNodes`, `architecture`, `archGroup` e `showArch`; cenário em `demoRuns`. | Código-base da revisão `a495b11`, consultado em 12/11/2026. Fonte do comportamento visual, não prova do ambiente corporativo. |
| **DOC1** | “Gerenciamento end-to-end de imagens-base”: cadeia conhecida, controles atuais, proposta de gestão, identidade e decisões necessárias. | Texto sem data de atualização por seção; consultado em 12/11/2026. O próprio documento separa cadeia conhecida de TO-BE. |
| **DOC2** | “Supply chain e imagens-base”: resumo dos controles e delimitação do caminho conteinerizado/Kubernetes. | Sem data explícita por seção; consultado em 12/11/2026. Remete a DOC1 e informa caminho separado Airflow/EMR. |
| **CAN** | Fatos `FACT-004`, `FACT-027`, `FACT-029`–`FACT-035`, `FACT-037`, `FACT-047`, `FACT-074`–`FACT-075`; decisões `DEC-003`, `DEC-011`, `DEC-034`; perguntas `QUE-020`, `QUE-043`, `QUE-050`; requisito `REQ-057`. | YAML canônico consultado em 12/11/2026; os registros citados não trazem data individual. Preservam-se status e IDs, sem atribuir-lhes data de implantação. |
| **CTX** | “Diagnóstico e hipóteses”, seções de fontes e AS-IS; “Visões de processo e decisão”, AS-IS e seus limites. | Discovery registra proposta recebida em 06/11/2026; data de cada relato não individualizada. Consulta em 12/11/2026. Descreve relatos de raw/hardened, proxy e digest, mas não inspeção dos workflows reais. |
| **REL** | Esclarecimento atual do responsável: whitelist YAML; aquisição/digest/raw; base certificada; derivada da plataforma a partir do ECR; aplicações e runtimes variados; aprovação e artefatos existentes relatados. | Conversa de 12/11/2026. Esclarecimento de domínio, sem execução ou inspeção de job nesta análise. Ainda não reconciliado nos YAML canônicos. |
| **REPO** | [Arquitetura atual do repositório](../processo/ARQUITETURA.md) e [especificação da UI](ESPECIFICACAO.md). | A referência compartilhada distingue processo informado, pendências e propostas; a especificação descreve a UI consultada em 12/11/2026. Nenhuma dessas leituras comprova execução corporativa. |

**Critério:** código comprova o que a UI representa; registro canônico comprova o estado documental registrado; relato comprova o que foi informado. Nenhum dos três, nesta rodada, comprova execução no ambiente de destino. Data mais recente não torna uma fonte automaticamente substituta das demais. As pendências de conciliação estão na seção 8.

## 3. O que a tela faz hoje

O primeiro painel, **“Ciclo operacional da imagem”**, exibe nove nós em dois grupos: origem/primeira camada e segunda camada/distribuição/consumo. Os detalhes de cada nó informam função, entrada, saída, responsável, evidência e situação. O segundo painel, **“Como os dados chegariam ao Hub”**, exibe cinco nós propostos de fontes até apresentação.

Sua função atual é **educativa e de referência do processo**, dentro de uma interface demonstrativa. Os nós não representam jobs acionáveis nem o estado observado de uma execução. As setas são conexões visuais entre cartões sequenciais, não eventos provenientes do CI. Clicar abre texto fixo em diálogo; não consulta registry, Actions, ECR ou runtime.

Não há cálculo de “último estado válido”, expiração ou `unknown` nessa tela. Ausência de fonte e plataforma desconhecida aparecem no cenário DEMO das telas operacionais, não como resultado dinâmico dos diagramas de Arquitetura. A divisão AS-IS/TO-BE está indicada no texto; os dados de execução DEMO são outra dimensão e não validam o AS-IS.

## 4. Processo de referência para discutir o PARA

Use a [arquitetura compartilhada](../processo/ARQUITETURA.md) para o percurso entre **imagem base certificada**, **imagem base derivada pela plataforma** e **imagem de aplicação**, suas publicações e responsabilidades. As matrizes abaixo analisam como a tela representa esse processo; não mantêm uma segunda definição AS-IS.

O ajuste visual deve preservar digests próprios por transformação, passagem pelo ECR antes do consumo da próxima camada e distinção entre construir, aprovar, publicar e implantar. Detalhes relatados ou conflitantes, como raw intermediário e aprovação da derivada, permanecem pendências na referência compartilhada. As mudanças de UI continuam congeladas.

## 5. Matriz DE/PARA dos nós

**C** = correspondência documental; **O** = omissão; **A** = ambiguidade; **D** = divergência. Toda coluna PARA abaixo é proposta, não alteração aplicada. As datas de procedência estão no catálogo de fontes da seção 2.

| Elemento atual / DE | Entrada → saída e responsabilidade exibidas | Fonte e correspondência | Lacuna e impacto | PARA proposto |
|---|---|---|---|---|
| `upstream` — Registro de origem | Imagem/tag → manifesto/digest; fornecedor. | UI; CAN `FACT-031`; DOC1; REL. **C/A** | Origem isolada não explica o conjunto autorizado de imagens nem a última identidade conhecida. | Mostrar whitelist como entrada de controle: registry/imagem/tag/último digest; origem fornece conteúdo, CI acompanha. Registrar como REL até conciliar. |
| `proxy` — JFrog | Referência → conteúdo ou erro; plataforma de artefatos. | UI; REL; CTX para proxy/digest. CAN `FACT-047` confirma também evidências no JFrog. **C/O** | Uma única caixa não distingue entrega de imagens de armazenamento de reports/SBOM. Cache pode ocultar mudança upstream. | Separar função proxy e função evidências; identificar conteúdo servido/digest/horário e erro sem pressupor consulta fresca à origem. |
| `matrix` — Matriz diária | Configuração/imagem → execuções/build; mantenedores CI. | CAN `FACT-004`, `FACT-075`, `DEC-034`, `REQ-057`; REL. **C/O** | Só há uma matriz antes da primeira camada; a rotina diária da plataforma desaparece. Também falta whitelist e comparação do digest. | Representar os dois ciclos diários e suas entradas/dependências. Explicar agendamento separado de aquisição e de aprovação. |
| `first` — Primeira camada | Imagem/política → base preparada/evidências; equipe da base. | DOC1; CAN `FACT-032`, `FACT-047`; REL. **C/O/A** | Agrupa ingestão, hardening, scan e artefatos; não mostra raw nem publicação da base. “Scans” não detalha cobertura. | Nomear imagem base certificada; mostrar transformação, scans e saída por digest. Raw intermediário e ordem exata ficam relatados. Listar controles conforme fonte, com Docker checks ainda `QUE-020`. |
| `gate1` — Aprovação existente | Base/evidências → aprovação/rejeição; aprovador atual. | CAN `FACT-075`, `QUE-050`; DOC1; REL. **C/A** | Existência registrada, mas modalidade humana/automática, política e autoridade exatas não foram conferidas. | Preservar aprovação da primeira camada e resultado/motivo; não nomear aprovador ou automatismo sem conciliação. Acrescentar saída aprovada para publicação da própria base. |
| `derived` — Segunda camada | Base aprovada/configuração → derivada; plataforma. | CAN `FACT-031`–`FACT-033`; DOC1; REL. **C/O** | Esconde FROM da base certificada já publicada no ECR, capacidades instaladas e digest pai/resultante. | Nomear base derivada pela plataforma; registrar entrada certificada do ECR, versão/digest pai, configuração e novo digest; mostrar seu rebuild diário. |
| `scans` — Scans e controles | Derivada → controles; donos da política/CI; gate pendente. | CAN `FACT-032`, `FACT-075`, `DEC-034`, `QUE-050`; REL. **C/D** | Scans nas duas camadas são confirmados documentalmente. Aprovação “pendente” na UI conflita com aprovação existente relatada hoje. | Distinguir scan, certificação e aprovação; mostrar conflito a reconciliar, sem retirar gate nem declará-lo implantado. |
| `registry` — ECR/distribuição | Imagem após controles → referência por digest; plataforma/registro. | CAN `FACT-029`–`FACT-034`; DOC1; REL. **C/O** | Um ECR final parece representar todas as publicações. Não separa raw, certificado, derivado e aplicação; alias pode ser confundido com identidade. | Publicações por categoria com digest próprio, versão/alias e prova correspondente. Raw relatado separado do catálogo aprovado. |
| `apps` — Aplicação e EKS | Digest/Dockerfile → imagem e deployment; consumidor. | DOC1; DOC2; CAN `FACT-027`, `FACT-030`, `FACT-034`–`FACT-035`; REL. **C/O/A** | Une build da aplicação, seus controles, publicação e runtime. EKS vira escopo universal; mapa de consumidores não é confiável. | Separar imagem de aplicação, publicação e implantação/runtime; suporte a vários repositórios; indicar escopo conteinerizado e outras cadeias sem inferir vínculos. |
| `systems` — Sistemas da cadeia | Eventos/manifests/execuções/deployment → dados brutos; donos das fontes. | UI; DOC1 identidade requerida; REPO. **C como proposta** | Fontes e fatos existentes não significam APIs ou contratos integrados. | Manter no segundo diagrama, com cada fonte de leitura e situação explícita; origem corporativa não é dataset DEMO. |
| `collectors` — Coleta por contratos | Dados/credenciais autorizadas → observações; integração. | UI; REPO. **C como proposta** | Pode parecer conector pronto se lido fora do aviso; sem frescor/erro medidos. | Preservar “proposto, sem conexão”; contrato de identidade, horário, erro e autoridade por fonte, sem escolher transporte agora. |
| `validation` — Validação e vínculo | Observações → válido/desconhecido; equipe Hub. | UI; DOC1 requisitos de identidade; REPO. **C como proposta** | UI não calcula validade/frescor; as provas locais da POC não integram esse nó. | Mostrar função futura; distinguir vínculo inválido, dado ausente e fonte vencida. Não representar validação da POC como certificação. |
| `evidence` — Estado e evidências | Registros/decisões → estado e recibos; Hub/donos dos gates. | UI; DOC1; CAN `FACT-047`. **C como proposta/O** | Persistência operacional não existe; recibos DEMO locais não são prova dos gates. Repositório de evidência real não é este estado visual. | Consumir referência ao registro do sistema competente; conservar origem, camada, digest e decisão. Diferenciar storage real e armazenamento DEMO do navegador. |
| `surface` — Base Image Hub | Estado/recibos → visão/bloqueios; produto. | UI; REPO. **C como protótipo** | Sem backend, o último nó apresenta somente exemplo. Clique em cartão não administra um job. | Manter explicação do produto e ações possíveis separadas de ações reais; rastrear cada estado integrado à fonte quando a integração for autorizada. |

## 6. Matriz das relações e dos caminhos ausentes

As relações “DE” abaixo são a leitura sequencial dos grupos do HTML; não são um grafo de dependências executável. Em particular, o fim do primeiro grupo e o início do segundo não possuem um vínculo visual dedicado que explique a publicação intermediária.

| Relação DE | Correspondência/procedência | Problema e impacto | Relação PARA proposta |
|---|---|---|---|
| Origem → proxy | REL/CTX; DOC1 confirma JFrog para evidências, não posiciona todas as chamadas. | Pedido do CI e fluxo do conteúdo se confundem. | Whitelist/rotina solicita; origem entrega via proxy; identificar cache, digest pedido e recebido. |
| Proxy → matriz | UI; CAN confirma matriz, REL confirma aquisição pelo fluxo. | Ordem visual sugere que proxy inicia o job, em vez de fornecer entrada à rotina. | Separar aresta de controle (agenda/whitelist → execução) da aresta de dados (proxy → conteúdo recebido). |
| Matriz → primeira camada | CAN `FACT-075`; REL. | Comparação do último digest e raw não aparecem; não se sabe o efeito de “sem mudança”. | Expor observação/comparação e decisão de continuar conforme regra a confirmar. Não presumir que digest igual cancela rebuild diário. Raw como intermediário relatado. |
| Primeira camada → gate | DOC1; CAN `FACT-032`, `FACT-075`; REL. | Sem ramo de rejeição/erro, todo caminho visual parece seguir. | Saídas aprovadas, reprovadas e prova insuficiente com motivo/responsável; não promover como aprovada quando falhar. |
| Gate1 → segunda camada | CAN `FACT-031`; REL detalha FROM do ECR. | Publicação da base certificada fica implícita; pode parecer que a derivada recebe o digest upstream. | Gate1 → publicação certificada ECR → consumo dessa base pela plataforma; relacionar pai e novo digest. |
| Segunda camada → scans | DOC1; CAN `FACT-032`; REL. | Scans genéricos escondem instalação/build e aprovação distinta. | Build/capacidades → controles da derivada → decisão da camada, com conflito do estado da aprovação marcado. |
| Scans → ECR | CAN `REQ-057` exige aprovação antes de promover alias; REL informa aprovação. | Seta direta pode comunicar “scan = aprovação” ou promoção sem gate definido. | Separar resultado de controles, autoridade/aprovação e publicação/movimento de alias. Reconciliar G2 antes de afirmar sequência implantada. |
| ECR → aplicação/EKS | CAN `FACT-030`, `FACT-033`–`FACT-035`; DOC1/DOC2; REL. | Publicação parece implicar rebuild/deploy; perde digest da aplicação e diversidade de consumo. | Base plataforma → build do consumidor → artefato aplicação → deployment observado por runtime; sem consumidor conhecido, estado não confirmado. |
| Sistemas → coleta → validação → estado → Hub | UI/REPO; requisitos de rastreabilidade DOC1. | Quatro ligações propostas podem ser lidas como integração existente. | Manter integralmente no TO-BE, com contratos pendentes e erros visíveis; não misturar com as nove etapas do ciclo informado. |
| Evidências/gates → catálogo aprovado | DOC1/CAN/REL. | JFrog como repositório de reports e catálogo relatado não têm caminho próprio. | Ligações por camada e digest; catálogo deve apontar ao artefato/gate competente, não certificar pelo simples cadastro. |
| Publicação → reauditoria → consumidores afetados | DOC1, CAN `DEC-003`, `FACT-035`. | Ciclo desenhado termina no consumo e não explica reavaliação; atualização da base pode parecer resolver aplicações antigas. | Explicitar como contexto de gestão: reauditoria e campanha são capacidades a integrar, não novas tarefas já executadas. Rebuild/redeploy do consumidor são independentes. |

### Digests e estados que o desenho deve preservar

- **Identidade:** upstream, pós-hardening/certificado, derivado e aplicação podem ter digests diferentes. O vínculo correto é parental/proveniência; não uma igualdade universal de SHA. Índice OCI e manifesto da plataforma também não são intercambiáveis.
- **Verificação:** “verificar SHA” no relato diz respeito à integridade/identidade informada; não comprova verificação de assinatura nem que o conteúdo visto no cache é o mais recente da origem.
- **Transformação:** raw, hardened, certificado e publicado precisam de critérios distintos. Raw não significa aprovado; scans existentes não provam que um gate formal aprovou.
- **Ausência:** sem digest, gate, evidência atual ou vínculo de consumidor, indicar o fato ausente e sua fonte. Não preencher com sucesso, zero consumidores ou “não aplicável” por conveniência.
- **Reavaliação:** uma CVE/política nova pode exigir revisão de um digest já publicado; um alias atualizado só será incorporado por uma aplicação quando ela construir novamente e implantar seu novo artefato.

## 7. Complexidade que não precisa virar produto ou infraestrutura nova

A análise de fidelidade não exige desenhar cada comando como uma tela nem instalar uma ferramenta por nó. A arquitetura deve permitir entender quem fornece a entrada, quem transforma/decide e onde fica a saída, mantendo o detalhe técnico acessível no contexto.

| Ponto | Complexidade evitável | Tratamento proposto e limite |
|---|---|---|
| Três categorias de imagem | Tratar nomes de repositório e cada subetapa como produtos independentes. | Organizar o ciclo nas três categorias aprovadas e abrir aquisição, build, scan e aprovação como detalhes. Não esconder decisões e publicações distintas. |
| ECR e JFrog | Desenhar raw/certificado/derivado/aplicação como quatro novos serviços ou separar “proxy” e “evidências” como duas instalações JFrog. | Mostrar funções e artefatos diferentes do mesmo sistema quando aplicável. Quantidade/configuração de repositórios não é decidida por esta análise. |
| Matriz, comparação e observação | Introduzir outro agendador/monitor apenas para reproduzir a rotina diária já existente. | Primeiro representar a rotina e sua whitelist. Eventual detecção adicional só se justifica por necessidade demonstrada, não porque houve POC de ferramenta. |
| Scans e gates | Duplicar scanners ou tratar o Hub como segundo aprovador porque precisa exibir resultados. | Reutilizar controles e decisões das fontes responsáveis; o Hub apresenta vínculo/razão e encaminha pedido autorizado. A conciliação da aprovação da derivada continua necessária. |
| Coleta, validação e persistência | Os cinco nós TO-BE parecerem exigir cinco serviços/microserviços novos. | São capacidades lógicas propostas; podem ser implementadas pelo menor conjunto compatível com o ambiente, ainda não escolhido. Não inferir topologia de implantação das caixas. |
| Raw e evidências | Eliminar intermediário ou duplicar todos os arquivos para “simplificar”. | Antes, confirmar finalidade, retenção e autoridade. O Hub pode referenciar evidências existentes; simplificação visual não autoriza remover prova ou controle. |
| POC e produto | Acrescentar o fluxo OCI/Diun/Vunnel/correlator como uma etapa obrigatória do AS-IS. | Manter POC como estudo e código reaproveitável. Nenhuma dessas ferramentas é requisito para explicar as três categorias ou conservar o CI atual. |

**Critério de corte proposto:** cada elemento do desenho deve explicar uma identidade, transformação, decisão, saída ou responsabilidade que não esteja clara em outro lugar. Duplicação de apresentação pode ser reduzida; diferença de autoridade ou de digest precisa permanecer explícita. A avaliação acima é documental e não mediu custo, capacidade ou necessidade de um serviço implantado.

## 8. Decisões necessárias antes de corrigir e sincronizar

| Tema a reconciliar | O que já está estabelecido | O que precisa ser decidido/registrado |
|---|---|---|
| Aprovação da derivada | Scans e rebuild existem nas fontes; `DEC-034` aprova aplicar o fluxo às duas camadas. | Se o relato atual confirma execução do fluxo completo ou outro tipo de certificação; modalidade e autoridade de cada camada. Atualizar `FACT-075`/`QUE-050` só após conciliação autorizada. |
| Assinatura e SLSA | SBOM Trivy/Wiz no JFrog está registrado (`FACT-047`); responsável informa assinatura/attestation existentes. | Quais artefatos/camadas estão cobertos, qual geração e verificação estão operacionais e o que permanece proposta KMS/Kyverno. Não confundir assinatura do bundle de exceções com assinatura da imagem. |
| Whitelist, SHA e raw | REL e CTX descrevem aquisição/digest/raw; os textos consolidados não detalham todo o percurso. | Campos canônicos, finalidade do “último digest”, ação com conteúdo igual, raw no ECR, ordem/retenção e controles antes de publicação. Sem mudar rebuild diário por suposição. |
| Catálogo e publicação | ECR e aliases/digests estão documentados; catálogo aprovado da derivada foi relatado. | O que “catálogo” representa: repositório, metadado de aprovação, visão Hub ou outra fonte; qual fato libera uso. |
| Escopo de consumidores | Cadeia conteinerizada conhecida; `FACT-027` e DOC2 reconhecem outro caminho de dados e inventário incompleto. | Quais runtimes entram no produto, como identificar consumidores diretos/indiretos e quais cadeias devem ter diagramas próprios. Não exigir Dockerfile em todos os casos. |

### Sincronização recomendada, somente depois da revisão

1. **Consolidar o processo:** registrar correções de fatos/perguntas/decisões nos canônicos e ajustar a referência end-to-end; preservar o histórico e a procedência, sem reclassificar proposta como medição.
2. **Alinhar documentação do repositório:** rever [Arquitetura](../processo/ARQUITETURA.md), [especificação da UI](ESPECIFICACAO.md) e trechos afetados de [Estado](../poc-deteccao-e-correcao/STATUS.md), especialmente aprovação derivada e artefatos.
3. **Alinhar UI e contexto:** atualizar nós, relações, legendas, rótulos e exemplos coerentes nas telas; manter separação entre processo informado, proposta de integração e dados DEMO. Atualizar orientações de continuidade para não restaurar a versão conflitante.
4. **Conferir o conjunto:** validar diagrama e navegação, cenários de erro/dado ausente e rastreabilidade imagem → versão/digest → tentativa → decisão → publicação → consumidor. Essa conferência futura não está executada nesta análise.

## 9. Alcance da entrega

Esta análise confronta os 14 nós, as relações sequenciais e caminhos relevantes ausentes usando código, documentação e relato. O arquivo é um instrumento de revisão, não a nova fonte canônica do processo. Não houve acesso aos serviços corporativos, inspeção de jobs, execução de CI, teste de cliques ou alteração da interface. Não há conclusão sobre eficácia de um controle implantado nem decisão de substituir ferramentas.
