# Revisão BMAD de arquitetura — interface e processo do Base Image Hub

**Método:** lente de arquitetura do BMAD (Winston). **Escopo:** as sete páginas navegáveis, seus detalhes e regras aparentes, confrontados com o processo documentado e com os resultados da POC. **Natureza:** parecer de desenho; a interface não foi executada contra serviços reais.

## Veredito

O protótipo comunica bem a **jornada geral** da imagem e a diferença entre certificação e consumo. Ainda não representa o **controle operacional** que motivou a POC: reconhecer uma correção aplicável a um digest e plataforma, avaliar uma candidata com evidência verificável e entregá-la ao gate existente sem aprová-la automaticamente. A interface atual contém dados fixos e não está ligada ao CI, registry, proxy, scanners ou correlator. Isso está declarado em [README](../../README.md) e [estado atual](../STATUS.md), mas precisa ser visível em cada decisão sugerida pela UI.

A recomendação arquitetural é preservar o protótipo como **mapa de navegação**, corrigir a cadeia e desenhar um percurso de candidata e evidência antes de especificar integração ou escolher ferramenta de observação. O processo existente de build e aprovação continua sendo a autoridade; a POC acrescenta informação e um pedido de avaliação. Ver [AS-IS e TO-BE](../ARCHITECTURE.md).

## Cobertura de toda a interface

| Visão do HTML | O que comunica bem | Desalinhamento ou regra ausente | Fonte do processo |
|---|---|---|---|
| **Visão geral** (`overview`, `flow`, `alerts`, linhas 41–43) | Prioridades, rotina, etapas e falhas em um lugar. | Os totais são fixos; “certificadas” e “precisa de atenção” não mostram a identidade, a fonte e a data da evidência. Não existe fila de candidatas ou de correções que exijam decisão. | [Contrato TO-BE](../ARCHITECTURE.md#3-to-be-encaixe-proposto-sem-integração-implantada), [POC](../POC.md) |
| **Jornada das imagens** (`journey`, linhas 40 e 45) | Separa build, validação, certificação, homologação e produção. | O estado é um marcador por etapa, sem versão/digest do artefato, execução, gate, decisor ou prova. “Sem evidência” agrega situações diferentes: não iniciado, dado desatualizado e fonte inacessível. | [AS-IS](../ARCHITECTURE.md#1-as-is-da-imagem-upstream-à-aplicação), [contratos](../ARCHITECTURE.md#contratos-entre-etapas) |
| **Automações** (`autoPage`, `showAuto`, linhas 46 e 61) | Distingue execução, atualização da fonte e certificação; mostra coleta degradada. | Não exibe run ID, entrada, artefato, checkpoint, recibo, dependência do gate ou ação de recuperação. O “sucesso” de uma rotina pode parecer sucesso da avaliação da imagem. | [Estados e retomada](../WORKFLOWS.md#estado-e-retomada), [próxima etapa](../NEXT-STEPS.md) |
| **Catálogo** (`catalog`, `showImage`, linhas 47–48 e 59) | Dá acesso por imagem e indica certificação e consumo. | A entidade é nome/versão textual, não identidade OCI por tag, índice, manifesto filho, plataforma e digest. A contagem de CVEs não prova correção aplicável; falta pacote instalado, fonte, versão corrigida e exceção. | [Problema da POC](../POC.md#qual-problema-foi-exercitado), [contratos](../ARCHITECTURE.md#contratos-entre-etapas) |
| **Adoção e cobertura** (`coverage`, linha 49) | Diferencia catálogo declarado de uso observado e sinaliza coleta parcial. | Disponibilidade e uso precisam estar vinculados ao **digest certificado e ao digest consumido**, não só ao nome da imagem. Falta distinguir “não coletado”, “coleta parcial”, “não observado” e “confirmado sem uso”. | [AS-IS](../ARCHITECTURE.md#1-as-is-da-imagem-upstream-à-aplicação) |
| **Arquitetura** (`archNodes`, `architecture`, linhas 50–53) | Apresenta origem, certificação, publicação, derivação e consumidores. | A ordem desenhada põe ECR antes das imagens derivadas e omite o JFrog antes da matriz; [o processo documentado](../ARCHITECTURE.md#1-as-is-da-imagem-upstream-à-aplicação) mostra proxy → matriz/certificação → primeira aprovação → segunda camada/build/scan → ECR → aplicação. Também não separa o gate existente da primeira camada da aprovação ainda pendente na segunda. | [AS-IS](../ARCHITECTURE.md#1-as-is-da-imagem-upstream-à-aplicação), [TO-BE](../ARCHITECTURE.md#3-to-be-encaixe-proposto-sem-integração-implantada) |
| **Roadmap** (`tasks`, `roadmap`, linhas 54–55) | Mostra dependências e evolução. | “Entregue” na interface refere-se ao cenário fictício e pode ser confundido com capacidade implantada. Não aparecem como itens distintos o contrato de candidata, handoff ao CI, limite do proxy, evidência por digest e gate da segunda camada. | [Estado atual](../STATUS.md), [próxima etapa](../NEXT-STEPS.md) |

As ações navegáveis de filtro, detalhes e download do HTML operam **somente sobre o conjunto fixo em memória** (`images`, `automations`, `tasks`; [código](../../index.html)). Modais de imagem e automação avisam que evidências reais, logs e reexecução dependem de backend. Logo, nenhum botão atual altera estado operacional ou solicita aprovação. O [preview](../../preview.png) é uma imagem da mesma proposta, não uma prova adicional.

## Lacunas priorizadas pelo efeito no negócio

### 1. Corrigir o modelo de autoridade e a ordem da cadeia

A página de arquitetura precisa refletir explicitamente as **duas camadas**, a aprovação já existente da primeira, a lacuna de aprovação da segunda e a posição do JFrog. Caso contrário, um leitor pode inferir publicação e consumo depois de um único gate e confundir a decisão `validate_candidate` com certificação. A POC registra `image_approved=false` e não move alias; [resultado técnico](../POC.md#afirmações-e-cadeia-de-evidências). A interface deve nomear quem apenas propõe, quem revisa e qual sistema efetivamente publica. Os donos específicos ainda precisam ser confirmados no ambiente de destino.

### 2. Introduzir uma candidata com identidade e procedência próprias

Uma tela operacional precisa partir da **referência observada** (origem, repositório, tag, horário), resolver índice e manifesto filho por plataforma, vincular o **digest recebido pelo proxy**, inspecionar pacote e distro/suite e associar advisory, revisão da fonte e versão corrigida. Depois, exibir o recibo da correlação e a diferença para o baseline certificado. A entidade candidata não deve ser confundida com a imagem já certificada do catálogo. O [contrato proposto](../ARCHITECTURE.md#contratos-entre-etapas) descreve as entradas e falhas seguras; o [runbook](../RUNBOOK.md) reproduz partes separadas. A cadeia completa entre produtores e consumidor ainda não roda neste repositório.

### 3. Tornar `unknown`, frescor e divergência estados de primeira classe

Ao perder acesso, receber plataforma ambígua, pacote ausente, fix não confirmado, fonte divergente ou dados velhos, o Hub deve mostrar **qual elo falhou, última evidência válida, próximo responsável e se há reavaliação pendente**. Não transformar ausência de dado em “sem CVEs”, nem usar o verde de “concluída” para uma candidata cujo conteúdo não foi verificado. Advisory novo pode reavaliar o **mesmo digest**; trocar digest é outro evento. Esses invariantes aparecem no [TO-BE](../ARCHITECTURE.md#contratos-entre-etapas) e na [POC](../POC.md#afirmações-e-cadeia-de-evidências), não na navegação atual.

### 4. Ligar cada estado ao recibo e ao gate existente

Para cada imagem e etapa, permitir abrir a cadeia: entrada, hash/digest, execução, teste/scan, decisão, responsável, horário e artefato de saída. O painel de automações deve mostrar quando houve apenas coleta, quando houve decisão de candidata e quando o CI existente aprovou certificação. Reexecução precisa partir de estado confirmado, preservar bloqueios e impedir duplicação. Essa é uma regra de produto, mesmo que o protótipo continue estático por enquanto. Ver [workflows](../WORKFLOWS.md#estado-e-retomada) e [limites da POC](../STATUS.md).

### 5. Ajustar a navegação ao trabalho do operador

O percurso principal deveria responder, nesta ordem: **o que mudou na origem? → qual digest/plataforma/pacote foi verificado? → há correção aplicável? → qual decisão segura e por quê? → quem revisa? → o que foi certificado/publicado/consumido?** O catálogo e a jornada podem continuar como vistas, mas precisam abrir essa mesma linha de evidências. Automações e roadmap são suporte; não substituem a fila de candidatas, exceções e bloqueios.

## Contrato mínimo proposto para orientar a próxima versão da UI

| Entidade | Identidade mínima | Resultado exibido |
|---|---|---|
| Observação | Origem + repositório + tag + plataforma + revisão/horário | Índice, filho, bytes/hash, baseline anterior, evento novo ou duplicado. |
| Conteúdo inspecionado | Digest filho + digest entregue pelo proxy | Distro/suite, pacote fonte/binário, versão instalada, evidência da inspeção. |
| Correção | CVE/advisory + pacote + suite + revisão da fonte | Versão corrigida, frescor, conflito ou ausência de fix. |
| Candidata | Observação + conteúdo + correção + baseline | `validate_candidate`, `wait`, `unknown` ou duplicata, com razão e recibo; **nunca aprovação automática**. |
| Certificação e consumo | Digest certificado + gate + alias + digest da aplicação/ambiente | Decisão humana/CI, publicação e adoção verificáveis separadamente. |

Esta tabela é **proposta de arquitetura**, derivada dos contratos da [documentação](../ARCHITECTURE.md), e não implementação da UI. Deve ser validada com os responsáveis pelo processo antes de virar regra operacional. Ela também acomoda bases não Debian: o adaptador de advisory e o comparador de versões precisam variar por distribuição, enquanto a identidade da imagem e o gate permanecem comuns.

## Resultado da revisão

**Aproveitar:** estrutura de navegação, separação entre certificação e consumo, saúde de fontes e sinalização de coleta degradada. **Revisar antes de implementação:** diagrama da cadeia, entidades e estados por digest, fila/decisão de candidata, evidência por etapa, autoridade dos gates e promessas de “entregue” no roadmap. **Não inferir dos testes:** que a interface opera o CI, que Diun/Vunnel foram escolhidos, que o proxy atualiza a origem ou que a POC certificou uma imagem. Ver [marco atual](../STATUS.md).
