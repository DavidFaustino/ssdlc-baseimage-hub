# O que a POC técnica demonstrou

Esta página relata provas, não opções de implantação. O caso principal foi uma imagem Distroless Java 21 baseada em Debian 13 e uma correção do pacote `expat`/`libexpat1`.

## Percurso do caso

1. **Caso histórico:** dois digests da mesma variante mostraram `libexpat1` antes e depois de uma versão corrigida. Isso deu uma resposta verificável para exercitar o comparador.
2. **Detecção controlada:** um registry local serviu manifestos históricos como se uma tag tivesse mudado. A consulta OCI direta produziu um evento; Diun produziu um aviso na mudança e nenhum na repetição. A tag pública não foi alterada por nós.
3. **Dados do patch:** a consulta direta ao Debian e a saída processada do Vunnel concordaram para a mesma CVE e o mesmo advisory capturado.
4. **Imagem pública:** uma leitura pontual de uma tag Distroless confirmou índice, manifesto `linux/amd64`, 34 camadas, suite Debian e versão de `libexpat1` para um digest estável.
5. **Estado e falhas:** o validador local guardou baseline, evitou decisões duplicadas e retornou `unknown` para entradas sem vínculo suficiente. Na captura pública, registrou duas reavaliações do feed e **zero decisões de trocar imagem**. O fix da CVE selecionada era igual nas duas revisões do arquivo.

## Comparação das duas entradas

| Rota | O que realmente forneceu | Trabalho que continuou nosso |
|---|---|---|
| **Direta:** OCI + fonte Debian | Consulta do digest e versão corrigida da CVE. | Agenda, estado durável, erros, vínculo da plataforma e recibo. |
| **Com ferramentas:** Diun + Vunnel | Aviso da troca de digest e dados Debian processados. | Resolver e verificar o manifesto filho da plataforma, lidar com aviso perdido e aplicar a mesma regra de correlação. |

Na fixture histórica, as duas rotas chegaram à mesma avaliação. Em três pares locais, a rota direta fez menos requisições. A medição não inclui a operação corporativa e **não é justificativa suficiente para escolher uma ferramenta**. Diun oferece agenda, estado e notificações próprios; a pergunta sobre seu valor deve considerar a matrix diária que já existe.

## O que significa a matriz de 44 casos

Foram **6 completos, 38 parciais, nenhum falho e nenhum bloqueado** na classificação final. “Parcial” quer dizer que houve observação útil, mas aquele cenário não atravessou todas as mesmas etapas nas duas rotas. Portanto, **44 não significa 44 provas completas**. A linha pública que antes estava bloqueada foi fechada somente para o digest e as duas capturas de feed preservadas.

## Limites que importam para replicar

- A troca da tag pública não foi observada; o caso de mudança foi controlado localmente.
- A prova pública cobre uma CVE e a inspeção dirigida de um pacote, não uma certificação de imagem inteira.
- A recuperação após queda foi em parte simulada por exceção após commit; não prova todos os efeitos de uma queda real com transporte externo.
- JFrog, ECR, scanners corporativos, promoção e os consumidores não participaram das provas locais.
- Os horários, digests e custos da captura são evidência daquele experimento, não parâmetros transferíveis ao trabalho.

**Resultado utilizável:** os contratos de identidade e de evidência, os casos negativos e a regra de não afirmar correção sem pacote/fix vinculados ao mesmo digest. **Resultado ainda em discussão:** qual componente deve produzir cada entrada na arquitetura existente.
