# Migração de assinatura RSA para licenças offline

## Objetivo

Esta branch prepara a emissão de tokens offline assinados com RSA-SHA256. O servidor guarda a chave privada; o cliente AutoHotkey contém somente a chave pública e verifica a assinatura antes de aceitar o cache.

## Compatibilidade

- O endpoint `/verify`, a resposta `allow/msg/config`, o fluxo de cadastro, os registros e as tabelas existentes foram mantidos.
- A assinatura compartilhada da requisição foi desativada por padrão (`REQUIRE_SIGNATURE=false`) para permitir a transição de clientes antigos e novos.
- A chave de API continua exigida por padrão (`REQUIRE_API_KEY=true`) e agora o cliente novo a envia no cabeçalho `X-API-Key`, não na URL.
- Mantenha `SHARED_SECRET` configurado no ambiente da API: ele ainda é usado para assinar os tokens de autenticação do painel administrativo.
- A conexão MySQL exige TLS com validação do certificado e da identidade do servidor. Nenhuma migração de schema é necessária para a assinatura RSA.

## Configuração no Render e Aiven

1. Mantenha as variáveis atuais `DB_TYPE`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER` e `MYSQL_PASSWORD`.
2. Mantenha `MYSQL_SSL_ENABLED=true` e `MYSQL_SSL_VERIFY_IDENTITY=true`.
3. Baixe o certificado CA da conexão no painel do serviço MySQL da Aiven.
4. No Render, cadastre o certificado como **Secret File**, por exemplo com o nome `aiven-ca.pem`.
5. Configure `MYSQL_SSL_CA` com o caminho exato do Secret File mostrado pelo Render (por exemplo, `/etc/secrets/aiven-ca.pem`, se esse for o caminho exibido).
6. Gere/guarde uma chave privada RSA PKCS#8 de pelo menos 3072 bits. A chave privada não deve ser adicionada ao Git.
7. Em cada serviço que assina tokens, cadastre-a em **Secret Files** com o nome `license_signing_private.pem`. A API a lê de `/etc/secrets/license_signing_private.pem`.
8. Para desenvolvimento local, defina `LICENSE_SIGNING_PRIVATE_KEY_FILE` com o caminho de um PEM de desenvolvimento. A variável Base64 antiga continua aceita como fallback temporário, mas não é necessária no Render.
9. Mantenha `REQUIRE_API_KEY=true`, `API_KEY` e `SHARED_SECRET` configurados com os valores atuais.
10. Defina `REQUIRE_SIGNATURE=false` durante a migração. Não habilite novamente sem primeiro migrar todos os clientes online.

Sem a chave privada, a API continua respondendo às verificações online, mas não emite token offline. Isso evita emitir um token sem assinatura verificável.

## Teste seguro usando o mesmo banco

O script `api/smoke_test_readonly.py` faz apenas:
- validação da configuração TLS;
- conexão TLS à Aiven;
- consultas `SELECT 1` e `SELECT COUNT(*) FROM devices`;
- criação e verificação local de uma assinatura RSA de teste.

Execute dentro da pasta `api` com `python smoke_test_readonly.py`. O script não chama `init_db()`, não chama o endpoint `/verify`, não insere/atualiza/exclui dados e não exibe IDs de licença.

**Atenção:** não use o endpoint `/verify` com a licença real como primeiro teste. Esse endpoint atualiza métricas de acesso e grava logs; dependendo da detecção de clones, também pode bloquear um dispositivo. O teste completo de emissão de token pelo endpoint deve ser feito depois de preparar um fluxo isolado e controlado.

## Política offline escolhida

- Não existe prazo de carência adicional: um token assinado de licença perpétua (`expires_at: null`) pode ser usado offline sem limite de tempo.
- Licenças com data de término continuam respeitando essa data mesmo offline.
- Um dispositivo bloqueado ou uma licença revogada só será conhecido pelo cliente quando voltar a consultar a API. Uso offline ilimitado não permite revogação remota instantânea.
- Tokens antigos assinados por HMAC não são aceitos pelo novo validador RSA. Cada cliente precisa conectar-se uma vez à API após a implantação para receber o novo token RSA.

## Ordem de implantação segura

1. Faça backup do MySQL/Aiven e confirme que o backup pode ser restaurado.
2. Cadastre a CA da Aiven como Secret File e configure `MYSQL_SSL_CA`.
3. Cadastre a mesma chave privada RSA como Secret File nos serviços que emitem tokens, sem colocá-la no GitHub.
4. Execute `python smoke_test_readonly.py` no ambiente de teste ou Shell autorizado. Ele não altera os dados.
5. Valide o cliente AHK em Windows com uma licença de teste isolada antes de usar a licença real.
6. Só depois revise a PR e planeje a publicação em produção.

## Itens que ainda exigem validação antes de produção

- Compilar/executar o AHK no Windows com AutoHotkey v1.1 e PowerShell compatível.
- Testar o fluxo completo do endpoint `/verify` com um dispositivo de teste controlado. Esse endpoint grava logs e métricas e pode bloquear em caso de detecção de clone.
- Testar o modo offline e failover dos servidores.
- A chave de API embutida no cliente já foi publicada no repositório público; trate-a como exposta e planeje sua rotação coordenada após atualizar os clientes. Não a rotacione isoladamente, pois os clientes antigos podem parar de validar.
- A configuração CORS, o proxy Cloudflare e os endpoints do dashboard não foram alterados nesta branch.
