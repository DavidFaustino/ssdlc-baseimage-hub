# Continuidade — Base Image Hub

## Objetivo e entrada

Organizar e preparar a execução no trabalho de um piloto Distroless dentro do processo existente, preservando o produto Hub e as provas anteriores. Comece por `docs/README.md` e `docs/piloto-distroless/ESPECIFICACAO.md`.

A única referência atual do processo é `docs/processo/ARQUITETURA.md`: base certificada → base derivada pela plataforma → imagem de aplicação. Use as fontes e divergências registradas; não peça ao responsável para reconstruir o processo de memória.

## Limites e continuidade

- Preservar GitHub Actions, registry/proxy, gates, scanners e evidências existentes. Não introduzir outra autoridade de aprovação.
- Piloto: adicionar Distroless em convivência com as bases atuais, com Quarkus e Angular. Receitas, integração e passagem completa até aplicação ainda precisam ser implementadas. Seguir especificação, plano e guia de execução; não declarar implementação por haver documentação.
- A POC anterior está em `poc/deteccao-e-correcao/`; documentação em `docs/poc-deteccao-e-correcao/`. A e B são alternativas de detecção. C avalia entradas históricas, não compete com A/B nem recebe automaticamente saídas novas. Vunnel é coleta de fonte. Os 44 casos completos não são reproduzíveis com o pacote publicado.
- A POC antiga é referência opcional; reproduzi-la integralmente não é pré-requisito do piloto.
- A UI é demonstrativa e não está integrada ao CI. Sua revisão arquitetural está congelada até decisão correspondente. Organização documental não autoriza mudanças funcionais.
- `docs/poc-deteccao-e-correcao/ARCHITECTURE.md` e `NEXT-STEPS.md` são registros históricos, não outra fonte normativa do processo/plano atual.
- Preservar scripts, fixtures e resultados; ajustar caminhos quando necessário e verificar testes e hashes após movimentação.
- Não publicar nomes de empresas, credenciais, caminhos privados ou material interno identificável. Fonte interna ausente no pacote deve ter sua limitação declarada.
- Atualizar a referência compartilhada e os links consumidores quando uma decisão mudar. Não duplicar o processo em cada frente; não criar instruções específicas para uma ferramenta de IA.
