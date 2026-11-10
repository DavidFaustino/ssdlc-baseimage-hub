# Reexecutar a POC local

Este roteiro é para conferir a **prova técnica principal** sem depender de uma IA. Ele usa manifestos históricos congelados e um banco SQLite local. A saída `validate_candidate` significa **pedir validação**; não certifica, publica ou promove imagens. Nenhum passo altera a tag pública ou acessa o ambiente corporativo.

## 1. Preparar

**Você precisa:** checkout deste repositório com a pasta `poc/`, Python 3 e permissão para criar um ambiente Python e um diretório temporário. Comece na **raiz do checkout**. Execute na cópia de trabalho, não em produção. Se a pasta `poc/` ou o arquivo `run_local.py` não estiver presente, esta versão ainda não está pronta para reprodução: **pare**. O pacote público usa uma derivação da fixture histórica na qual metadados de caminhos privados foram removidos e os hashes dependentes recalculados; ela não é byte a byte idêntica ao ledger privado arquivado.

```sh
cd poc
python3 --version
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
export PYTHONPATH=experiments/integrated-update-poc-20261108
```

**Esperado:** instalação sem erro. A instalação limpa em uma venv com as dependências fixadas foi verificada nesta migração. Se o arquivo de dependências não existir, houver falha de versão ou rede, **pare** e registre o erro; não instale dependências globalmente. Use o mesmo ambiente nas etapas seguintes.

Antes do teste, ainda na pasta `poc/`, confira os 55 arquivos de evidência publicados:

```sh
shasum -a 256 -c evidence/SHA256SUMS
```

**Esperado:** todos os arquivos exibem `OK`. **Pare** se algum hash divergir; não use evidência alterada para justificar uma conclusão.

## 2. Rodar os testes do núcleo

Na pasta `poc/`:

```sh
python3 -m unittest discover -s experiments/integrated-update-poc-20261108/tests -v
```

**Esperado neste pacote público:** 18 testes passando. Eles cobrem o núcleo de vínculo entre digest, plataforma, pacote, advisory, estado, recuperação e rejeição de entradas inconsistentes. A suíte local mais ampla tinha 30 testes, mas os insumos de `test_abc_c`, `test_feed` e `test_public_pipeline` não foram todos migrados; **não** declare esses 30 reproduzidos neste repositório. **Pare** se houver falha; um recibo positivo depois disso não é evidência suficiente. Guarde a saída do comando, a versão de Python e o commit usado.

## 3. Reproduzir a decisão principal

Escolha um diretório **novo e vazio**. O exemplo abaixo é local; mude o nome se já existir:

```sh
python3 experiments/integrated-update-poc-20261108/run_local.py --output /tmp/base-image-hub-replay-01
```

**Esperado:** a saída informa `PASS`, um baseline é registrado, o digest seguinte vira `validate_candidate`, a repetição não duplica a decisão, e o mesmo digest é reavaliado quando o advisory é consultado. Confira no diretório de saída `run.json`, `receipt.json`, `advisory-receipt.json` e `state.sqlite`. O recibo deve indicar `image_approved=false`. **Pare** se o programa aprovar ou promover imagem, se houver mais de uma decisão ou se os arquivos não forem produzidos.

## 4. Conferir a retomada sem repetir a decisão

Use **o mesmo diretório** da etapa anterior:

```sh
python3 experiments/integrated-update-poc-20261108/run_local.py --recover --output /tmp/base-image-hub-replay-01
```

**Esperado:** a saída informa recuperação dos recibos sem nova decisão. O modo `--recover` lê o SQLite e reexporta os JSONs após conferir a fixture. **Pare** se o estado arquivado divergir da entrada, se o banco não existir ou se o comando pedir para refazer a decisão. Não apague um recibo original para forçar um resultado.

## 5. Repetir a detecção direta (A)

Este script usa um registry de teste em `127.0.0.1` e os manifestos históricos incluídos. Ainda na pasta `poc/`, escolha um diretório novo:

```sh
python3 experiments/operational-abc-comparison-20261108/scripts/A/probe.py --output /tmp/base-image-a-01
```

**Esperado:** resumo com 36 execuções, três ciclos de baseline → mudança → repetição, um evento por ciclo e nenhum evento duplicado. Abra `/tmp/base-image-a-01/summary.json` e os registros de cada caso. **Pare** se o script tentar consultar um registry externo, se mudar os arquivos de entrada ou se uma falha produzir decisão positiva. Este caminho foi repetido com o pacote público.

## 6. Repetir o aviso real do Diun (B)

**Pré-requisito adicional:** binário Diun **4.33.1** obtido da [release oficial](https://github.com/crazy-max/diun/releases/tag/v4.33.1), com o checksum do arquivo escolhido conferido contra o arquivo oficial da release. Use o binário adequado ao seu sistema; ele não é distribuído neste repositório. No Mac ARM da prova, a versão 4.33.1 foi executada com os mesmos manifestos históricos em loopback. Exemplo para **macOS ARM**, fora da pasta do repositório:

```sh
mkdir -p /tmp/base-image-diun-4.33.1
curl -fL -o /tmp/base-image-diun-4.33.1/diun.tar.gz https://github.com/crazy-max/diun/releases/download/v4.33.1/diun_4.33.1_darwin_arm64.tar.gz
curl -fL -o /tmp/base-image-diun-4.33.1/checksums.txt https://github.com/crazy-max/diun/releases/download/v4.33.1/checksums.txt
rg -F 'diun_4.33.1_darwin_arm64.tar.gz' /tmp/base-image-diun-4.33.1/checksums.txt
printf '%s  %s\n' '9c78a81179801866ee704db9a3bd0b2454472f60ab8a224755dfe07f13ae979a' '/tmp/base-image-diun-4.33.1/diun.tar.gz' | shasum -a 256 -c -
tar -xzf /tmp/base-image-diun-4.33.1/diun.tar.gz -C /tmp/base-image-diun-4.33.1
```

**Esperado:** `OK` na conferência e o mesmo hash na lista oficial. Se não bater, **pare**; não execute o binário. Para Linux ou outra arquitetura, escolha o asset correspondente na release e compare seu hash com o arquivo oficial.

```sh
/tmp/base-image-diun-4.33.1/diun --version
DIUN_BIN=/tmp/base-image-diun-4.33.1/diun python3 experiments/operational-abc-comparison-20261108/scripts/B/run_retained_b.py --output-dir /tmp/base-image-b-01
```

**Esperado:** um aviso depois da troca e nenhum na repetição após reiniciar o processo. Abra `/tmp/base-image-b-01/results.json`, `receipt.json`, `notifications.jsonl` e os corpos servidos. **Pare** se a versão/checksum do binário não for a conferida, se o comando não usar loopback ou se houver aviso duplicado. Diun avisa; ele não certifica o manifesto filho nem a imagem.

## 7. Conferir a fonte de segurança e o comparativo arquivado

O [inventário de evidências](../poc/EVIDENCE.md) inclui o recorte congelado do feed e os recibos da comparação. Para **conferir o resumo arquivado**, abra `experiments/operational-abc-comparison-20261108/evidence/C/rows.json` e `cost-pairs.json`. Verifique cada linha parcial e seu motivo registrado. Isso permite auditar a classificação publicada, **não** recalcular os 44 resultados desde as entradas brutas: essas capturas completas não estão neste repositório.

O script `experiments/operational-abc-comparison-20261108/scripts/B/measure_vunnel.py` foi migrado e **a coleta ao vivo foi repetida** nesta publicação. Para executá-lo você precisa de `uv`, Python 3.13 disponível ao `uv`, rede para os feeds oficiais e espaço temporário suficiente para a base Debian completa. Ele fixa Vunnel 0.66.0 e escreve um recibo novo. Os hashes e tempos vão mudar com o feed; não use esse comando como igualdade bit a bit com o snapshot histórico. Se a rede, versão ou espaço faltarem, **pare** antes da coleta. O comando é:

Se faltar `uv`, siga a [instalação oficial](https://docs.astral.sh/uv/getting-started/installation/). Confira a ferramenta e prepare o Python 3.13 com a [gestão oficial de versões](https://docs.astral.sh/uv/guides/install-python/):

```sh
uv --version
uv python install 3.13
```

Depois execute:

```sh
python3 experiments/operational-abc-comparison-20261108/scripts/B/measure_vunnel.py --output /tmp/base-image-vunnel-01
```

**Esperado:** `receipt.json`, log e workspace de dados em `/tmp/base-image-vunnel-01`. Verifique no recibo o status da coleta, hash do feed Debian, versão corrigida selecionada e recursos consumidos. Uma nova coleta pode ter dados diferentes; investigue a diferença em vez de exigir os hashes da rodada anterior.

**Interpretação:** A e B observaram a mesma troca histórica. O núcleo e os avisos reproduzidos aqui não representam a comparação integral de 44 casos nem uma decisão de adotar Diun ou Vunnel no processo atual.

## 8. Guardar um recibo de reprodução

Anote: commit deste repositório, sistema e versão de Python, comando, saída, diretório de recibos, hashes de entradas e conclusão. Se a fonte pública mudar depois, não ajuste a fixture congelada para ela “passar”; faça uma nova captura com outro identificador. [O marco](STATUS.md) e [o encaixe arquitetural](ARCHITECTURE.md) explicam o alcance da prova antes de qualquer uso no processo real.
