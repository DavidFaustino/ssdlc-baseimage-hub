# Próxima etapa: tornar o Hub útil no processo atual

O marco técnico está em [Estado atual](STATUS.md). A evolução funcional do **protótipo local** foi autorizada para mostrar e ensaiar quatro capacidades: acompanhar a execução, rastrear a imagem até o consumo, encaminhar ações pelos sistemas existentes e investigar bloqueios. Isso **não** autoriza alterar o CI, conectar serviços corporativos ou publicar uma decisão de certificação. A arquitetura e os critérios desta etapa estão em [Arquitetura](ARCHITECTURE.md), seção 6.

## Entrega local — histórias e tarefas executáveis

Cada história usa **um conjunto coerente de dados demonstrativos**. Toda imagem, run, gate, evidência e consumidor da demonstração compartilha identificadores e digests compatíveis. O operador deve poder percorrer a cadeia sem saltar para uma POC histórica como se fosse operação atual.

### H1 — Saber o que executou e quem precisa agir

1. Registrar no exemplo cada tentativa da matriz diária com identificador, horário, imagem, fase, resultado, último evento e motivo de bloqueio.
2. Mostrar na Visão geral as tentativas recentes, atrasadas, bloqueadas e desconhecidas; abrir a tentativa na ficha da imagem.
3. Mostrar responsável **informado** por fase; quando não houver mapeamento validado, exibir “responsável a confirmar”.

**Aceite local:** ao escolher uma tentativa bloqueada, o operador encontra fase, horário, motivo, evidência disponível e próxima ação permitida. Execução ausente ou dado velho aparece como `unknown`, sem inferir sucesso.

### H2 — Seguir imagem, aprovação, publicação e consumo

1. Modelar a identidade por família, versão/alias, digest de índice, digest filho e plataforma; cada tentativa referencia essa identidade.
2. Ligar cada gate a resultado, evidência e autoridade responsável. Separar aprovação da primeira camada da pendência de aprovação equivalente da segunda.
3. Mostrar publicação no ECR separadamente de certificação; ligar aplicações e ambientes ao digest **efetivamente observado**, ou declarar consumo não confirmado.

**Aceite local:** a ficha responde “qual digest foi avaliado?”, “qual gate decidiu?”, “o que foi publicado?” e “quem consome esse digest?”. Alias ou tag mutável nunca substitui digest como identidade; ausência de vínculo não produz adoção presumida.

### H3 — Encaminhar trabalho sem usurpar o CI

1. Definir os pedidos de ação `encaminhar avaliação`, `solicitar atualização` e `repetir execução`, cada um com run/imagem, motivo, destinatário e referência de evidência.
2. No protótipo, ensaiar pedido e retorno **localmente** com confirmação visual de que nenhuma chamada externa foi feita; registrar pendente, aceito/rejeitado e motivo sem alegar execução real.
3. Documentar qual ferramenta existente executaria cada pedido em integração futura e quais permissões, confirmação humana e idempotência seriam exigidas.

**Aceite local:** um bloqueio oferece somente ações compatíveis com seu estado; pedir repetição não muda o gate nem o alias. Sem autorização, identidade ou destino definidos, a ação fica indisponível com motivo explícito.

### H4 — Investigar resultado e bloqueio

1. Oferecer, no contexto do run, linha do tempo e referências a recibo do CI, scans, SBOM CycloneDX e atestações SLSA **quando existentes**; não presumir como são assinadas.
2. Exibir o motivo técnico do bloqueio e a última evidência válida; permitir navegar entre fase, run, imagem, gate, publicação e consumidor.
3. Ensaiar falha de fonte, digest divergente, gate reprovado, evidência ausente e tentativa repetida, com resultados distintos.

**Aceite local:** cada resultado tem razão e procedência visíveis. Evidência faltante e divergência ficam `unknown` ou bloqueadas e não tornam a imagem certificada/publicada.

### Verificação cruzada da entrega local

- Abrir o protótipo sem backend e percorrer um sucesso, um bloqueio e um estado desconhecido do resumo à evidência; conferir links e retorno ao ponto de partida.
- Conferir que digest, plataforma, run, gate, publicação e consumo correspondem em cada tela e que dados fictícios estão marcados como demonstrativos.
- Conferir que botões de pedido não chamam Actions, JFrog, ECR ou EKS; nenhum ato de aprovação ou publicação pode ser simulado como real.
- Confrontar textos e telas com o AS-IS abaixo e com [Estado atual](STATUS.md); registrar lacunas corporativas como pendências, sem criar responsáveis, datas ou resultados.

## Integração real — dependências ainda abertas

1. Confirmar com donos dos sistemas os contratos de leitura de Actions, JFrog, scans, recibos, SBOM, atestações, ECR e EKS, além de IDs compartilhados e frescor de cada fonte.
2. Confirmar autoridade, responsável e registro de aprovação dos dois gates; o fluxo equivalente da segunda camada continua pendente.
3. Definir autenticação, RBAC, auditoria, confirmação e proteção contra repetição para cada pedido de ação; o Hub deverá chamar **ferramentas existentes** em vez de substituir seus gates.
4. Testar em ambiente autorizado o vínculo `origem → proxy → digest avaliado → ECR → consumidor`, inclusive cache, plataforma, falha, retomada e dados desatualizados.
5. Só então decidir implantação, mecanismo de integração e eventual papel de Renovate; a avaliação de Renovate é estudo separado, não requisito da entrega local.

## Trabalho técnico anterior que continua válido

O roteiro abaixo preserva a linha de investigação da POC. Ele não deve ser confundido com a implementação das quatro capacidades do Hub.

| Ordem | Tarefa | Entrega verificável | Critério para avançar |
|---|---|---|---|
| 1 | Confirmar com os responsáveis a cadeia upstream → JFrog → matriz diária → primeira certificação → segunda camada → ECR → aplicação/ambiente. | Diagrama AS-IS validado, dono de cada gate e inventário do que CI e scanners já registram. | Local da aprovação da primeira camada, lacuna da segunda e identidade de cada evidência conhecidos; dúvidas marcadas. |
| 2 | Definir a menor capacidade adicional: observar tag/plataforma/digest, relacionar pacote e advisory e registrar candidata. | Contrato de entrada, saída, estado e erro, com responsável pelo baseline e pelo recibo. | `validate_candidate` apenas solicita avaliação; `wait`, `unknown` e duplicata têm comportamento e retomada definidos. |
| 3 | Fechar a fronteira do proxy: origem, cache, aquisição e conteúdo efetivamente certificado. | Regra de frescor e de aquisição por digest, com prova da cadeia origem → proxy → digest certificado. | Tag em cache não é tratada como estado atual da origem; divergência bloqueia a candidata. |
| 4 | Revisar a interface inteira como produto: Imagens (lista e ficha com jornada e consumo), automações, cobertura, arquitetura, roadmap e seus detalhes. | Mapa tela → regra → fonte → evidência → responsável; protótipo corrigido para separar dado fictício, POC comprovada e capacidade proposta. | O operador consegue responder o que mudou, por que a candidata existe, quem decide e o que foi publicado/consumido; a UI não sugere aprovação automática. |
| 5 | Preparar **uma** imagem piloto autorizada e seus resultados esperados. | Plano curto: imagem, plataforma, caso de correção, fontes, testes positivos/negativos, responsáveis e limite de atuação. | Critério de acerto e de parada definidos antes de rodar. |
| 6 | Repetir o caso no ambiente de destino, ligando o recibo ao gate que já existe. | Evidências para digest estável, mudança, fix ausente, fonte divergente, erro de acesso e bytes distintos no proxy. | Nenhum caso incompleto aprova ou promove imagem; resultado e limitações revisáveis. |
| 7 | Decidir o formato reutilizável: script na matriz atual, adaptador ou componente separado; e o papel eventual de Diun/Vunnel. | Decisão arquitetural baseada no processo real e na prova do piloto. | Explicar que função nova cada peça agrega, quem a opera e como o estado é recuperado. |
| 8 | Se BMAD for usado no desenvolvimento, levar **uma** história real delimitada pelo [contrato de workflow](WORKFLOWS.md). | História, testes, revisão, recibo e decisão final vinculados ao contrato do Hub. | Não confundir G0/G1 do desenvolvimento com certificação, nem o Loop sintético com validação do ciclo de domínio. |

As tarefas 1–3 definem o contrato. O desenho da interface (4) pode começar em paralelo, mas só fica alinhado quando essas regras forem confirmadas. A execução do piloto (6) depende do plano autorizado (5). A escolha de ferramenta (7) depende do resultado e **não exige** inventar uma operação contínua fora do escopo desta POC. O trabalho de workflow (8) é uma frente separada e pode ser planejado em paralelo sem mudar a decisão de arquitetura.

Para conferir as provas que já existem, siga o [runbook](RUNBOOK.md) e o [inventário de evidências](../poc/EVIDENCE.md). Para discutir o encaixe, comece por [Processo atual e proposta](ARCHITECTURE.md).
