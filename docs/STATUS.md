# Marco atual — Base Image Hub e workflows

**Revisão:** 10 de novembro de 2026. **Objetivo desta página:** permitir retomar o trabalho sem ler os experimentos em ordem cronológica.

## Resumo em uma frase

A POC local provou partes da identificação de digest, inspeção de pacote e correlação com patch para um caso Distroless Java 21/Debian 13. Ainda não existe um fluxo corporativo completo integrado nem um workflow SSDLC BMAD executado de ponta a ponta.

| Frente | Estado confirmado | O que falta |
|---|---|---|
| Processo de imagens base | A cadeia atual já possui execução diária em GitHub Actions, ingestão/certificação, imagens de arquitetura, publicação no ECR e consumo por aplicações em EKS. | Definir **onde** uma observação de patch/digest acrescenta informação e **qual evento** entra nos gates existentes. |
| Caso histórico | Dois digests da mesma variante e a versão de `libexpat1` antes/depois de uma correção Debian foram comprovados. | Não confundir esses digests com uma mudança observada hoje na tag pública. |
| Imagem pública | Uma captura do digest estável foi vinculada ao índice, manifesto filho, 34 camadas, pacote e um advisory selecionado. | Não houve mudança pública de tag nem certificação da imagem. |
| Comparação de entradas | Consulta direta OCI/Debian e Diun/Vunnel chegaram ao mesmo resultado nos casos principais; o validador comum preservou uma decisão e rejeitou entradas incoerentes. | A comparação **não** decide, por si só, se Diun/Vunnel agregam valor ao processo atual. |
| BMAD Method/CIS/TEA | Instalação e inventário de skills concluídos; há especificações de handoff, gates e arquivos de saída. | O workflow SSDLC completo continua um desenho; seus artefatos de negócio não foram produzidos por uma execução integral. |
| BMad Loop e modelo local | Uma história sintética chegou a `done` com recibo; controle local de estado e escopo teve testes. | A variante de revisão/contexto segue experimental; não há história real do domínio concluída pelo Loop com esse contrato. |
| Protótipo de painel deste repositório | Navegação com dados demonstrativos. | Não há backend nem integração com GitHub, JFrog, ECR ou scanners. |

## O que preservar

1. **Problema de produto:** reduzir o intervalo entre patch aplicável e imagem corporativa certificada, distinguindo descoberta, conteúdo do digest, decisão e certificação.
2. **Prova técnica reutilizável:** identificar imagem/tag/plataforma/digest, verificar bytes e versão do pacote, comparar com a versão corrigida, registrar `unknown` quando a evidência falta.
3. **Disciplina de execução:** entrada fixada, critérios de aceite, teste, recibo, revisão e estado de retomada. Isso vale mesmo que o executor de IA mude.

## O que não concluir deste marco

- Não há ferramenta nova aprovada. Menos requisições numa amostra local não bastam para escolher a arquitetura.
- Diun não elimina o resolvedor OCI por plataforma; Vunnel não substitui a regra de correlação.
- O BMad Loop sintético não demonstra que ele desenvolverá autonomamente toda a POC.
- O protótipo visual não representa integrações funcionais.

**Próxima conversa arquitetural:** mapear a informação nova sobre digest e patch contra a matrix diária e os gates existentes. [Veja o encaixe proposto](ARCHITECTURE.md).
