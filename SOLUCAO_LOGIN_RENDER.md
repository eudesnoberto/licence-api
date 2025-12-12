# 🔧 Solução: Login Falhou no Render

## ❌ Problema

O login com `admin/admin123` está falhando no Render.

## 🔍 Possíveis Causas

1. **Senha foi alterada** no Render
2. **Usuário admin não foi criado** corretamente
3. **Banco de dados novo** sem usuário padrão

---

## ✅ Soluções

### **Opção 1: Resetar Senha via Dashboard** (Mais Fácil)

1. Acesse o dashboard: `https://fartgreen.fun/#dashboard`
2. Tente fazer login
3. Se falhar, use "Esqueceu a senha?"
4. Ou crie um novo usuário admin via código

### **Opção 2: Criar Usuário Admin via API Direta**

Se você tem acesso ao código do Render, pode criar um script temporário:

```python
# criar_admin_render.py
import sqlite3
import hashlib

def _hash_admin_password(raw: str) -> str:
    return hashlib.sha256(f"admin-salt::{raw}".encode("utf-8")).hexdigest()

# Conectar ao banco do Render (caminho pode variar)
DB_PATH = "/opt/render/project/src/api/license.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Criar ou atualizar admin
username = "admin"
password = "admin123"
password_hash = _hash_admin_password(password)

# Verificar se existe
cur.execute("SELECT id FROM admin_users WHERE username = ?", (username,))
if cur.fetchone():
    # Atualizar senha
    cur.execute(
        "UPDATE admin_users SET password_hash = ?, must_change_password = 0 WHERE username = ?",
        (password_hash, username)
    )
    print("✅ Senha do admin resetada!")
else:
    # Criar novo
    cur.execute(
        "INSERT INTO admin_users (username, password_hash, must_change_password) VALUES (?, ?, 0)",
        (username, password_hash)
    )
    print("✅ Admin criado!")

conn.commit()
conn.close()
```

### **Opção 3: Usar SQL Direto no Render** (Se tiver acesso)

1. Acesse o shell do Render
2. Execute SQL direto:

```sql
-- Verificar se admin existe
SELECT * FROM admin_users WHERE username = 'admin';

-- Criar ou resetar admin
DELETE FROM admin_users WHERE username = 'admin';
INSERT INTO admin_users (username, password_hash, must_change_password) 
VALUES ('admin', '20e7f11e408021b5b954664afe93796078873514c5b0082499c1950021633a8a', 0);
```

O hash acima é para a senha `admin123`.

### **Opção 4: Importar Apenas Licenças** (Sem Usuários)

Se você só quer importar as licenças, pode fazer login com qualquer método acima e depois executar apenas a parte de importação de licenças.

---

## 🎯 Recomendação

**A forma mais fácil é:**

1. Acesse o dashboard: `https://fartgreen.fun/#dashboard`
2. Tente fazer login
3. Se não funcionar, use a opção de "Esqueceu a senha?"
4. Ou crie um novo usuário admin manualmente no código

Depois que conseguir fazer login, execute novamente:
```powershell
python importar_para_render.py
```

---

**Documento criado em**: 2024-12-15



