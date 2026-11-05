# Histórico de versões

Este projeto ainda não possui release pública final homologada. Versões candidatas não devem ser interpretadas como release estável.

## Candidato de validação — 5 de novembro de 2026

- Reexecutados 102 testes da aplicação (101 passaram; 1 skip DPAPI), 8 testes Open Core, compilação e smoke da interface.
- O EXE e o ZIP Windows foram reconstruídos em `work/validation`; ambos passaram os smoke tests após extração limpa. O modo empacotado de manutenção também passou com dados isolados.
- O instalador NSIS 3.13 foi compilado e testado em pasta isolada: instalação, smoke do EXE, desinstalação, preservação de dados e preservação de arquivos alheios passaram. O script e o manifesto foram corrigidos a partir dos erros reais do compilador.
- O asset PIX foi verificado byte a byte no pacote Windows e continua ausente do ZIP-fonte.
- A build foi feita sem credencial OAuth; login real, DPAPI de destino e integração YouTube permanecem pendentes. Releases anteriores não foram substituídas.
- A auditoria das páginas Cloudflare confirmou HTTP 200 e os links de política do Google/YouTube; foi identificada uma distinção a corrigir na redação de prazos de exclusão após revogação externa. A correção local está em `POLITICA-DE-PRIVACIDADE.md`; a página hospedada ainda aguarda acesso à origem e ao projeto para implantação.

## Não lançado — escopo Open Core em andamento

- Separado o motor genérico de recorrência em `open_core/recurrence.py` sob MPL-2.0, com testes independentes.
- Adicionada lista consolidada de autorizações externas, mapa preliminar de licenças, arquitetura e auditoria inicial de escopo OAuth.
- Mantidas as correções anteriores de salvamento SQLite, ETag, concorrência, sincronização, deduplicação, callbacks Tk e retenção local.
- Implementados menus globais, temas claro/escuro, importação/exportação JSON local sem dados de API/credenciais, exclusão por filtros com prévia e confirmação remota, lembrete de apoio com PIX privado, integração opcional com a bandeja Windows, consulta manual de releases e manutenção OAuth opt-in pelo Agendador do Windows.
- O ZIP-fonte foi restringido a uma allowlist do Open Core; o QR PIX e o núcleo proprietário não entram no pacote público. O build Portable candidato incorpora o QR somente no Windows e copia licenças/EULA/avisos.
- O primeiro commit Open Core foi publicado em `TDAHzeirenses/liveflow` e contém somente os 12 arquivos allowlistados. Essa publicação não é uma release binária do LiveFlow para Windows.
- Ainda pendentes: confirmação OAuth do projeto `logindeYT`, login real, operações YouTube reais, DPAPI no perfil Windows de destino, implantação da correção de texto no Cloudflare e validação visual da bandeja numa sessão Explorer. O Setup candidato não tem assinatura Authenticode.
