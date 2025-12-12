# 📊 Explicação: Base de Dados Local vs Render

## ⚠️ IMPORTANTE: São Bases de Dados DIFERENTES!

### 🔴 Situação Atual

**Local (sua máquina):**
- Arquivo: `C:\protecao\api\license.db`
- Contém: Todos os usuários, licenças e dados que você criou
- Persiste: Sim, fica salvo no seu computador

**Render (servidor online):**
- Arquivo: Criado automaticamente no servidor (localização varia)
- Contém: **APENAS** o usuário padrão `admin/admin123`
- Persiste: ⚠️ **NÃO!** O Render apaga arquivos a cada deploy (exceto volumes)

---

## 🔍 Por que isso acontece?

### 1. **Render não persiste arquivos por padrão**
- Cada vez que você faz deploy, o Render cria um ambiente novo
- Arquivos criados durante a execução são perdidos no próximo deploy
- SQLite precisa de um arquivo físico que persista

### 2. **Criação automática do admin**
O código em `db.py` cria automaticamente:
```python
# Se não existir nenhum usuário, cria admin/admin123
if count == 0:
    cur.execute(
        "INSERT INTO admin_users (username, password_hash, must_change_password) VALUES (?, ?, 1)",
        ("admin", _hash_admin_password("admin123")),
    )
```

Isso significa:
- ✅ No Render: Sempre cria `admin/admin123` (base vazia)
- ✅ No Local: Só cria se você deletar o banco

---

## ✅ Soluções

### **Opção 1: Usar o usuário padrão no Render** (Mais Rápido)

1. Faça login no Render com:
   - **Usuário**: `admin`
   - **Senha**: `admin123`

2. Depois, altere a senha no dashboard

### **Opção 2: Criar usuário via API** (Recomendado)

Use o endpoint de criação de usuários após fazer login:

```bash
# 1. Login para obter token
curl -X POST https://licence-api-zsbg.onrender.com/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Use o token retornado para criar seu usuário
curl -X POST https://licence-api-zsbg.onrender.com/admin/users/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"username":"seu_usuario","password":"sua_senha","email":"seu@email.com","role":"admin"}'
```

### **Opção 3: Usar Volume Persistente no Render** (Melhor para Produção)

O Render oferece volumes persistentes (pago), mas para SQLite você pode:

1. **Usar PostgreSQL** (Render oferece gratuito)
2. **Usar banco externo** (Supabase, PlanetScale, etc.)
3. **Fazer backup/restore manual** do banco local

---

## 🔄 Sincronizar Dados

### **Exportar do Local para Render:**

```python
# script_exportar.py
import sqlite3
import json

# Conectar ao banco local
conn_local = sqlite3.connect('api/license.db')
conn_local.row_factory = sqlite3.Row

# Exportar usuários
users = conn_local.execute("SELECT * FROM users").fetchall()
admin_users = conn_local.execute("SELECT * FROM admin_users").fetchall()
devices = conn_local.execute("SELECT * FROM devices").fetchall()

# Salvar em JSON
data = {
    'users': [dict(u) for u in users],
    'admin_users': [dict(a) for a in admin_users],
    'devices': [dict(d) for d in devices],
}

with open('backup.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Dados exportados para backup.json")
```

### **Importar no Render:**

Você precisaria criar um endpoint temporário ou usar SQL direto.

---

## 📋 Resumo

| Aspecto | Local | Render |
|---------|------|--------|
| **Arquivo** | `api/license.db` | Criado automaticamente |
| **Usuários** | Todos que você criou | Apenas `admin/admin123` |
| **Licenças** | Todas cadastradas | Nenhuma (base vazia) |
| **Persiste?** | ✅ Sim | ❌ Não (perde no deploy) |
| **Solução** | - | Usar `admin/admin123` ou criar via API |

---

## 🎯 Recomendação Imediata

**Para fazer login no Render agora:**

1. Use: `admin` / `admin123`
2. Depois, altere a senha no dashboard
3. Crie seus usuários normalmente

**Para produção futura:**

- Considere migrar para PostgreSQL (Render oferece gratuito)
- Ou use um serviço de banco externo (Supabase, PlanetScale)

---

**Documento criado em**: 2024-12-15



