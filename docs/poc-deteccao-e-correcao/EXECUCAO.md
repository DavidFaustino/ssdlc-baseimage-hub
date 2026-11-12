# Checklist para reproduzir e conferir a entrega

> **Conferência da POC existente.** Este checklist serve a quem optar por reproduzir as provas históricas publicadas; não é pré-requisito para o novo piloto Distroless.

Use este checklist depois de baixar a cópia no computador de trabalho. O objetivo imediato é entender e repetir **o que está publicado**, registrar concordâncias e diferenças e aceitar ou questionar os resultados. Só depois se avalia encaixe no processo AS-IS. Os **comandos de execução** estão apenas no [runbook](RUNBOOK.md), para que haja um único roteiro técnico.

1. **Confira o pacote.** Abra [Estado atual](STATUS.md) e o [inventário de evidências](../../poc/deteccao-e-correcao/EVIDENCE.md). Distinga scripts e entradas publicados, recibos históricos e arquivos que ficaram fora desta cópia. Nenhum item deve sugerir certificação ou adoção de ferramenta.
2. **Entenda as duas provas principais.** No [runbook](RUNBOOK.md), identifique o que entra, o que o script faz e o que sai em **A** (detecção OCI) e **C** (correlação das entradas históricas arquivadas). **B** testa Diun como alternativa de detecção e **V** coleta feed com Vunnel; ambos são opcionais para entender as ferramentas e não alimentam C automaticamente.
3. **Repita o que está incluído.** Execute os comandos existentes do runbook e guarde saídas, versões e hashes. Pare se um hash ou teste falhar. O pacote não refaz integralmente os 44 casos arquivados nem a inspeção de todos os blobs públicos.
4. **Verifique a recuperação de verdade.** No cenário C2, use a cópia descartável com um recibo truncado; confirme que o SQLite não muda e que o JSON é reexportado. Repetir `--recover` sobre os arquivos intactos de C1, sozinho, não demonstra recuperação.
5. **Confronte as conclusões.** Compare entradas, saídas e recibos da sua execução com [Resultados da POC](POC.md). Para qualquer diferença ou correção, anote cenário, comando, versão, página, afirmação e evidência. Uma proposta só vira resultado comprovado quando há entrada, execução, saída e recibo verificáveis. Resultados BMAD/Loop permanecem históricos nesta cópia, pois suas provas de reexecução não estão publicadas.
6. **Depois avalie o encaixe.** Leia [Processo atual e encaixe](ARCHITECTURE.md) e marque quais resultados reproduzidos acrescentam informação aos gates que já existem. Não trate esta conferência como aprovação de integração, imagem ou ferramenta.

Os documentos do acervo original estão relacionados em [Fontes](SOURCES.md). Se você tiver acesso a eles, pode auditar a comparação integral pelo runbook original; **esses comandos e arquivos não estão todos no repositório público**.
