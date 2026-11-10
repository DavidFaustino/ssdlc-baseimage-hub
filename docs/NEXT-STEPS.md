# Retomada sem perder o contexto

## Marco de decisão

**Estado:** a POC técnica local produziu evidências úteis; a inserção dessa capacidade na cadeia atual ainda é desenho. Não há decisão de adotar Diun, Vunnel, outro monitor ou um sistema novo. O repositório público contém um protótipo visual, não um produto conectado.

## Ordem recomendada para a próxima etapa

1. **Revisar o AS-IS com os donos da cadeia.** Validar onde a matriz diária observa hoje a referência upstream, o digest usado no build e a versão do pacote. Registrar o que já é produzido por CI, scanners e catálogo. Não redesenhar gates já existentes.
2. **Definir o menor encaixe funcional.** Para uma imagem piloto, registrar tag, plataforma, digest upstream, digest do pacote inspecionado, advisory e resultado. Decidir se essa checagem roda na matriz atual ou antes dela; isto é uma escolha de arquitetura, não uma disputa de ferramentas.
3. **Definir a fronteira do JFrog.** Especificar se a observação do manifesto deve enxergar a origem ou a resposta do proxy, qual atraso de cache é aceitável e como pedir a candidata por digest. Verificar os bytes obtidos. Não presumir que uma tag em cache equivale à tag atual da origem.
4. **Executar um piloto no ambiente de destino.** Usar uma imagem autorizada, sem promover nada automaticamente; ligar os recibos aos gates e aos artefatos que a cadeia já guarda. Repetir os casos de digest estável, mudança, fix ausente e erro de fonte.
5. **Só então empacotar o processo como workflow/skill.** O guia de replicação deve pedir as entradas do ambiente, produzir artefatos nomeados e parar em decisões fora do contrato. Não importar cegamente caminhos, versões, segredos ou digests do laboratório.

## Perguntas abertas que mudam o desenho

- A matriz diária já registra e compara o digest **filho da plataforma** ou apenas reconstrói a tag?
- Quais evidências de SBOM e pacote já saem de Xray/Trivy, vinculadas ao digest exato?
- A atualização de advisory precisa acionar reavaliação antes da próxima rodada diária?
- Qual é a tolerância de atraso do manifesto no proxy e quem é dono dessa política?
- Qual gate atual recebe a candidata e quem autoriza certificação/promoção?

**Pronto para levar como discussão:** [arquitetura](ARCHITECTURE.md) e [estado da POC](STATUS.md). **Não levar como decisão fechada:** comparação de ferramentas ou o protótipo de painel.
