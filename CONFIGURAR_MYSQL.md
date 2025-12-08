# 🗄️ Configuração MySQL - Banco Centralizado

## 🎯 Objetivo

Migrar de SQLite local para MySQL remoto no HostGator, permitindo que **todos os servidores** (local, Render, Koyeb) usem o **mesmo banco de dados centralizado**.

---

## 📋 Informações do Banco

- **Host**: `108.179.252.54`
- **Porta**: `3306`
- **Database**: `scpmtc84_api`
- **Usuário**: `scpmtc84_api`
- **Senha**: `nQT-8gW%-qCY`
- **Status**: ✅ Liberado para acesso remoto

---

## 🚀 Passo a Passo

### **Passo 1: Instalar Dependências**

No servidor local e em todos os servidores de nuvem:

```bash
cd api
pip install pymysql
```

Ou atualizar `requirements.txt` (já atualizado):
```bash
pip install -r requirements.txt
```

---

### **Passo 2: Configurar Variáveis de Ambiente**

Crie ou edite o arquivo `.env` na pasta `api/`:

```env
# Tipo de banco: "sqlite" ou "mysql"
DB_TYPE=mysql

# Configuração MySQL (HostGator)
MYSQL_HOST=108.179.252.54
MYSQL_PORT=3306
MYSQL_DATABASE=scpmtc84_api
MYSQL_USER=scpmtc84_api
MYSQL_PASSWORD=nQT-8gW%-qCY
```

---

### **Passo 3: Criar Tabelas no MySQL**

O código criará automaticamente as tabelas na primeira execução, mas você pode executar manualmente:

```bash
python api/app.py
```

As tabelas serão criadas automaticamente se não existirem.

---

### **Passo 4: Migrar Dados do SQLite para MySQL**

Execute o script de migração:

```bash
python migrar_sqlite_para_mysql.py
```

Este script irá:
- ✅ Conectar ao SQLite local
- ✅ Conectar ao MySQL remoto
- ✅ Migrar todas as tabelas
- ✅ Preservar todos os dados

---

### **Passo 5: Configurar Servidores de Nuvem**

Para cada servidor (Render, Koyeb), adicione as variáveis de ambiente:

#### **Render:**
1. Dashboard → Seu serviço → Environment
2. Adicione:
   - `DB_TYPE=mysql`
   - `MYSQL_HOST=108.179.252.54`
   - `MYSQL_PORT=3306`
   - `MYSQL_DATABASE=scpmtc84_api`
   - `MYSQL_USER=scpmtc84_api`
   - `MYSQL_PASSWORD=nQT-8gW%-qCY`

#### **Koyeb:**
1. Dashboard → Seu serviço → Settings → Environment Variables
2. Adicione as mesmas variáveis acima

---

## ✅ Vantagens da Solução MySQL

1. **Banco Centralizado**: Todos os servidores usam o mesmo banco
2. **Dados Persistidos**: Não perde dados quando servidor reinicia
3. **Sincronização Automática**: Mudanças em um servidor refletem em todos
4. **Backup Centralizado**: Backup único no HostGator
5. **Escalabilidade**: Suporta múltiplos servidores simultaneamente

---

## 🔄 Voltar para SQLite (se necessário)

Se precisar voltar para SQLite local:

```env
DB_TYPE=sqlite
DB_PATH=api/license.db
```

---

## 🧪 Testar Conexão MySQL

Execute este script para testar:

```python
import pymysql

try:
    conn = pymysql.connect(
        host="108.179.252.54",
        port=3306,
        user="scpmtc84_api",
        password="nQT-8gW%-qCY",
        database="scpmtc84_api",
        charset='utf8mb4'
    )
    print("✅ Conexão MySQL bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
```

---

## 📊 Estrutura das Tabelas

As tabelas serão criadas automaticamente com:

- `devices` - Licenças
- `users` - Usuários/revendedores
- `admin_users` - Administradores
- `blocked_devices` - Dispositivos bloqueados
- `access_logs` - Logs de acesso
- `license_history` - Histórico de licenças

---

## ⚠️ Importante

1. **Segurança**: As credenciais estão no `.env` (não versionado)
2. **Backup**: Configure backup automático no HostGator
3. **Performance**: MySQL remoto pode ser mais lento que SQLite local
4. **Conexão**: Certifique-se de que o IP está liberado no HostGator

---

## 🔍 Troubleshooting

### **Erro: "pymysql não instalado"**
```bash
pip install pymysql
```

### **Erro: "Access denied"**
- Verifique se o IP está liberado no HostGator
- Verifique credenciais no `.env`

### **Erro: "Database does not exist"**
- Crie o banco `scpmtc84_api` no HostGator
- Ou ajuste `MYSQL_DATABASE` no `.env`

---

**Pronto!** Todos os servidores agora usam o mesmo banco MySQL centralizado! 🚀

