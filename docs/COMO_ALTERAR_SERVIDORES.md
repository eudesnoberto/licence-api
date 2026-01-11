# Como Alterar Servidores - Guia Rápido

## 🎯 Onde Alterar

### **Arquivo: `api/config.py` (Linhas 108-112)**

```python
LICENSE_SERVERS = [
    "https://api.epr.app.br",                    # ← Servidor Principal
    "https://licence-api-6evg.onrender.com",     # ← Backup 1
    "https://api-epr.rj.r.appspot.com",          # ← Backup 2
]
```

## 📝 Passo a Passo

### 1. Edite o arquivo `api/config.py`

Abra o arquivo e modifique a lista `LICENSE_SERVERS`:

```python
LICENSE_SERVERS = [
    "https://novo-servidor-1.com",      # Novo servidor principal
    "https://novo-servidor-2.com",      # Novo backup 1
    "https://novo-servidor-3.com",      # Novo backup 2
]
```

### 2. Reinicie a API

Após salvar o arquivo, reinicie o servidor da API:

```bash
# Se estiver usando systemd
sudo systemctl restart sua-api

# Se estiver rodando manualmente
# Pare o processo (Ctrl+C) e inicie novamente
python app.py
```

### 3. Pronto! ✅

Os 30k+ clientes atualizarão automaticamente:
- **Imediato**: Clientes que executarem agora baixarão a nova lista
- **Automático**: Clientes existentes atualizarão nas próximas 24 horas
- **Cache**: Se cache for inválido (>1 hora), atualiza imediatamente

## 🔄 Como Funciona

```
Você altera config.py
    ↓
Reinicia API
    ↓
Endpoint /servers retorna nova lista
    ↓
Clientes baixam automaticamente
    ↓
Salvam no cache local
    ↓
Usam nova lista de servidores
```

## 🌐 Opção 2: Variável de Ambiente

Se preferir não editar código, use variável de ambiente:

```bash
export LICENSE_SERVERS="https://servidor1.com,https://servidor2.com,https://servidor3.com"
```

Depois reinicie a API. A variável de ambiente **sobrescreve** o `config.py`.

## ✅ Testar Alteração

### 1. Teste o endpoint:

```bash
curl https://api.epr.app.br/servers
```

Deve retornar:
```json
{
  "version": 1,
  "timestamp": 20260110220000,
  "servers": [
    "https://novo-servidor-1.com",
    "https://novo-servidor-2.com",
    "https://novo-servidor-3.com"
  ]
}
```

### 2. Verifique nos clientes:

Os clientes baixarão automaticamente. Para forçar atualização imediata:

1. Delete o cache: `%AppData%\LicenseSystem\servers_cache.json`
2. Execute o cliente novamente
3. Ele baixará a nova lista

## 📊 Monitoramento

### Ver logs da API:

```bash
# Logs mostrarão quantos servidores estão sendo retornados
INFO:__main__:SERVERS: Retornando lista com 3 servidores
```

### Ver logs dos clientes:

Arquivo: `%Temp%\license_config_log.txt`

```
[2026-01-10 22:00:00] Lista de servidores atualizada com sucesso de: https://api.epr.app.br/servers
```

## ⚠️ Importante

1. **Ordem importa**: Primeiro servidor é tentado primeiro
2. **Sempre mantenha fallbacks**: Não remova todos os servidores
3. **Teste antes**: Verifique se novos servidores estão funcionando
4. **Cache**: Clientes podem usar cache por até 1 hora

## 🚀 Exemplo Prático

### Adicionar novo servidor:

```python
LICENSE_SERVERS = [
    "https://api.epr.app.br",                    # Mantém principal
    "https://novo-backup-super-rapido.com",      # Novo servidor
    "https://licence-api-6evg.onrender.com",     # Mantém backup antigo
    "https://api-epr.rj.r.appspot.com",          # Mantém backup antigo
]
```

### Trocar servidor principal:

```python
LICENSE_SERVERS = [
    "https://novo-servidor-principal.com",       # Novo principal
    "https://api.epr.app.br",                    # Vira backup
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com",
]
```

## 📍 Localização do Arquivo

```
c:\protecao\
  └── api\
      └── config.py  ← EDITE AQUI (linhas 108-112)
```

---

**Resumo**: Edite `api/config.py` → Reinicie API → Clientes atualizam automaticamente! 🎉
