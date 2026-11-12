# Preparação e execução do piloto no trabalho

**Estado em 12/11/2026: preparação documentada; piloto ainda não executável.** Esta página identifica o material necessário para implementar e parametrizar a trilha Distroless. Não contém comandos de uma automação já entregue. Os workflows, Dockerfiles e resultados corporativos originais ainda não foram examinados neste repositório.

O objetivo é aproveitar o [processo existente das três camadas](../processo/ARQUITETURA.md) para acompanhar **base certificada → base derivada pela plataforma → imagem de aplicação**, em cada caminho, Quarkus e Angular. Uma ancestral comum aos dois caminhos é hipótese, não premissa. As bases atuais continuam em uso. Depois da primeira passagem, o piloto deve repetir o percurso com correção disponível e demonstrar quais artefatos foram reconstruídos e testados.

Leia esta preparação junto da [especificação](ESPECIFICACAO.md) e do [plano de implementação](PLANO.md). A reprodução dos experimentos anteriores está no [runbook da POC de detecção e avaliação](../poc-deteccao-e-correcao/RUNBOOK.md); executá-lo não substitui o piloto nem é requisito obrigatório para iniciá-lo.

## 1. Partir do processo já documentado

O AS-IS, suas responsabilidades e divergências estão na [arquitetura compartilhada](../processo/ARQUITETURA.md), sem necessidade de consultar um vault local. Esta preparação localiza os pontos concretos de entrada/saída nos workflows e projetos reais. Não reabre a adoção dos controles já informados nem transforma informação ausente do pacote público em ausência de capacidade corporativa.

Os modos Quarkus JVM/nativo e Angular estático/SSR serão escolhidos pelos projetos existentes, conforme a especificação. Não é necessário implementar todos esses modos no mesmo piloto.

## 2. Reunir seis amostras, com escopo limitado

Use referências internas e cópias saneadas. Uma amostra pode atender mais de uma linha; não é necessário exportar o catálogo inteiro nem todos os históricos. Segredos permanecem nos mecanismos de credenciais existentes. Não coloque tokens, valores de secrets, dados de clientes ou nomes internos de organização no repositório público.

| Amostra | Material concreto a localizar no trabalho | Para que será usado |
|---|---|---|
| **1. Entrada autorizada** | Uma entrada do manifesto de origens e a saída de uma execução que resolveu tag/digest/plataforma; referência do repositório remoto JFrog e localização do último digest. | Parametrizar a aquisição da variante Distroless pelo percurso permitido e aproveitar a comparação já existente. |
| **2. Base certificada** | Dockerfile/receita e workflow reutilizável correspondentes; nomes e tipos dos inputs; outputs; referência de uma tentativa com digest final e gate. | Identificar onde compor/selecionar a base mínima e entregar a saída à plataforma, mantendo os controles existentes. |
| **3. Base derivada** | Uma receita de cada caminho, Quarkus e frontend, e a interface do workflow que as constrói, verifica e publica. Registrar qual base pai é resolvida no `FROM`. | Separar o runtime e as capacidades da plataforma das dependências específicas das aplicações. |
| **4. Duas aplicações** | Dockerfile, manifesto de dependências/lockfile, comando de build e testes do backend e do frontend selecionados. Identificar portas, configuração necessária e resultado funcional esperado. | Produzir os artefatos das aplicações e validar comportamento, além de apenas observar que o processo iniciou. |
| **5. Segurança e correção** | De uma tentativa representativa, referências a scan, SBOM, assinatura/attestation e decisão do gate. Selecionar um achado com componente, versão, origem da informação e correção disponível, quando houver. | Vincular a avaliação ao digest certo e escolher uma atualização verificável. Não reexportar toda a base de vulnerabilidades. |
| **6. Publicação e execução efêmera** | Destinos de teste no ECR, workflow/meio existente de executar as duas aplicações e referência da identidade autorizada; política de retenção/limpeza e limite de duração. | Isolar os artefatos do piloto, executar os testes e registrar a remoção dos recursos temporários. Nenhuma implantação é acionada por esta página. |

**Resultado desta coleta:** uma ficha privada do piloto com referências aos arquivos e execuções. No material compartilhável, usar nomes neutros como “workflow de certificação” e “destino ECR do piloto”, preservando a correspondência no ambiente autorizado. Uma referência de secret informa seu uso; nunca contém seu valor.

### Resolver o comportamento das duas amostras

- **Backend Quarkus:** registrar JVM ou nativo, versão do Java quando aplicável, arquitetura de destino, formato produzido pelo build, bibliotecas nativas necessárias e comando de inicialização. Não assumir que o exemplo JVM da POC representa o projeto real.
- **Frontend Angular:** registrar se publica arquivos estáticos ou executa SSR. Node/npm usados na construção não significam que ambos devam integrar a imagem final. No caminho estático, identificar o servidor/configuração atuais; no SSR, o runtime e o artefato de servidor.
- **Ambos:** apontar os testes já existentes, incluindo as verificações essenciais do ambiente: configuração, endpoints/rotas relevantes e dependências necessárias. Uma inicialização sem erro, sozinha, não prova equivalência funcional.

## 3. Mapear os contratos para outputs reais

Use os [contratos entre camadas da arquitetura compartilhada](../processo/ARQUITETURA.md#3-contratos-e-evidências-entre-camadas). Para cada fronteira, registre na ficha privada o workflow/output que fornece o dado, uma tentativa de exemplo, a evidência correspondente e o responsável. Marque como ausente o campo não encontrado; só essa lacuna justifica adaptar a coleta. Não criar outra definição dos contratos nem um banco/API por consequência da documentação.

Além desse mapeamento, o ensaio efêmero precisa registrar o digest da aplicação executada, testes, resultado e cleanup; a atualização precisa ligar os artefatos anteriores/novos às reconstruções afetadas. SBOM, scan, assinatura e attestation devem apontar ao artefato-alvo; presença de arquivos numa pasta não comprova esse vínculo.

## 4. Pontos de encaixe a confirmar antes de implementar

### Aquisição e estado existente

Identificar a referência que o runner consegue acessar pelo JFrog e o mecanismo corporativo de autenticação, sem duplicá-lo no script. Registrar como o repositório remoto atualiza manifestos e qual digest foi realmente entregue. Uma consulta agendada ao proxy pode receber conteúdo em cache; o piloto não presume acesso direto permitido ao registry público nem um parâmetro que ignore o cache.

Localizar onde a rotina mantém o último digest e como distingue primeira observação, mudança, repetição e falha. A implementação deve respeitar a política atual de rebuild diário; digest igual não autoriza cancelar o build por suposição. Também é necessário definir quem grava esse estado quando há execuções simultâneas. SQLite da POC não é requisito do piloto.

### Construção e decisão de segurança

A Distroless final não é o lugar para executar um gerenciador de pacotes. A receita precisa selecionar uma base oficial atualizada ou compor conteúdo corrigido durante a construção, com dependências e testes definidos na especificação. Escolher a via de composição interna exige uma receita verificável; ela ainda não foi homologada por este projeto.

Para cada achado selecionado, identificar o digest e a camada afetados, a correção disponível e o controle que aceita ou rejeita o resultado. Se não houver fix, a saída é o tratamento de risco/mitigação previsto no processo vigente, com responsável e reavaliação; não uma imagem declarada corrigida. O piloto não promete eliminar todas as vulnerabilidades nem cria outra autoridade de aprovação.

### Publicação, consumidores e teste efêmero

Definir destinos de teste e quem pode publicar neles. Conservar as regras existentes de versão, digest, imutabilidade e promoção de aliases. Não usar a aprovação de uma base para aprovar automaticamente sua derivada.

Listar somente os consumidores escolhidos para o piloto e seus workflows. Determinar como recebem a referência da base, quem pode solicitar o rebuild e como o resultado retorna. A autonomia pretendida é uma sequência parametrizada com resultados observáveis, respeitando os gates atuais — não uma permissão para contorná-los.

Na execução efêmera, definir o ambiente permitido, testes, configuração disponível sem expor segredos, timeout e responsável/rotina de cleanup. Reservar referências para logs e resultados, inclusive em falha. O mecanismo concreto depende do ambiente escolhido; esta preparação não pressupõe EKS, EC2 ou um serviço novo.

## 5. Quando a preparação está concluída

Use estas condições como aceite da preparação, não como declaração de que já foram atendidas:

- [ ] As variantes e os dois modos de aplicação estão definidos a partir dos projetos reais; as bases atuais continuam disponíveis.
- [ ] As interfaces de receita/workflow, parâmetros de origem/destino e estado foram localizados nos mecanismos existentes; as adaptações necessárias estão identificadas para implementação.
- [ ] Está definido de onde virão digest, relação com o pai, tentativa, evidências e decisão de cada camada, incluindo como falha/ausência de prova será registrada.
- [ ] Os casos antes/depois de SO, runtime e dependência foram delimitados, com fix disponível e fontes ou pendência explícita. Uma amostra inicial permite mapear o contrato; não fecha automaticamente as três classes de correção.
- [ ] Os dois consumidores e a execução efêmera têm entradas, testes, resultados e limpeza definidos, dentro do acesso autorizado.
- [ ] O recorte, as decisões abertas e a ordem das tarefas foram revisados contra o plano, sem exigir que a implementação já esteja pronta.

Receitas, hooks, execuções e runbook validado são entregas posteriores de P1–P6 no [plano](PLANO.md). Concluir esta preparação libera o trabalho de implementação definido; não declara o piloto pronto para executar nem dispensa a revisão dessas entregas.

**Situação atual:** esta documentação organiza o trabalho e o material a localizar. Ainda faltam as amostras corporativas, a definição das receitas e a implementação/validação do pacote do novo piloto. Os testes antigos de digest e correlação permanecem reproduzíveis no seu próprio escopo; não comprovam a construção Distroless nem a propagação pelas aplicações.

## 6. Sequência de execução quando o pacote estiver implementado

Esta é a ordem das entregas futuras, não uma lista de comandos já disponíveis:

1. Revisar receitas e parâmetros definidos em P0; implementar a base mínima e as derivadas com os hooks necessários dos workflows existentes.
2. Executar controles/gates e publicação de teste; conservar os digests e as evidências de cada camada.
3. Construir e verificar as aplicações Quarkus e Angular no ambiente efêmero autorizado; registrar o pai realmente usado e a limpeza.
4. Repetir os percursos afetados pelos fixes de SO/runtime/dependência, incluindo falhas e retomada previstas no plano.
5. Consolidar os comandos efetivamente executados, resultados e diagnóstico neste roteiro; validar a reprodução antes de apresentar o pacote como executável.

Os critérios e tarefas detalhados estão no [plano](PLANO.md); a ordem não libera execução produtiva nem contorna gates. Volte à [especificação](ESPECIFICACAO.md) para o recorte ou ao [índice](README.md). A UI permanece congelada nesta etapa.
