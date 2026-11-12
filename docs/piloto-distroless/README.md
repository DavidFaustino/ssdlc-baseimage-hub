# Piloto Distroless no processo existente

**Estado: especificação em revisão. O novo piloto ainda não é executável.** Esta pasta define o que será construído e os dados necessários para começar. Ainda não contém receitas, scripts ou workflows novos prontos para rodar.

O objetivo é abrir uma **trilha adicional de imagens mínimas/Distroless**, convivendo com as bases atuais, e demonstrar uma atualização de segurança até duas aplicações existentes: um backend Quarkus e um frontend Angular. GitHub Actions, JFrog, ECR, scanners, aprovações e mecanismos de evidência existentes continuam no processo.

O piloto precisa responder: **quando há uma correção aplicável no SO, runtime ou dependência, qual artefato muda, quais bases/aplicações precisam ser reconstruídas e como comprovar que passaram a usar o conteúdo corrigido?** O digest identifica cada artefato e conecta essas etapas.

## Por onde começar no trabalho

1. [Especificação](ESPECIFICACAO.md): entender objetivo, processo reaproveitado, delta Distroless e critérios de aceite.
2. [Preparação e execução](EXECUCAO.md): reunir as amostras do trabalho e acompanhar a sequência; comandos operacionais ainda serão implementados.
3. [Plano de tarefas](PLANO.md): conferir histórias, entregas e condições para avançar.

Nesta etapa, a ação é levantar os insumos e revisar o recorte. Os comandos operacionais serão escritos e validados quando receitas, aplicações e pontos de integração estiverem definidos; não há um comando deste piloto para executar hoje.

## O que já temos e o que falta

| Já disponível | Ainda precisa ser implementado ou confirmado |
|---|---|
| Processo informado de base certificada → base derivada pela plataforma → aplicação. | Variantes Distroless e receitas compatíveis com as aplicações escolhidas. |
| [POC anterior de detecção e correção](../poc-deteccao-e-correcao/README.md), com provas locais de digest, pacote/advisory e retomada. | Encadeamento real de atualização, builds, gates e publicação nos workflows existentes. |
| Protótipo visual do Hub e artefatos de segurança informados como existentes. | Duas aplicações executadas em validação efêmera, antes/depois da correção, com linhagem e evidências dos digests finais. |

A POC anterior é referência técnica, não o roteiro deste piloto. Diun/Vunnel e as alternativas A/B não foram adotados para esta nova trilha. A interface permanece fora da implementação desta etapa.

**Resultado esperado do piloto:** um percurso reproduzível de construção, correção e verificação das três camadas, com limites e falhas documentados. Isso não equivale a migrar o catálogo inteiro, garantir ausência de CVEs ou autorizar implantação produtiva.
