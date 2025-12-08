# 🚀 Guia de Deploy - MySQL Centralizado

## ✅ Status do GitHub

**Último commit**: `0f38729`  
**Branch**: `main`  
**Status**: ✅ **Tudo enviado para o GitHub**

---

## 📦 O que foi enviado

### **Backend (API)**
- ✅ Suporte completo MySQL (`api/db.py`, `api/config.py`)
- ✅ Compatibilidade automática SQLite/MySQL
- ✅ Normalização de queries
- ✅ Wrapper `DatabaseCursor` para compatibilidade
- ✅ `requirements.txt` atualizado com `pymysql==1.1.0`

### **Scripts**
- ✅ `criar_tabelas_mysql.py` - Criar tabelas remotamente
- ✅ `migrar_sqlite_para_mysql.py` - Migrar dados
- ✅ `verificar_dados_mysql.py` - Verificar dados migrados
- ✅ `testar_mysql.py` - Testar conexão MySQL

### **Documentação**
- ✅ `CONFIGURAR_MYSQL.md` - Guia completo de configuração
- ✅ `STATUS_MYSQL.md` - Status de compatibilidade
- ✅ `TESTE_APLICACAO.md` - Resultados dos testes

### **Dados**
- ✅ 78 registros migrados para MySQL
- ✅ Tabelas criadas no HostGator

---

## 🔧 Configurar Deploy nos Servidores

### **1. Render**

1. Acesse: https://dashboard.render.com
2. Vá em seu serviço `licence-api`
3. **Settings** → **Environment Variables**
4. Adicione as seguintes variáveis:

```env
DB_TYPE=mysql
MYSQL_HOST=108.179.252.54
MYSQL_PORT=3306
MYSQL_DATABASE=scpmtc84_api
MYSQL_USER=scpmtc84_api
MYSQL_PASSWORD=nQT-8gW%-qCY
```

5. Clique em **Save Changes**
6. O Render fará deploy automático

---

### **2. Koyeb**

1. Acesse: https://app.koyeb.com
2. Vá em seu serviço `licence-api`
3. **Settings** → **Environment Variables**
4. Adicione as mesmas variáveis acima
5. Clique em **Save**
6. O Koyeb fará deploy automático

---

### **3. Servidor Local**

1. Crie/edite `api/.env`:

```env
DB_TYPE=mysql
MYSQL_HOST=108.179.252.54
MYSQL_PORT=3306
MYSQL_DATABASE=scpmtc84_api
MYSQL_USER=scpmtc84_api
MYSQL_PASSWORD=nQT-8gW%-qCY
```

2. Instale dependências:
```bash
cd api
pip install -r requirements.txt
```

3. Inicie o servidor:
```bash
python app.py
```

---

## ✅ Verificar Deploy

### **Testar Endpoints**

Após o deploy, teste os endpoints:

```bash
# Health check
curl https://licence-api-zsbg.onrender.com/health

# Ping
curl https://licence-api-zsbg.onrender.com/ping

# Login (teste)
curl -X POST https://licence-api-zsbg.onrender.com/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📊 Dados no MySQL

Todos os dados já estão no MySQL:
- ✅ 1 usuário admin (`admin`)
- ✅ 1 usuário comum (`sergio`)
- ✅ 2 licenças ativas
- ✅ 74 logs de acesso

**Não é necessário migrar novamente!**

---

## 🎯 Próximos Passos

1. ✅ **GitHub**: Arquivos enviados
2. ⏳ **Render**: Configurar variáveis de ambiente e aguardar deploy
3. ⏳ **Koyeb**: Configurar variáveis de ambiente e aguardar deploy
4. ✅ **Local**: Configurar `.env` e iniciar servidor

---

## ⚠️ Importante

- **Não** crie as tabelas novamente (já estão criadas)
- **Não** migre os dados novamente (já estão migrados)
- **Apenas** configure as variáveis de ambiente nos servidores
- Todos os servidores usarão o **mesmo banco MySQL centralizado**

---

**Pronto para deploy!** 🚀

