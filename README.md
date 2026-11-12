# Base Image Hub

Este repositório reúne o produto Hub e o trabalho sobre o ciclo das imagens base. A referência compartilhada é o [processo de imagens base](docs/processo/ARQUITETURA.md): **base certificada → base derivada pela plataforma → imagem de aplicação**.

## Comece pelo que você precisa fazer

| Objetivo | Ponto de entrada | Situação |
|---|---|---|
| Preparar o piloto Distroless no trabalho | [Especificação do piloto](docs/piloto-distroless/ESPECIFICACAO.md) | Define o incremento ao processo, entregas, tarefas e aceite. Receitas e integração ainda precisam ser implementadas. |
| Entender o processo existente | [Arquitetura compartilhada](docs/processo/ARQUITETURA.md) | Síntese das fontes e do relato, com divergências explicitadas; não é auditoria dos workflows. |
| Reproduzir a POC anterior | [Runbook da POC](docs/poc-deteccao-e-correcao/RUNBOOK.md) | Provas separadas de detecção e avaliação histórica. Não é o piloto Distroless completo. |
| Entender ou integrar futuramente o Hub | [Especificação do produto e da interface](docs/hub/ESPECIFICACAO.md) | Interface navegável demonstrativa, sem backend ou conexão com o CI. |

**O piloto acrescenta Distroless ao circuito existente**, preservando GitHub Actions e controles. Usa duas aplicações existentes, Quarkus e Angular, para avaliar construção, correção por camada, propagação e funcionamento. Reproduzir toda a POC anterior não é pré-requisito para esse trabalho.

O [índice da documentação](docs/README.md) liga processo, piloto, produto e experimentos sem definir cópias concorrentes da arquitetura. O código da POC está em [poc/deteccao-e-correcao](poc/deteccao-e-correcao/README.md); dados e scripts foram preservados na reorganização.

## Abrir o protótipo

Abra [index.html](index.html) no navegador. Para servir a raiz localmente:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

A interface usa dados e pedidos DEMO; não executa workflows, aprova imagens nem consulta registries/scanners. [Prévia visual](preview.png). As correções propostas para sua tela Arquitetura estão [documentadas para revisão](docs/hub/REVISAO-ARQUITETURA.md); a reorganização documental não alterou a UI.

## Limites da entrega

- O piloto tem especificação e plano; não há comando único nem pacote novo pronto para executá-lo.
- A POC antiga permite repetir A (OCI direto), B (Diun), coleta Vunnel e C (avaliação histórica), separadamente. C não consome automaticamente saídas novas de A/B/Vunnel.
- Os 44 casos históricos não podem ser integralmente recalculados com as capturas publicadas. Consulte o [inventário de evidências](poc/deteccao-e-correcao/EVIDENCE.md).
- Aprovar a organização deste repositório não equivale a aprovar implantação ou alterações nos controles corporativos.
