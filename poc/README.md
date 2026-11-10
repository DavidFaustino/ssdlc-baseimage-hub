# Scripts e evidências da POC

Este diretório contém scripts e capturas selecionados da prova local. Para executar, comece pelo [runbook](../docs/RUNBOOK.md). Para saber exatamente quais arquivos foram incluídos, consulte o [inventário de evidências](EVIDENCE.md).

O uso imediato deste pacote é **reproduzir e conferir os ensaios publicados em outro computador**. Comece pela decisão/recuperação **C** sobre entradas arquivadas e pela detecção direta **A** em registry local. **B** e **Vunnel** continuam disponíveis como ensaios de outra entrada e da fonte de correção; executar esses cenários não significa adotar as ferramentas. C consome evidências para decidir, não compete com A/B como observador. A ligação entre saídas recém-geradas e C e o encaixe no CI/Hub pertencem a uma avaliação posterior.

## O que pode ser repetido daqui

- **Correlação local arquivada:** usa observações OCI históricas já capturadas para verificar pacote e correção, persistir o estado em SQLite e emitir recibos. O replay não consulta uma tag pública nem aprova imagem.
- **Detecção direta A:** script real sobre registry em loopback, usando os manifestos históricos.
- **Detecção Diun B:** script real sobre o mesmo registry em loopback; requer binário Diun instalado à parte.
- **Coleta Vunnel:** script real que obtém o feed Debian público atual; requer `uv`, Python 3.13 e acesso à rede. Os dados e hashes podem mudar com a data.

Os scripts de A, B e Vunnel geram saídas novas fora deste repositório. As capturas locais preservadas em `experiments/` sustentam o replay da correlação. Um ledger teve caminhos locais removidos e seus hashes de vínculo foram recalculados; por isso esta é uma fixture pública derivada, não cópia byte a byte daquele ledger privado.

Para demonstrar **recuperação** de C, o runbook copia a saída do primeiro replay, trunca um recibo somente nessa cópia e reexporta os JSON a partir do SQLite confirmado. Isso é diferente de executar `--recover` sobre arquivos ainda íntegros.

## O que não pode ser repetido daqui

Este pacote não contém as capturas completas da comparação operacional de 44 casos nem o dump completo de camadas da leitura pública. Portanto, ele **não** reproduz aquela matriz inteira só com um comando. Para reconstruí-la, é preciso coletar ou importar essas evidências, verificar seus hashes e revisar a portabilidade dos scripts restantes antes de declarar a mesma contagem.
