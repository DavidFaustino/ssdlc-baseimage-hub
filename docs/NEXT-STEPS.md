# Próxima etapa: encaixar a POC no processo atual

O marco técnico está em [Estado atual](STATUS.md). A próxima etapa é descobrir **onde a informação sobre digest, pacote e correção acrescenta valor à cadeia já existente**. Esta página é uma ordem de trabalho, não uma aprovação de ferramenta ou implantação.

| Ordem | Tarefa | Entrega verificável | Critério para avançar |
|---|---|---|---|
| 1 | Confirmar o processo atual com seus responsáveis: entrada upstream, matriz diária, ingestão/certificação, publicação e consumo. | Diagrama AS-IS validado e inventário do que CI e scanners já registram. | Local de cada gate e de cada evidência conhecido; dúvidas permanecem marcadas. |
| 2 | Definir a menor capacidade adicional: observar tag/plataforma/digest, relacionar pacote e advisory e registrar resultado. | Contrato de entrada, saída e erro, com responsável pelo estado e pelo recibo. | Um digest sem pacote/fix confiáveis resulta em `unknown`, sem aprovação. |
| 3 | Fechar a fronteira do proxy: o que vem da origem, o que pode vir do cache e qual digest efetivamente entra na certificação. | Regra de frescor e de aquisição por digest, com pontos de verificação dos bytes. | Não tratar a tag em cache como prova da tag atual da origem. |
| 4 | Preparar **uma** imagem piloto autorizada e seus resultados esperados. | Plano curto: imagem, plataforma, caso de correção, fontes, testes positivos/negativos e limite de atuação. | Critério de acerto e de parada definidos antes de rodar. |
| 5 | Repetir o caso no ambiente de destino, ligando o recibo ao gate que já existe. | Evidências para digest estável, mudança, fix ausente, fonte divergente e erro de acesso. | Nenhum caso incompleto aprova ou promove imagem; resultado e limitações revisáveis. |
| 6 | Só depois decidir o formato reutilizável: script na matriz atual, adaptador ou componente separado; e o papel eventual de Diun/Vunnel. | Decisão arquitetural baseada no processo real e na prova do piloto. | Explicar que função nova cada peça agrega e quem a opera. |
| 7 | Se o processo de desenvolvimento com BMAD for usado, levar **uma** história real delimitada pelo [contrato de workflow](WORKFLOWS.md). | História, testes, revisão, recibo e decisão final vinculados. | Não confundir o Loop sintético já concluído com validação do ciclo de domínio. |

As tarefas 1–3 definem o contrato; a tarefa 4 depende delas. A execução da tarefa 5 depende do piloto autorizado. A escolha de ferramenta (6) depende do resultado e **não exige** inventar uma operação contínua fora do escopo desta POC. O trabalho de workflow (7) é uma frente separada e pode ser planejado em paralelo sem mudar a decisão de arquitetura.

Para conferir as provas que já existem, siga o [runbook](RUNBOOK.md) e o [inventário de evidências](../poc/EVIDENCE.md). Para discutir o encaixe, comece por [Processo atual e proposta](ARCHITECTURE.md).
