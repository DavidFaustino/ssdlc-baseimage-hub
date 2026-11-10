# Pacote executável da POC

Este diretório preserva os scripts originais da prova local, com somente ajustes de caminhos para execução fora do Mac de origem. Comece pelo [runbook](../docs/RUNBOOK.md), que separa pré-requisitos, comandos, saídas esperadas e critérios de parada.

## O que é reproduzível daqui

- **Correlação local arquivada:** consulta OCI sobre manifestos históricos, verificação de pacote e fix, estado SQLite e recibos. O teste e o replay não aprovam imagem.
- **Detecção direta A:** script real sobre registry em loopback, usando os manifestos históricos.
- **Detecção Diun B:** script real sobre o mesmo registry em loopback; requer binário Diun instalado à parte.
- **Coleta Vunnel:** script real que obtém o feed Debian público atual; requer `uv`, Python 3.13 e acesso à rede. Os dados e hashes podem mudar com a data.

Os scripts de A, B e Vunnel geram saídas novas fora deste repositório. As capturas locais preservadas em `experiments/` sustentam o replay da correlação. Um ledger teve caminhos locais removidos e seus hashes de vínculo foram recalculados; por isso esta é uma fixture pública derivada, não cópia byte a byte daquele ledger privado.

## Limite honesto

Este pacote não contém as capturas completas da comparação operacional de 44 casos nem o dump completo de camadas da leitura pública. Portanto, ele **não** reproduz aquela matriz inteira só com um comando. Para reconstruí-la, é preciso coletar ou importar essas evidências, verificar seus hashes e revisar a portabilidade dos scripts restantes antes de declarar a mesma contagem.
