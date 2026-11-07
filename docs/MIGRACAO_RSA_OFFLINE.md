# Migração de assinatura RSA para licenças offline

## Objetivo

Esta branch prepara a emissão de tokens offline assinados com RSA-SHA256. O servidor guarda a chave privada; o cliente AutoHotkey contém somente a chave pública e verifica a assinatura antes de aceitar o cache.

## Compatibilidade

- O endpoint `/verify`, a resposta `allow/msg/config`, o fluxo de cadastro, os registros e as tabelas existentes foram mantidos.
- A assinatura compartilhada da requisição foi desativada por padrão (`REQUIRE_SIGNATURE=false`) para permitir a transição de clientes antigos e novos.
- A chave de API continua exigida por padrão (`REQUIRE_API_KEY=true`) e agora o cliente novo a envia no cabeçalho `X-API-Key`, não na URL.
- Mantenha `SHARED_SECRET` configurado no ambiente da API: ele ainda é usado para assinar os tokens de autenticação do painel administrativo.
- Não remova nem altere as variáveis MySQL/Aiven. Nenhuma migração de banco ou alteração de schema é necessária para esta mudança.

## Configuração obrigatória no servidor

1. Gere/guarde uma chave privada RSA PKCS#8 de pelo menos 3072 bits. A chave privada não deve ser adicionada ao Git.
2. Converta o arquivo PEM inteiro para Base64 em uma única linha, sem cabeçalhos adicionais:
   `[Convert]::ToBase64String([IO.File]::ReadAllBytes("license_signing_private.pem"))`
3. Cadastre o resultado como variável secreta `LICENSE_SIGNING_PRIVATE_KEY_B64` no ambiente onde a API é executada.
4. Mantenha `REQUIRE_API_KEY=true`, `API_KEY` e `SHARED_SECRET` configurados.
5. Defina `REQUIRE_SIGNATURE=false` durante a migração. Não habilite novamente sem primeiro migrar todos os clientes online.

Sem `LICENSE_SIGNING_PRIVATE_KEY_B64`, a API continua respondendo às verificações online, mas não emite token offline. Isso evita emitir um token sem assinatura verificável.

## Política offline escolhida

- Não existe prazo de carência adicional: um token assinado de licença perpétua (`expires_at: null`) pode ser usado offline sem limite de tempo.
- Licenças com data de término continuam respeitando essa data mesmo offline.
- Um dispositivo bloqueado ou uma licença revogada só será conhecido pelo cliente quando voltar a consultar a API. Uso offline ilimitado não permite revogação remota instantânea.
- Tokens antigos assinados por HMAC não são aceitos pelo novo validador RSA. Cada cliente precisa conectar-se uma vez à API após a implantação para receber o novo token RSA.

## Ordem de implantação segura

1. Faça backup do MySQL/Aiven e confirme que o backup pode ser restaurado.
2. Cadastre a chave privada no ambiente da API, sem colocá-la no GitHub.
3. Publique esta branch em ambiente de teste, apontando para uma cópia do banco (não para a base de produção).
4. Teste login do painel, criação/renovação/bloqueio de licença, verificação online, token RSA, modo offline e failover.
5. Distribua o cliente AHK atualizado e confirme que ele recebe e salva um token RSA.
6. Só então abra o PR para revisão e planeje a publicação em produção.

## Itens que ainda exigem validação antes de produção

- Compilar/executar o AHK no Windows com AutoHotkey v1.1 e PowerShell compatível.
- Testar o fluxo completo com o banco de homologação e os servidores de redundância.
- A chave de API embutida no cliente já foi publicada no repositório público; trate-a como exposta e planeje sua rotação coordenada após atualizar os clientes. Não a rotacione isoladamente, pois os clientes antigos podem parar de validar.
- A configuração CORS, o proxy Cloudflare e os endpoints do dashboard não foram alterados nesta branch.
