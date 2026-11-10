# Comece aqui

Este repositório reúne o protótipo do Hub e o material técnico da pesquisa e POC. **Agora, a tarefa é reproduzir e conferir os experimentos publicados nesta cópia; depois, avaliar o reaproveitamento no processo AS-IS documentado.** Integração corporativa e implementação operacional do Hub ficam para uma etapa posterior.

| Parte | O que é | Onde está |
|---|---|---|
| Protótipo visual | Hub operacional demonstrativo. Visão geral, Imagens, Automações e Adoção usam os mesmos três runs fictícios para ilustrar bloqueio, evidência, digest, gate, publicação e ausência de consumo confirmado. O Roadmap separa descoberta, validação e evolução proposta. Pedidos feitos na interface ficam apenas no navegador; não consultam sistemas nem tomam decisões reais. | [`index.html`](../index.html) |
| Visualização independente da POC | Artefato HTML para consulta ou compartilhamento separado; não é uma rota da interface do Hub nem altera seus estados. | [`poc/overview.html`](../poc/overview.html) |
| Pesquisa e POC | Documentos, scripts, testes e algumas evidências de uma solução para acompanhar correções em imagens base. | [Estado e arquitetura](STATUS.md) e [scripts da POC](../poc/README.md) |

## Ordem para conferir esta entrega

Leia nesta ordem:

1. [Estado atual](STATUS.md) e [inventário de evidências](../poc/EVIDENCE.md): o que está de fato publicado e o que não pode ser refeito com esta cópia.
2. [Runbook](RUNBOOK.md): entender entradas, processamento e saídas; repetir os cenários que já têm scripts e dados aqui.
3. [Checklist de conferência](EXECUCAO.md) e [Resultados da POC](POC.md): comparar sua execução com as afirmações registradas.
4. [Processo atual e encaixe](ARCHITECTURE.md): depois da conferência, identificar o que se aproveita no AS-IS.
5. [Próxima etapa](NEXT-STEPS.md): separar a reprodução imediata da integração e da evolução do produto.

Para localizar as fontes e distinguir arquivos publicados do acervo original, use a [lista das fontes](SOURCES.md).

## Para executar

Siga o [runbook](RUNBOOK.md). Ele traz pré-requisitos, comandos, saídas esperadas e quando parar. Os [scripts e arquivos incluídos](../poc/README.md) permitem repetir duas provas principais: **A** detecta a mudança por OCI direto; **C** correlaciona dados históricos arquivados e registra a decisão. **B** repete a detecção com Diun como alternativa a A; **V** coleta dados do feed com Vunnel. C não é uma opção concorrente de detecção nem consome automaticamente as novas saídas de A, B e V. O [inventário de evidências](../poc/EVIDENCE.md) mostra os arquivos presentes.

**Limite:** a comparação arquivada de 44 casos e a inspeção integral da imagem pública **não podem ser refeitas apenas com este repositório**. As capturas brutas dessas provas ainda estão no acervo local. O runbook diz exatamente o que já é executável.

As provas sintéticas do BMAD/Loop estão resumidas em [Workflows](WORKFLOWS.md), mas seus comandos e recibos não foram publicados aqui. Não há roteiro de reexecução dessa frente neste PR.

## Outros trabalhos relacionados

[Workflows e BMAD](WORKFLOWS.md) registra o desenho do processo de desenvolvimento e os testes sintéticos do Loop. Essa frente não é o motor que avalia imagens base.

## Termos usados aqui

| Termo | Significado |
|---|---|
| Tag | Nome que aponta para uma imagem e pode mudar, como `latest`. |
| Digest | Identificador do conteúdo de uma imagem. |
| OCI | Padrão usado para consultar imagens em um registry. |
| Manifesto da plataforma | Arquivo que aponta para o conteúdo de uma variante, como Linux em x86-64. |
| Advisory | Comunicado de segurança com informações sobre uma falha e sua correção. |
| Recibo | Registro da entrada e do resultado de um teste ou decisão. |

**Estado desta documentação:** rascunho para revisão. Ela não aprova ferramenta, arquitetura nem implantação.
