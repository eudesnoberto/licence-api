# 🗄️ Solução: Banco de Dados Persistente no Render

## 🎯 Problema

O SQLite no Render free é **efêmero**:
- ⚠️ Perde dados quando servidor reinicia
- ⚠️ Sistema de arquivos é temporário
- ⚠️ Não há volume persistente no plano free

---

## ✅ Solução: Migrar para PostgreSQL (GRATUITO)

O Render oferece **PostgreSQL gratuito** que persiste dados mesmo quando o servidor reinicia!

---

## 📋 Passo a Passo

### **Passo 1: Criar Banco PostgreSQL no Render**

1. Acesse: https://dashboard.render.com
2. Clique em **"New +"** → **"PostgreSQL"**
3. Preencha:
   - **Name**: `license-db`
   - **Database**: `license_db`
   - **User**: (será gerado automaticamente)
   - **Region**: Escolha a mesma região do seu serviço
   - **PostgreSQL Version**: 15 (ou mais recente)
   - **Plan**: Free
4. Clique em **"Create Database"**

---

### **Passo 2: Obter Connection String**

1. No dashboard do banco, vá em **"Connections"**
2. Copie a **"Internal Database URL"** (para uso dentro do Render)
3. Ou copie a **"External Database URL"** (para uso externo)

Exemplo:
```
postgresql://user:password@dpg-xxxxx-a/license_db
```

---

### **Passo 3: Configurar Variável de Ambiente**

1. Dashboard → Seu serviço (licence-api-zsbg) → **Environment**
2. Adicione:
   - **Key**: `DATABASE_URL`
   - **Value**: Cole a connection string do PostgreSQL
3. Clique em **"Save Changes"**

---

### **Passo 4: Atualizar Código (Próximo Passo)**

O código precisa ser adaptado para usar PostgreSQL ao invés de SQLite. Isso requer:

1. Instalar `psycopg2`:
   ```bash
   pip install psycopg2-binary
   ```

2. Atualizar `requirements.txt`:
   ```
   psycopg2-binary>=2.9.0
   ```

3. Adaptar `db.py` para usar PostgreSQL

---

## 🎯 Solução Temporária: Keep-Alive

Enquanto não migra para PostgreSQL, use **keep-alive externo**:

1. **UptimeRobot** (recomendado):
   - https://uptimerobot.com
   - Configure para fazer ping em `/ping` a cada 5 minutos
   - Mantém servidor ativo, evitando que "durma"

2. **Script local**:
   - Use `keep_alive.py` se tiver PC sempre ligado

---

## 📊 Comparação

| Aspecto | SQLite (Atual) | PostgreSQL |
|---------|---------------|------------|
| **Persistência** | ❌ Efêmero | ✅ Persistente |
| **Custo** | ✅ Grátis | ✅ Grátis |
| **Dados após restart** | ❌ Perde | ✅ Mantém |
| **Complexidade** | ✅ Simples | ⚠️ Média |

---

## 🚀 Recomendação

**Curto Prazo:**
- ✅ Configure **UptimeRobot** para keep-alive
- ✅ Mantém servidor ativo
- ✅ Evita perda de dados temporária

**Longo Prazo:**
- ✅ Migre para **PostgreSQL**
- ✅ Dados persistem mesmo com restarts
- ✅ Mais robusto para produção

---

**Solução implementada!** Use keep-alive agora e migre para PostgreSQL quando possível! 🚀



