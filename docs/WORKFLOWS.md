# Workflows, BMAD e servidor de IA

Este é um **trabalho de engenharia do processo de desenvolvimento**. Ele apoia o Base Image Hub, mas não deve ser confundido com a lógica que decide sobre imagens base.

## O fluxo pretendido

```mermaid
flowchart LR
  D[Discovery e fontes] --> S[Especificação e arquitetura]
  S --> G[Pacote revisado por pessoa]
  G --> I[Histórias delimitadas no Loop]
  I --> V[Testes e verificação]
  V --> R[Resultado consolidado e revisão]
```

A revisão humana foi prevista **no pacote antes do Loop** e **no resultado consolidado**, com intervenção intermediária quando uma decisão sair do escopo autorizado ou depender de acesso. O agente não deve declarar uma história concluída só porque seus testes locais passaram: estado, revisão, escopo e recibo precisam concordar.

## O que foi feito

| Parte | Evidência observada | Leitura correta |
|---|---|---|
| BMAD Method, CIS, TEA e BMad Loop | Ferramentas e skills instaladas e inventariadas localmente; foram mapeadas saídas declaradas e pontos interativos. | Instalação não é execução do workflow completo. |
| Desenho SSDLC | Há especificação, diagramas, handoffs, gates, estados e arquivos previstos. Revisores contestaram o desenho. | É uma proposta de orquestração, não runtime automatizado em produção. |
| Controle de estado | Fixture local testou bloqueio, retomada, eventos e escrita de evidência. | Prova do controle local, separada da lógica de imagens. |
| Modelo local | OpenCode no Mac chamou o modelo hospedado no servidor de IA em provas sintéticas. | O servidor executou inferência; isso não significa que o workflow do domínio foi concluído por ele. |
| BMad Loop | Uma história sintética chegou a `done` com revisão, testes e recibo formal em uma variante isolada. | Prova de caminho técnico. O perfil de revisão e o controle de contexto continuam experimentais. |
| Contexto e escopo | Checkpoint externo e gate Git foram testados; uma retomada sintética concluiu. | Uso/compreensão do checkpoint pelo modelo após compactação em execução real ainda não foi comprovado. |

## O que não foi feito

- O ciclo inteiro **Discovery → especificação → histórias → Loop → verificação → fechamento** não foi executado com uma história real de atualização de imagem base.
- O desenho de workflow não foi promovido como padrão reutilizável para outros produtos.
- A variante enxuta de revisão do Loop não foi homologada para histórias reais. A revisão de um caso correto, sozinha, não prova que ela encontra defeitos ou mudanças fora do escopo.
- Paperclip, Orca e Open WebUI foram estudados em experimentos anteriores; nenhum foi escolhido como coordenador desta POC.

## Regra para continuar

Antes de usar o Loop em trabalho de domínio, congelar uma história pequena com arquivos permitidos, saída exigida, testes e critério de parada. Provar a checagem independente de alterações e a retomada de contexto. Depois executar **uma** história real e comparar o resultado com a especificação, sem confundir um recibo sintético com maturidade do fluxo inteiro.

Os arquivos e versões de cada experimento estão listados em [Fontes e migração](SOURCES.md). Esta página é um mapa; os relatórios de prova continuam sendo a evidência técnica.
