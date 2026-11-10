# Evidências incluídas no pacote público

Este diretório contém **capturas selecionadas** da POC local; alguns metadados de caminhos foram sanitizados para publicação. Não contém a cópia integral do laboratório. Para conferir os bytes publicados antes de interpretar os resultados, execute a partir de `poc/`:

```sh
shasum -a 256 -c evidence/SHA256SUMS
```

## O que está aqui

| Conjunto | Conteúdo | O que permite conferir |
|---|---|---|
| Caso histórico | Manifestos, configurações, camadas do pacote, status do `libexpat1` antes/depois e seleção dos digests. | Que os dois digests históricos da mesma variante continham versões diferentes do pacote. |
| Replay OCI local | Índices, manifestos filhos, observações, eventos e requisições do registry controlado. | Que a troca de digest gerou um evento e a repetição não gerou outro. |
| Contrato e entradas de correlação | Schema, entradas do caso, prova de suite e manifesto de fontes. | Que a decisão foi baseada em fontes vinculadas por hash, plataforma, pacote e advisory. |
| Resumo A/B/C | Linhas classificadas da comparação, pares de custo, recibo de replay e recibo da leitura pública arquivada. | O resultado publicado da comparação; **não** é suficiente para refazer todos os 44 casos a partir do zero. |

## O que pode ser executado agora

O [runbook](../docs/RUNBOOK.md) reproduz o núcleo de correlação com estado e recuperação usando a fixture pública deste pacote. Os scripts originais adaptados em `experiments/operational-abc-comparison-20261108/scripts/A/probe.py` e `scripts/B/run_retained_b.py` também permitem **nova execução local** de A (consulta OCI direta) e B (Diun real) sobre o registry controlado. O script `scripts/B/measure_vunnel.py` exercita a coleta do feed com Vunnel quando a ferramenta e a rede estão disponíveis. Esses ensaios geram **recibos novos no diretório temporário escolhido pelo executor**; eles não substituem os recibos arquivados neste diretório.

Assim, há três coisas distintas para conferir: (1) a fixture e seus hashes publicados, (2) os resultados de uma execução nova, e (3) o registro histórico dos 44 casos. Compare o resultado novo com o histórico apenas quando entradas, versões e escopo coincidirem.

## O que foi adaptado para publicação

O ledger de camadas continha caminhos absolutos do computador de origem. Nesta cópia, **somente esses caminhos e a referência a um cache temporário foram trocados por caminhos relativos**. Os hashes encadeados no `suite-proof.json`, `inputs.json` e `I0-H1/manifest.json` foram recalculados para os bytes da cópia pública. Portanto, estes quatro arquivos são **derivados sanitizados**; não afirmamos que são idênticos aos originais arquivados. Os digests OCI, versões de pacote e resultados técnicos não foram alterados. O manifesto `SHA256SUMS` identifica exatamente a cópia publicada.

## Limites explícitos

- A matriz de 44 casos está em `rows.json` como resultado arquivado. As capturas completas que a geraram somam cerca de 211 MB, incluindo camadas públicas repetidas e o banco Vunnel. Elas **não estão neste repositório**; portanto os scripts A/B incluídos reproduzem seus respectivos percursos locais, mas **não** o comparador integral de 44 casos.
- Os 34 blobs brutos da imagem pública não foram importados. O ledger e o recibo mostram o que foi verificado no laboratório, mas uma nova inspeção integral exige baixar os blobs por digest e conferir os hashes.
- Os recibos incluídos não comprovam implantação, certificação ou operação contínua.

Para repetir somente o caminho principal com os scripts incluídos, siga o [runbook](../docs/RUNBOOK.md). Para auditar a matriz completa, use o acervo original do experimento e seu runbook local até que seja publicada uma forma portátil de obter e verificar os arquivos grandes.
