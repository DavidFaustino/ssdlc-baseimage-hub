# Roteiro de conferência e execução

Use este roteiro como pessoa revisora. Cada passo diz o que observar e quando parar. Há **dois níveis de reprodução**: o [núcleo incluído neste repositório](RUNBOOK.md) e a comparação integral de 44 casos, que ainda exige o acervo bruto local. Não confunda um com o outro.

## Parte 1 — conferir o que está entregue aqui

1. Abra [Marco atual](STATUS.md). Confira que cada frente está marcada como processo informado, prova local, proposta ou pendência. **Pare** se algum item sugerir que a POC já certificou uma imagem ou implantou uma ferramenta.
2. Abra [Arquitetura](ARCHITECTURE.md). Leia primeiro a cadeia que já existe e depois o bloco proposto de observação. **Saída esperada:** conseguir apontar o local da nova informação sem criar outra aprovação ou substituir a reconstrução diária.
3. Abra [POC](POC.md). Confira separadamente o caso histórico, a leitura pública pontual e a comparação das entradas. **Saída esperada:** identificar que a troca da tag foi controlada localmente e que 38 dos 44 casos ficaram parciais.
4. Abra [Workflows](WORKFLOWS.md). **Saída esperada:** distinguir a história sintética concluída do fluxo completo de desenvolvimento ainda proposto.
5. Anote correções no [marco](STATUS.md) e na página temática. Para mudar um estado para “provado”, exija entrada, saída, teste e recibo correspondentes.

## Parte 2 — repetir a prova incluída neste repositório

Siga o [runbook reproduzível](RUNBOOK.md): conferir os hashes, instalar dependências numa venv, rodar os 18 testes incluídos, repetir a decisão e conferir a recuperação do recibo. **Esperado:** uma candidata para validação, uma reavaliação do mesmo digest, nenhuma aprovação automática. **Pare** em qualquer falha de hash ou teste.

## Parte 3 — auditar a comparação integral no acervo local

**Pré-requisito:** acesso à pasta `Engineer/2_pocs/base_image_hub`, Python 3 e às dependências e binários descritos no runbook local `experiments/operational-abc-comparison-20261108/RUNBOOK.md`. Faça a execução em diretório de saída novo. O registry do caso histórico é local; estes comandos não mudam uma tag pública. Não cole credenciais nos comandos ou recibos.

1. **Conferir integridade das capturas B.** Na raiz da POC local, execute:

   ```sh
   cd experiments/operational-abc-comparison-20261108/evidence/B
   shasum -a 256 -c SHA256SUMS
   ```

   **Esperado:** todos os hashes conferem. **Pare** se algum falhar; a comparação não pode usar capturas alteradas.

2. **Recalcular a matriz comparativa.** Volte à raiz da POC e prepare as dependências conforme o runbook local. Execute:

   ```sh
   python3 experiments/operational-abc-comparison-20261108/scripts/C/compare.py
   ```

   **Esperado na captura arquivada:** 44 casos, sendo 6 completos e 38 parciais, sem falha ou bloqueio. Leia `experiments/operational-abc-comparison-20261108/evidence/C/rows.json`. **Pare** se os números mudarem antes de verificar entradas e hashes.

3. **Repetir a leitura pública arquivada, sem rede.** Use um diretório de saída vazio:

   ```sh
   python3 experiments/operational-abc-comparison-20261108/scripts/C/public_pipeline_replay.py --output-dir /private/tmp/public-pipeline-replay-novo
   ```

   **Esperado:** uma observação, duas reavaliações, nenhuma decisão de trocar imagem, duplicata ignorada e `unknown` para entradas adulteradas. Leia o recibo no diretório de saída. **Pare** se a execução produzir aprovação ou promoção: isso violaria o escopo.

4. **Repetir detecção A e B, se necessário.** Siga os pré-requisitos específicos dos relatórios locais `A.md` e `B.md`; eles usam, respectivamente, consulta direta e Diun real sobre o mesmo registry controlado. Compare recibos e estado, não só o número de requisições. A fonte Debian e Vunnel devem se referir à **mesma CVE e advisory**.

## Parte 4 — antes de levar ao trabalho

Use [Próxima etapa](NEXT-STEPS.md) para validar a cadeia existente, o papel do proxy e o ponto de entrada do resultado. Os scripts acima **não** devem ser copiados para um CI corporativo sem adaptar acesso, fonte de segurança, plataforma, armazenamento dos recibos e gates já existentes. O primeiro piloto nesse ambiente deve registrar uma candidata sem certificá-la automaticamente.
