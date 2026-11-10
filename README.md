# Base Image Hub

## Comece aqui

Abra o [guia do projeto](docs/README.md). Ele mostra o que foi feito, onde encontrar as provas e o que ainda falta. Para repetir os testes incluídos neste repositório, siga o [runbook](docs/RUNBOOK.md).

Este repositório também contém um **protótipo visual** com dados demonstrativos. Ele não executa a POC nem se conecta ao processo real.

![Visão geral do Base Image Hub](preview.png)

## Abrir o protótipo visual

Abra `index.html` diretamente no navegador. O HTML contém os estilos, os ícones e o JavaScript; não requer instalação nem acesso à internet.

Para uma prévia por HTTP:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Acesse http://127.0.0.1:8765.

## Áreas disponíveis

- Visão geral da operação e prioridades.
- Jornada das imagens, com busca e filtro por estado.
- Automações, agenda e histórico demonstrativo.
- Catálogo de imagens e detalhes de certificação.
- Adoção e cobertura por ambiente.
- Arquitetura conceitual com componentes clicáveis.
- Roadmap com entregas e dependências.

O botão **Baixar HTML** exporta uma cópia independente do protótipo.

## Estado do projeto

Esta versão usa dados demonstrativos. A arquitetura está apresentada para validação com o processo real. Não há integração com GitHub, ECR, S3, JFrog, scanners ou backend de automações.

Verificações realizadas: sintaxe JavaScript, navegação nas sete áreas, busca sem resultados, limpeza e filtro por estado, detalhes das imagens, fechamento por Escape e detalhes da arquitetura.
