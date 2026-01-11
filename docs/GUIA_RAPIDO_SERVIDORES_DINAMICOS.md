# Guia Rápido - Sistema de Servidores Dinâmicos

## Para Desenvolvedores

### Como Atualizar Lista de Servidores (30k+ clientes)

#### Opção 1: Via `config.py` (Recomendado)

1. Edite `api/config.py`
2. Modifique a lista `LICENSE_SERVERS`:
```python
LICENSE_SERVERS = [
    "https://api.epr.app.br",                  # Servidor Principal
    "https://novo-backup1.com",            # Novo Backup 1
    "https://novo-backup2.com",            # Novo Backup 2
]
```

3. Reinicie a API
4. **Pronto!** Clientes atualizarão automaticamente nas próximas 24 horas

#### Opção 2: Via Variável de Ambiente

```bash
export LICENSE_SERVERS="https://api.epr.app.br,https://backup1.com,https://backup2.com"
```

Reinicie a API.

### Testar Endpoint

```bash
curl https://api.epr.app.br/servers
```

Resposta esperada:
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

## Para Usuários Finais

### Como Funciona

O sistema **atualiza automaticamente** a lista de servidores. Você não precisa fazer nada!

### Se Algo Der Errado

1. **Limpar cache manualmente:**
   - Delete: `%AppData%\LicenseSystem\servers_cache.json`
   - Reinicie o programa

2. **Verificar logs:**
   - Abra: `%Temp%\license_config_log.txt`
   - Procure por erros

3. **Verificar internet:**
   - O sistema precisa de internet para atualizar servidores
   - Se não houver internet, usa servidores fallback hardcoded

## Estrutura de Arquivos

```
ahk-client/
  └── SOLUCAO_COM_REDUNDANCIA.ahk  (Cliente com sistema dinâmico)

api/
  ├── app.py                        (Endpoint /servers)
  └── config.py                     (Configuração LICENSE_SERVERS)

docs/
  ├── SISTEMA_SERVIDORES_DINAMICOS.md  (Documentação completa)
  └── GUIA_RAPIDO_SERVIDORES_DINAMICOS.md  (Este arquivo)
```

## Configurações Importantes

### No Cliente AHK

```autohotkey
; Endpoint para baixar lista de servidores
g_ConfigEndpoint := "https://api.epr.app.br/servers"

; Cache válido por 1 hora (3600 segundos)
g_ConfigCacheMaxAge := 3600

; Verifica atualizações a cada 24 horas (86400 segundos)
g_ConfigUpdateInterval := 86400
```

### No Backend

```python
# api/config.py
LICENSE_SERVERS = [
    "https://api.epr.app.br",
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com",
]
```

## Fluxo de Atualização

```
┌─────────────────┐
│ Cliente Inicia  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Cache Válido?      │
│ (< 1 hora)         │
└────┬───────────┬───┘
     │ SIM       │ NÃO
     ▼           ▼
┌─────────┐  ┌──────────────────┐
│ Usa     │  │ Baixa do         │
│ Cache   │  │ /servers         │
└─────────┘  └────┬──────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Sucesso?        │
         └────┬─────────┬──┘
              │ SIM     │ NÃO
              ▼         ▼
      ┌───────────┐  ┌──────────────┐
      │ Salva     │  │ Usa Fallback │
      │ Cache     │  │ Hardcoded    │
      └───────────┘  └──────────────┘
```

## Vantagens

✅ **Sem Recompilação**: Atualiza 30k+ clientes sem redistribuir executável  
✅ **Automático**: Clientes se atualizam sozinhos  
✅ **Resiliente**: Sempre funciona, mesmo se endpoint falhar  
✅ **Rápido**: Cache local reduz latência  
✅ **Centralizado**: Gerencie tudo de um lugar  

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Cliente não atualiza | Limpar cache: `%AppData%\LicenseSystem\servers_cache.json` |
| Endpoint não responde | Verificar se API está rodando |
| Servidores incorretos | Verificar `config.py` e reiniciar API |
| Cache sempre inválido | Verificar permissões em `%AppData%\LicenseSystem\` |

## Suporte

Para mais detalhes, consulte: `docs/SISTEMA_SERVIDORES_DINAMICOS.md`
