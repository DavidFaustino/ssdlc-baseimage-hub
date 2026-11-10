# Reexecutar a POC de atualização de imagem base

Este guia explica **o que cada teste faz, como executá-lo e como ler o resultado**. Nenhum passo altera uma tag pública, certifica imagem ou acessa o ambiente corporativo. Execute numa cópia do repositório e grave as saídas em diretórios novos fora dela.

## Primeiro, entenda o percurso

**Pergunta da POC:** quando uma correção fica disponível, conseguimos identificar o conteúdo exato da imagem, verificar o pacote afetado, decidir se há candidata para validação e retomar o trabalho sem repetir a decisão?

O caso congelado usa uma imagem Distroless Java 21 sobre Debian 13. Há dois manifestos históricos da mesma variante, com o pacote `libexpat1` antes e depois da correção. **Tag** é o nome mutável da imagem; **digest** identifica o conteúdo recebido; **advisory** é o comunicado da correção.

Na prática, o teste faz quatro coisas: serve a mesma tag localmente apontando primeiro para o conteúdo antigo e depois para o novo; verifica se A ou B percebe a troca; cruza a versão do pacote com a correção no passo C; e repete a leitura para confirmar que nenhuma decisão duplicada foi gravada. A fonte Debian ou o Vunnel informa a correção; nenhum dos dois inspeciona a imagem por conta própria.

| Peça | Função | Prova que você pode repetir aqui |
|---|---|---|
| **A — consulta direta** | Nosso script consulta a tag e compara os digests. | Troca e repetição num registry local. |
| **B — Diun** | A ferramenta consulta a tag, guarda o estado e emite aviso de mudança. | Mesmo caso local, usando o binário oficial. |
| **Fonte Debian / Vunnel** | Fornece a versão corrigida do pacote. | Uma coleta nova pelo Vunnel; o feed pode ter mudado. |
| **C — correlação** | Vincula digest, plataforma, pacote e correção; registra decisão em SQLite. | Replay da decisão com entradas históricas congeladas. |

**Limite da ligação:** os comandos A, B e Vunnel abaixo são execuções separadas. O replay C usa entradas arquivadas. Os recibos originais mostram A e B chegando à mesma decisão no laboratório; estes comandos **não** repetem automaticamente a comparação operacional inteira de 44 casos.

## 1. Preparar o ambiente

**Por quê:** instalar dependências sem modificar o Python global. **Entrada:** checkout deste repositório, Python 3, acesso aos pacotes Python e espaço para saídas temporárias.

Comece na raiz do checkout:

```sh
cd poc
python3 --version
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
export PYTHONPATH=experiments/integrated-update-poc-20261108
```

**Esperado:** instalação sem erro. A venv fica dentro de `poc/` e é ignorada pelo Git. **Pare se:** faltar o arquivo de dependências, houver erro de instalação ou não puder criar a venv. Os testes do núcleo foram repetidos com uma instalação limpa das versões fixadas.

## 2. Conferir as entradas

**Por quê:** um manifesto ou recibo modificado não deve sustentar uma conclusão. **Entrada:** 55 arquivos selecionados listados em `poc/evidence/SHA256SUMS`. Ainda dentro de `poc/`, execute no macOS:

```sh
shasum -a 256 -c evidence/SHA256SUMS
```

No Linux, use `sha256sum -c evidence/SHA256SUMS`. **Esperado:** todos os arquivos mostram `OK`. Alguns caminhos privados foram removidos dos metadados e os hashes dependentes foram recalculados; o manifesto identifica os bytes **desta cópia pública**, conforme o [inventário](../poc/EVIDENCE.md). **Pare se:** qualquer hash falhar.

## 3. Testar as regras de correlação (C)

**Por quê:** verificar casos válidos e entradas incoerentes antes do replay. **Entradas:** manifestos, versões de pacote, advisory e contrato congelados em `poc/experiments/`.

```sh
python3 -m unittest discover -s experiments/integrated-update-poc-20261108/tests -v
```

**Esperado:** `Ran 18 tests` e `OK`. A suíte testa vínculos entre digest, plataforma, pacote e correção, além de estado e recuperação. **Pare se:** algum teste falhar. Os 18 testes incluídos não equivalem aos 30 da suíte local mais ampla nem aos 44 casos comparativos.

## 4. Gerar uma decisão e seu recibo (C)

**Por quê:** atravessar o caso histórico com estado persistido. **Entradas:** os dados congelados verificados no passo 2 e um diretório de saída novo. O comando não baixa nem publica imagens.

```sh
python3 experiments/integrated-update-poc-20261108/run_local.py --output /tmp/base-image-hub-replay-01
```

**Esperado:** `PASS baseline→validate_candidate→unchanged; stable digest reassessed; no approval`. Abra `run.json`, `receipt.json`, `advisory-receipt.json` e `state.sqlite` no diretório de saída. `run.json` deve indicar **uma decisão**, **uma reavaliação** e `image_approved: false`. A ação `validate_candidate` significa **encaminhar para validação**, sem aprovar a imagem. **Pare se:** o diretório já contiver arquivos, faltar recibo, houver decisão duplicada ou surgir aprovação automática.

**Exemplo de recibo real:** em `poc/experiments/operational-abc-comparison-20261108/evidence/C/pipeline-replay.json`, tanto A quanto B têm `baseline.status = baseline`, `decision_count = 1`, `decision_receipt.action = validate_candidate` e `decision_receipt.image_approved = false`. Esse é o registro histórico selecionado; o comando acima gera **outro recibo**, que você deve conferir por conta própria.

## 5. Retomar sem decidir de novo (C)

**Por quê:** verificar que a decisão gravada sobrevive à reabertura. **Entrada:** o **mesmo** diretório do passo 4; não o apague.

```sh
python3 experiments/integrated-update-poc-20261108/run_local.py --recover --output /tmp/base-image-hub-replay-01
```

**Esperado:** `PASS recovered receipts from committed state; no new decision`. O programa lê o SQLite e recompõe os JSONs sem recalcular a decisão. **Pare se:** o banco faltar, a entrada não corresponder ao estado ou o comando pedir nova decisão.

## 6. Detectar a mudança por consulta direta (A)

**Por quê:** mostrar que um script pode detectar mudança sem Diun. **Entradas:** os mesmos manifestos históricos; o script os serve num registry local em `127.0.0.1`, sem consultar a tag pública.

```sh
python3 experiments/operational-abc-comparison-20261108/scripts/A/probe.py --output /tmp/base-image-a-01
```

**Esperado:** o terminal informa `runs: 36` e `cycles: 3`. Abra `/tmp/base-image-a-01/summary.json`: em cada ciclo principal, a primeira consulta cria o ponto de partida, a troca cria **um evento**, e a repetição não cria outro. Outros casos exercitam falhas, plataforma e retomada. **Pare se:** a saída já existir, houver evento positivo após falha ou o script tentar acessar registry externo. Esta etapa passou com o pacote público.

## 7. Detectar a mesma mudança com Diun (B)

**Por quê:** ver o que a ferramenta entrega além da consulta direta: estado e aviso. **Entradas:** os manifestos históricos, binário Diun oficial e diretório novo. O script usa somente `127.0.0.1`.

No Mac ARM, usamos Diun **4.33.1**. Baixe o arquivo da [release oficial](https://github.com/crazy-max/diun/releases/tag/v4.33.1), confira seu hash **antes de executar** e extraia fora do repositório:

```sh
mkdir -p /tmp/base-image-diun-4.33.1
curl -fL -o /tmp/base-image-diun-4.33.1/diun.tar.gz https://github.com/crazy-max/diun/releases/download/v4.33.1/diun_4.33.1_darwin_arm64.tar.gz
curl -fL -o /tmp/base-image-diun-4.33.1/checksums.txt https://github.com/crazy-max/diun/releases/download/v4.33.1/checksums.txt
grep -F 'diun_4.33.1_darwin_arm64.tar.gz' /tmp/base-image-diun-4.33.1/checksums.txt
printf '%s  %s\n' '9c78a81179801866ee704db9a3bd0b2454472f60ab8a224755dfe07f13ae979a' '/tmp/base-image-diun-4.33.1/diun.tar.gz' | shasum -a 256 -c -
tar -xzf /tmp/base-image-diun-4.33.1/diun.tar.gz -C /tmp/base-image-diun-4.33.1
```

**Esperado:** `OK` e o mesmo hash no arquivo oficial. **Pare se:** o hash divergir. Para Linux ou outra arquitetura, escolha o arquivo correspondente na release e confira o checksum específico dele.

Com o binário conferido, volte à pasta `poc/` e execute:

```sh
/tmp/base-image-diun-4.33.1/diun --version
DIUN_BIN=/tmp/base-image-diun-4.33.1/diun python3 experiments/operational-abc-comparison-20261108/scripts/B/run_retained_b.py --output-dir /tmp/base-image-b-01
```

**Esperado:** `notifications: 1`. Abra `/tmp/base-image-b-01/results.json`: os três passos têm avisos novos `[0, 1, 0]` — nenhum na primeira leitura, um na troca e nenhum na repetição após reiniciar. `receipt.json` liga aviso e manifestos servidos; `notifications.jsonl` guarda o aviso. **Pare se:** houver aviso duplicado, binário não conferido ou acesso fora do registry local. Diun **avisa**; a validação da plataforma e do pacote continua nossa.

## 8. Consultar o feed atual com Vunnel

**Por quê:** coletar dados processados de correções Debian. **Entradas:** feed **atual**, rede, espaço temporário, `uv` e Python 3.13. Isto **não** repete a revisão congelada do caso histórico; conteúdo e hashes podem mudar.

Se faltar `uv`, siga a [instalação oficial](https://docs.astral.sh/uv/getting-started/installation/). Depois, ainda em `poc/`:

```sh
uv --version
uv python install 3.13
python3 experiments/operational-abc-comparison-20261108/scripts/B/measure_vunnel.py --output /tmp/base-image-vunnel-01
```

**Esperado:** `receipt.json`, `vunnel.log` e um workspace de dados no diretório indicado. Em `receipt.json`, confira `exit_code: 0`, os hashes das entradas Debian, `lookup[].fixed_source_version` e métricas de tempo e tamanho. **Pare se:** rede, instalação ou coleta falhar; consulte `vunnel.log` e não use recibo incompleto. Se o feed diferir do snapshot antigo, registre a nova revisão em vez de mudar a fixture. O script fixa Vunnel 0.66.0. [Como `uv` gerencia Python](https://docs.astral.sh/uv/guides/install-python/).

## 9. Ler a comparação histórica de 44 casos

O arquivo `poc/experiments/operational-abc-comparison-20261108/evidence/C/rows.json` contém o resultado **arquivado**: 6 casos completos, 38 parciais, nenhum falho e nenhum bloqueado. `cost-pairs.json` guarda medições selecionadas. “Parcial” significa que aquela linha não percorreu todas as mesmas etapas nos dois caminhos; o motivo está na própria linha.

**Você consegue:** conferir as linhas e recibos selecionados e repetir os passos 3 a 8. **Ainda não consegue:** recalcular os 44 casos a partir de todas as entradas brutas. O acervo original tem cerca de 211 MB de capturas não publicadas, além de scripts com caminhos locais. A inspeção integral dos 34 blobs da imagem pública também não está no pacote. [Inventário dos limites](../poc/EVIDENCE.md).

## Registrar sua conferência

Guarde o commit usado, sistema e versão de Python, comandos, diretórios de saída, hashes, testes e recibos. Se o feed ou a tag pública mudarem, faça uma **nova** captura; não altere a fixture histórica. Para decidir onde a capacidade caberia no processo existente, leia a [arquitetura](ARCHITECTURE.md). Esta POC não aprova ferramenta nem implantação.
