# Contexto de continuidade — Base Image Hub

## Objetivo atual confirmado pelo responsável

Permitir que o responsável baixe este repositório no computador de trabalho, entenda o que foi feito, reproduza os experimentos publicados e confira seus resultados. Depois dessa reprodução, identificar quais partes podem ser aproveitadas no processo de imagens base já documentado. A integração ao CI existente e à interface do Hub é uma etapa posterior.

Leia `docs/README.md` e `docs/STATUS.md` antes de propor trabalho. O processo existente está em `docs/ARCHITECTURE.md`; não peça ao responsável que o reconstrua de memória quando a documentação responder à questão.

## Escopo das provas existentes

- A demonstra detecção de mudança de imagem por consulta OCI em registry local controlado.
- B demonstra detecção com Diun e é alternativa de entrada a A, não requisito de adoção.
- A coleta Vunnel demonstra uma fonte de dados de correção Debian, sem inspecionar a imagem.
- C reproduz uma avaliação histórica de correção com entradas arquivadas, estado SQLite e recibos; não lê automaticamente as saídas novas de A, B ou Vunnel.
- As duas provas principais para explicar o pacote são detectar a mudança e reproduzir a avaliação histórica. Não apresentar A e C como opções concorrentes.
- A UI contém outro cenário demonstrativo e ainda não consome os resultados desses scripts.
- A comparação histórica integral de 44 casos não é reexecutável apenas com os arquivos publicados.

## Continuidade do trabalho

Preserve comandos, dados e resultados históricos. Diferencie sempre o que é executável, o que é registro histórico e o que ainda precisa ser desenvolvido. Não substitua o objetivo atual por nova comparação de ferramentas, redesenho do CI/CD, operação contínua ou desenvolvimento do Hub. Esses assuntos só avançam mediante instrução correspondente.

O responsável pediu uma explicação compreensível antes de aprovar a forma de um novo roteiro. Registrar este objetivo não autoriza criar um roteiro adicional, novos experimentos ou integrações. Use o runbook existente como referência dos comandos publicados e submeta alterações de abordagem ao responsável antes de executá-las.

Evite identificadores de organização, credenciais e caminhos privados no material público. Mantenha separados os fatos documentados e as hipóteses de adaptação ao ambiente de destino.
