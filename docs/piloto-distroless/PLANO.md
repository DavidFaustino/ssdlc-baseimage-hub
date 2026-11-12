# Plano de execução do piloto Distroless

**Estado: planejamento em revisão; nenhuma história executada por este documento.** Este plano entrega uma trilha adicional, com duas aplicações existentes, preservando as bases atuais. Não autoriza criar scripts, alterar workflows ou executar o ambiente antes da revisão do recorte e dos contratos. Leia [Preparação](EXECUCAO.md) e [Especificação](ESPECIFICACAO.md).

## 1. Como acompanhar

Cada história só muda para concluída quando sua entrega e evidência de aceite estiverem disponíveis. Uma implementação futura deve registrar executor, revisão, tentativa e resultado; não transformar a data deste plano em data de execução. Não há prazos estimados antes de conhecer aplicações, acesso, runners e artefatos.

| Fase | Entrega que libera a seguinte | Condição de parada |
|---|---|---|
| **Preparação — P0.** | Insumos e recorte revisados, duas aplicações escolhidas, contratos corporativos identificados. | Modo de execução/variante, fonte, autoridade de gate ou escopo de teste não definidos. |
| **Receitas — P1/P2.** | Base certificada e derivadas reproduzíveis, compatíveis e verificáveis por digest. | Hardening depende de shell/instalação na imagem final; runtime incompatível; origem não permitida. |
| **Integração — P3.** | Hooks na matrix e nos controles atuais, publicação de teste e lineage por tentativa. | Alteração de produção implícita, permissão excessiva ou perda de evidência/identidade. |
| **Execução — P4/P5.** | Duas aplicações verificadas e correção propagada nos casos de SO/runtime/dependência. | Sem fix real, gate/teste falho ou uso do digest novo não comprovado. |
| **Consolidação — P6.** | Evidências, runbook validado e decisão sobre a trilha. | Comandos não reproduzidos ou limites ocultos; produção não é liberação automática. |

As atividades independentes podem ocorrer em paralelo: levantamento das duas aplicações; desenho das derivadas por stack; seleção dos casos de correção; mapeamento dos hooks existentes. A publicação de uma derivada depende de sua base certificada aprovada; a prova de propagação depende da cadeia de builds e testes pronta.

## 2. Épicos, histórias e tarefas

Todos os itens abaixo estão **a fazer**. Nomes de entregáveis são funções, não arquivos já existentes. Os caminhos de receitas, scripts, schemas e workflows serão definidos na revisão técnica; este plano não cria links para arquivos futuros.

### P0 — Preparar o recorte e preservar a operação atual

**P0-H1 — Confirmar o processo e os contratos do piloto.**

- **Tarefas:** levantar entradas/saídas da matrix diária e allowlist; mapear origem/proxy/`raw`/ECR; identificar gates, responsáveis e artefatos existentes; conciliar documentação antiga com o relato atual de aprovação, assinatura e SLSA; delimitar recursos e publicação de teste.
- **Entrega:** preparação preenchida e contrato de cada camada com identidades, autoridade e fronteiras do teste.
- **Aceite:** percurso Certified → Arch → aplicações descrito sem trocar ferramentas; entradas inacessíveis/lacunas identificadas; nenhuma nova autoridade ou ação produtiva presumida.

**P0-H2 — Selecionar backend e frontend reais.**

- **Tarefas:** registrar repositórios/revisões autorizados; ler configuração/Dockerfiles/lockfiles; confirmar Quarkus JVM ou nativo e Angular estático ou SSR; levantar plataformas, bibliotecas, configuração, dependências externas e testes disponíveis.
- **Entrega:** ficha das duas aplicações e critérios de funcionalidade representativos, usando o documento de preparação.
- **Aceite:** cada aplicação tem comando/artefato de build e contrato de runtime conhecidos; os testes exercitam comportamento real; não substituir ambos os projetos por fixtures genéricas.

**P0-H3 — Escolher variantes e casos de correção.**

- **Tarefas:** conferir suporte/arquitetura/ABI das variantes; decidir se uma ancestral comum atende ou se há bases distintas; localizar fixes reais de SO, runtime e dependência aplicáveis aos componentes selecionados; registrar entradas anteriores/corrigidas e origem da informação.
- **Entrega:** matriz de variante por stack e casos antes/depois com fontes e escopo.
- **Aceite:** nenhuma base universal presumida; cada caso tem componente/versão afetada, correção disponível e caminho de aquisição permitido; o que não existir permanece pendente, sem fabricar vulnerabilidade ou resultado.

### P1 — Produzir a imagem base certificada mínima

**P1-H1 — Definir e implementar a receita da trilha adicional.**

- **Tarefas:** fixar origem por digest/plataforma; adaptar hardening à construção mínima; separar ferramentas de build do artefato final; definir usuário, arquivos necessários, permissões e comando de execução aplicável; manter bases atuais intactas.
- **Entrega:** receita versionada e registro dos componentes/configurações incorporados; scripts somente após a revisão que liberar essa implementação.
- **Aceite:** build resulta em artefato de identidade verificável e conteúdo mínimo descrito; não depende de shell/package manager na imagem final; nenhum `apt upgrade` improvisado no contêiner final.

**P1-H2 — Reutilizar certificação e evidências da primeira camada.**

- **Tarefas:** executar os controles existentes no ponto autorizado; vincular scan, SBOM, assinatura/SLSA e decisão ao digest construído; publicar no destino de teste pelo processo existente.
- **Entrega:** base certificada da trilha, digest e artefatos da tentativa, incluindo resultado negativo quando ocorrer.
- **Aceite:** origem e filho rastreáveis, gate competente aplicado, publicação correspondente à decisão; falha não promove alias nem sobrepõe a base atual.

### P2 — Compor derivadas da plataforma por contrato de runtime

**P2-H1 — Derivada compatível com o backend Quarkus.**

- **Tarefas:** usar a base certificada por digest; incorporar runtime/capacidades necessários no build; conferir Java/empacotamento ou binário nativo/ABI conforme escolha P0; validar certificados, bibliotecas, usuário e parâmetros; executar controles da derivada.
- **Entrega:** receita e derivada Quarkus com vínculo ao pai e evidências por digest.
- **Aceite:** compatível com o modo real da aplicação; ferramentas de compilação não aparecem no runtime por acidente; gate da segunda camada e publicação de teste identificados.

**P2-H2 — Derivada compatível com o frontend Angular.**

- **Tarefas:** usar base certificada por digest; separar Node/npm de build do runtime; no modo estático, incluir/validar servidor HTTP e configuração necessários; em SSR, compor runtime Node compatível e dependências; executar controles da derivada.
- **Entrega:** receita e derivada Angular correspondente ao modo real, com vínculo ao pai.
- **Aceite:** não presume Node em runtime estático nem servidor HTTP fornecido por uma base vazia; rotas, arquivos, permissões e inicialização têm contrato verificável; gate existente aplicado.

### P3 — Encadear pelos workflows existentes

**P3-H1 — Adicionar a trilha à matrix e ao catálogo autorizado.**

- **Tarefas:** mapear o contrato atual antes de adaptar; inserir apenas entradas/parametrização necessárias; conservar whitelist de origem, plataforma e digest; conferir aquisição pelo proxy e equivalência do conteúdo; manter agenda e bases atuais.
- **Entrega:** alteração revisável dos hooks existentes e parâmetros da trilha de teste, quando autorizada a implementação.
- **Aceite:** não cria outro agendador/detector por padrão; valida entradas fechadas; identifica tentativa, falhas e resultado; credenciais/escopo seguem mecanismos atuais.

**P3-H2 — Registrar identidade, decisões e dependências entre builds.**

- **Tarefas:** aproveitar artefatos existentes; registrar pai/filho por digest/plataforma, receita/commit, execução, scans, gate e publicação; mapear derivadas e aplicações afetadas; definir proteção contra repetição e recuperação das referências.
- **Entrega:** registro de lineage e contrato de encaminhamento/repetição no armazenamento já definido pelo processo, ou lacuna específica para decisão.
- **Aceite:** origem → certificada → derivada → aplicação pode ser percorrida com evidências; publicação não é contada como consumo; nenhum banco/serviço novo escolhido sem necessidade demonstrada.

### P4 — Verificar as duas aplicações em ambiente efêmero

**P4-H1 — Construir e executar o backend existente.**

- **Tarefas:** construir o artefato real com toolchain compatível; usar a derivada por digest na imagem final; executar scans/testes atuais; iniciar em recurso efêmero autorizado; verificar health, fluxo representativo, TLS/DNS/configuração necessários e encerramento.
- **Entrega:** digest da aplicação Quarkus, vínculo ao pai, logs/resultados e confirmação de limpeza.
- **Aceite:** testes correspondem ao digest final e ao commit escolhido; timeout/falha produz resultado controlado; compilar ou rodar somente JVM fora do contêiner não fecha a história.

**P4-H2 — Construir e executar o frontend existente.**

- **Tarefas:** construir com lockfile/configuração reais; usar a derivada por digest no estágio final; iniciar efemeramente; verificar página, assets, rota profunda/refresh ou SSR conforme modo, e interação representativa com backend conforme acesso autorizado; encerrar e limpar.
- **Entrega:** digest da aplicação Angular, resultados e ligação aos artefatos/derivada.
- **Aceite:** fluxo real atende ao contrato P0, sem exigir navegação manual para fechar a prova; falha de backend/dependência externa fica distinguível de falha da base; recursos efêmeros removidos.

### P5 — Demonstrar correção e propagação na cadeia

**P5-H1 — Correção de pacote do SO.**

- **Tarefas:** comprovar versão anterior/fix aplicável; selecionar origem corrigida ou receita de build permitida; reconstruir base certificada e filhos afetados; repetir gates e testes das aplicações; comparar versões finais e lineage.
- **Entrega:** evidência antes/depois do caso de SO, com todos os digests e decisões do percurso afetado.
- **Aceite:** correção comprovada no conteúdo pertinente e uso do novo pai demonstrado; simples troca de tag, data, hash ou redução de contagem de CVEs não basta; sem fix disponível não se declara correção.

**P5-H2 — Correção de runtime ou capacidade da plataforma.**

- **Tarefas:** localizar a camada que introduziu o componente; alterar somente entrada/receita necessária; reconstruir essa camada e consumidores afetados; conferir versão final, funcionalidade e gates.
- **Entrega:** caso de runtime com origem da correção, pai/filho e resultados dos consumidores pertinentes.
- **Aceite:** runtime não é confundido com pacote do SO; bases/consumidores não afetados não recebem mudança arbitrária; quando runtime já está na base certificada, a propagação começa ali.

**P5-H3 — Correção de dependência da aplicação.**

- **Tarefas:** identificar dependência/fix e repositório afetado; alterar build/lockfile conforme processo; reconstruir a aplicação e repetir suas verificações; registrar que base/derivada foram usadas.
- **Entrega:** caso de dependência com novo digest da aplicação e evidências de teste/scan.
- **Aceite:** correção da dependência comprovada; não se impõe rebuild de base sem alteração/afetação; o contrato da aplicação continua atendido.

**P5-H4 — Falhas, repetição, espera e reversão.**

- **Tarefas:** exercer origem indisponível/digest divergente, falta de fix, falha de build/gate/teste e repetição da tentativa; conferir advisory novo com digest estável; preservar referências anteriores e validar reversão no escopo de teste.
- **Entrega:** resultados negativos e de retomada ligados às tentativas, com recursos efêmeros limpos.
- **Aceite:** nenhuma falha/entrada desconhecida gera promoção favorável; sem duplicação de efeito externo na repetição; não há patch manual dentro do runtime nem rollback produtivo implícito. A rotina diária atual não é desativada por esta classificação.

### P6 — Entregar reprodução e decisão sobre a trilha

**P6-H1 — Consolidar evidências e runbook do piloto.**

- **Tarefas:** inventariar artefatos executáveis e dependências; escrever sequência com entradas, processamento, comandos, intermediários, resultados e diagnóstico; registrar distribuição dos scripts/configurações sem segredos; repetir o percurso em ambiente limpo autorizado.
- **Entrega:** runbook do novo piloto e pacote de receitas/scripts/evidências efetivamente produzidos, separados da POC anterior.
- **Aceite:** outra pessoa consegue seguir sem presumir arquivos locais ausentes; resultados são verificáveis por digest/versão/tentativa; limites e casos pendentes aparecem no ponto afetado; nenhum comando futuro é apresentado como já testado.

**P6-H2 — Propor continuidade, ajuste ou descarte.**

- **Tarefas:** resumir compatibilidade, correções comprovadas, esforço de manutenção e falhas; comparar com a trilha atual no escopo observado; explicitar se houve via oficial ou composição própria e o que ficou sem prova.
- **Entrega:** decisão proposta sobre manter/adaptar/dispensar a trilha e condições para eventual expansão.
- **Aceite:** não usa desempenho da antiga comparação A/B como critério corporativo; não promete zero CVEs; implantação produtiva e migração de outras stacks permanecem decisões separadas.

## 3. Dependências e condição de rollout

P0 libera o desenho concreto das receitas. Os desenhos de receitas e hooks podem ocorrer em paralelo. Gates e publicações de P1/P2 utilizam interfaces existentes já compatíveis ou dependem da conclusão do hook correspondente em P3-H1; não se publica antes dessa condição. A base certificada aprovada libera o build da derivada correspondente. P4 demonstra as aplicações; P5 repete os percursos afetados por cada correção. P6 consolida somente o que tiver evidência.

**Avanço além do ambiente de teste:** requer resultados funcionais das duas aplicações, correções selecionadas comprovadas, gates e lineage das três camadas, tratamento de falhas e reversão, documentação reproduzida e aprovação no processo competente. Caso parcial deve ser apresentado como parcial. Até essa decisão, a trilha atual continua sendo a referência operacional.

Não há nova exigência de operação contínua como condição artificial para encerrar a POC antiga. O que encerra **este piloto** são os resultados explicitamente definidos aqui, revistos com os insumos reais.
