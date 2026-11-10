# Checklist para revisar a entrega

Este checklist ajuda a conferir as conclusões. Os **comandos de execução** estão apenas no [runbook](RUNBOOK.md), para que haja um único roteiro técnico.

1. **Entenda o estado.** Abra [Estado atual](STATUS.md). Separe o que foi observado no processo existente, testado na POC, proposto e ainda pendente. Nenhum item deve sugerir que uma imagem foi certificada ou uma ferramenta foi adotada.
2. **Confira o encaixe.** Leia [Processo atual e encaixe](ARCHITECTURE.md). A capacidade de relacionar digest, pacote e correção aparece como proposta; a reconstrução e os gates existentes continuam sendo parte do processo atual.
3. **Confira as provas.** Em [Resultados da POC](POC.md), distinga o caso histórico, a leitura pontual da imagem pública e os testes locais A/B. Use o [inventário de evidências](../poc/EVIDENCE.md) para saber quais arquivos estão neste repositório.
4. **Repita o que está incluído.** Execute o [runbook](RUNBOOK.md) na ordem indicada e guarde as saídas. Pare se um hash ou teste falhar. O runbook não refaz integralmente os 44 casos arquivados.
5. **Verifique a recuperação de verdade.** No cenário C2, use a cópia descartável com um recibo truncado; confirme que o SQLite não muda e que o JSON é reexportado. Repetir `--recover` sobre os arquivos intactos de C1, sozinho, não demonstra recuperação.
6. **Registre a revisão.** Para qualquer correção, anote a página, a afirmação e a evidência correspondente. Uma proposta só vira resultado comprovado quando há entrada, execução, saída e recibo verificáveis. Resultados BMAD/Loop permanecem históricos nesta cópia, pois suas provas de reexecução não estão publicadas.

Os documentos do acervo original estão relacionados em [Fontes](SOURCES.md). Se você tiver acesso a eles, pode auditar a comparação integral pelo runbook original; **esses comandos e arquivos não estão todos no repositório público**.
