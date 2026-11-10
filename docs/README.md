# Comece aqui

Este repositório tem **duas partes diferentes**:

| Parte | O que é | Onde está |
|---|---|---|
| Protótipo visual | Uma página com dados demonstrativos. Ela não consulta registries nem toma decisões. | [`index.html`](../index.html) |
| Pesquisa e POC | Documentos, scripts, testes e algumas evidências de uma solução para acompanhar correções em imagens base. | [Estado e arquitetura](STATUS.md) e [scripts da POC](../poc/README.md) |

## Para entender o trabalho

Leia nesta ordem:

1. [Estado atual](STATUS.md): o que foi feito, o que continua aberto e o que **não** foi aprovado.
2. [Processo atual e encaixe](ARCHITECTURE.md): onde a nova informação entraria na cadeia que já existe.
3. [Resultados da POC](POC.md): o que os testes demonstraram e seus limites.
4. [Próxima etapa](NEXT-STEPS.md): decisões e provas necessárias para continuar.

Para confrontar a documentação e a interface com o processo completo, leia a [revisão BMAD do Hub](reviews/README.md), com pareceres independentes de documentação, UX e arquitetura.

Se quiser conferir cada afirmação, use o [checklist de revisão](EXECUCAO.md) e a [lista das fontes](SOURCES.md).

## Para executar

Siga o [runbook](RUNBOOK.md). Ele traz pré-requisitos, comandos, saídas esperadas e quando parar. Os [scripts e arquivos incluídos](../poc/README.md) permitem repetir o núcleo da decisão, sua retomada, a detecção direta, o aviso do Diun e uma nova coleta do Vunnel. O [inventário de evidências](../poc/EVIDENCE.md) mostra os arquivos presentes.

**Limite:** a comparação arquivada de 44 casos e a inspeção integral da imagem pública **não podem ser refeitas apenas com este repositório**. As capturas brutas dessas provas ainda estão no acervo local. O runbook diz exatamente o que já é executável.

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
