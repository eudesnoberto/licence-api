# Sistema de Servidores Dinâmicos - Documentação Técnica

## Visão Geral

Sistema profissional para gerenciar lista de servidores em **30k+ computadores** sem necessidade de recompilar o executável AHK.

## Arquitetura

### Componentes

1. **Cliente AHK** (`SOLUCAO_COM_REDUNDANCIA.ahk`)
   - Baixa lista de servidores do endpoint `/servers`
   - Cache local com versionamento
   - Atualização periódica em background
   - Fallback para servidores hardcoded

2. **API Backend** (`/servers` endpoint)
   - Endpoint público que retorna lista atualizada
   - Configurável via `config.py` ou variável de ambiente
   - Suporta múltiplos servidores em ordem de prioridade

## Como Funciona

### Fluxo de Inicialização

1. Cliente executa e carrega servidores do cache local
2. Se cache inválido ou não existe, baixa do endpoint `/servers`
3. Se falhar download, usa servidores fallback hardcoded
4. Sempre garante que há pelo menos os servidores fallback

### Atualização Periódica

- Verifica atualizações a cada 24 horas (configurável)
- Executa em background sem bloquear o programa
- Atualiza cache local quando encontra nova lista

### Cache Local

- Localização: `%AppData%\LicenseSystem\servers_cache.json`
- Formato JSON com timestamp
- Validade: 1 hora (configurável)
- Estrutura:
```json
{
  "version": 1,
  "timestamp": 20250101120000,
  "servers": [
    "https://api.epr.app.br",
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com"
  ]
}
```

## Configuração

### No Cliente AHK

```autohotkey
; Endpoint para lista de servidores
g_ConfigEndpoint := "https://api.epr.app.br/servers"

; Cache válido por 1 hora
g_ConfigCacheMaxAge := 3600

; Verifica atualizações a cada 24 horas
g_ConfigUpdateInterval := 86400
```

### No Backend (API)

#### Via `config.py`:

```python
LICENSE_SERVERS = [
    "https://api.epr.app.br",
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com",
]
```

#### Via Variável de Ambiente:

```bash
LICENSE_SERVERS="https://api.epr.app.br,https://backup1.com,https://backup2.com"
```

## Endpoint `/servers`

### Requisição

```
GET https://api.epr.app.br/servers
```

### Resposta

```json
{
  "version": 1,
  "timestamp": 20250101120000,
  "servers": [
    "https://api.epr.app.br",
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com"
  ]
}
```

### Características

- **Público**: Não requer autenticação
- **Leve**: Resposta pequena (< 1KB)
- **Rápido**: Sem processamento pesado
- **Cacheável**: Pode ser servido via CDN

## Como Atualizar Servidores

### Método 1: Atualizar `config.py`

1. Edite `api/config.py`
2. Modifique a lista `LICENSE_SERVERS`
3. Reinicie a API
4. Clientes atualizarão automaticamente nas próximas 24h

### Método 2: Variável de Ambiente

1. Configure `LICENSE_SERVERS` no servidor
2. Reinicie a API
3. Clientes atualizarão automaticamente

### Método 3: Forçar Atualização Imediata

Para forçar atualização imediata em todos os clientes:

1. Altere a versão no endpoint (ex: `"version": 2`)
2. Clientes detectarão mudança e atualizarão cache

## Redundância e Fallback

### Níveis de Fallback

1. **Cache Local** (mais rápido)
   - Usado se válido (< 1 hora)

2. **Endpoint `/servers`** (atualizado)
   - Baixado se cache inválido
   - Tenta cada servidor fallback até conseguir

3. **Servidores Hardcoded** (último recurso)
   - Sempre disponíveis no código
   - Garantem funcionamento mesmo se tudo falhar

### Ordem de Tentativa

1. Tenta servidor principal
2. Se falhar, tenta backup 1
3. Se falhar, tenta backup 2
4. E assim por diante...

## Logs e Monitoramento

### Logs do Cliente

Localização: `%Temp%\license_config_log.txt`

Exemplos:
```
[20250101120000] Servidores carregados do cache (válido)
[20250101130000] Cache inválido ou não existe, tentando atualizar...
[20250101130001] Lista de servidores atualizada com sucesso de: https://api.epr.app.br/servers
[20250101130002] Servidores atualizados em background
```

### Logs da API

No console/logs da API:
```
INFO: SERVERS: Retornando lista com 3 servidores
```

## Vantagens da Solução

1. ✅ **Sem Recompilação**: Atualiza 30k+ clientes sem redistribuir executável
2. ✅ **Alta Disponibilidade**: Múltiplos servidores com failover automático
3. ✅ **Cache Inteligente**: Reduz carga no servidor e melhora performance
4. ✅ **Fallback Robusto**: Sempre funciona mesmo se endpoint falhar
5. ✅ **Atualização Automática**: Clientes se atualizam sozinhos
6. ✅ **Configuração Centralizada**: Gerencie tudo de um lugar

## Segurança

- Endpoint público mas pode adicionar rate limiting
- Lista de servidores validada antes de uso
- Fallback hardcoded garante funcionamento mesmo se atacado
- Cache local não expõe informações sensíveis

## Performance

- **Primeira execução**: ~100-200ms (download + cache)
- **Execuções subsequentes**: ~1-5ms (cache local)
- **Atualização em background**: Não bloqueia execução
- **Tamanho da resposta**: < 1KB

## Troubleshooting

### Cliente não atualiza servidores

1. Verifique se há internet
2. Verifique logs em `%Temp%\license_config_log.txt`
3. Verifique se endpoint `/servers` está acessível
4. Limpe cache: delete `%AppData%\LicenseSystem\servers_cache.json`

### Endpoint não responde

1. Verifique se API está rodando
2. Teste manualmente: `curl https://api.epr.app.br/servers`
3. Verifique logs da API
4. Cliente usará fallback hardcoded automaticamente

### Servidores incorretos

1. Verifique `config.py` ou variável `LICENSE_SERVERS`
2. Reinicie API
3. Aguarde até 24h ou force limpeza de cache nos clientes

## Próximos Passos (Melhorias Futuras)

- [ ] Health check automático de servidores
- [ ] Balanceamento de carga baseado em região
- [ ] Métricas de uso por servidor
- [ ] Notificações quando servidor cai
- [ ] Dashboard para gerenciar servidores
