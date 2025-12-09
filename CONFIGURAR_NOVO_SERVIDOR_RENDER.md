# 🚀 Configurar Novo Serviço no Render

## 📋 Passo a Passo

### **1. Criar Novo Web Service**

1. Acesse: https://dashboard.render.com
2. Clique em **New +** → **Web Service**
3. Conecte ao repositório: `eudesnoberto/licence-api`
4. Branch: `main`

---

### **2. Configurações Básicas**

- **Name**: `licence-api` (ou o nome que preferir)
- **Region**: Escolha a região mais próxima
- **Branch**: `main`
- **Root Directory**: Deixe vazio (raiz do repositório)

---

### **3. Configurações de Build e Deploy**

#### **Build Command:**
```bash
pip install -r api/requirements.txt
```

#### **Start Command:**
```bash
cd api && python app.py
```

**OU** (se o Render não encontrar o diretório `api`):

```bash
python api/app.py
```

---

### **4. Configurações de Ambiente**

#### **Python Version:**
- **Python Version**: `3.11.0` (ou a versão que você preferir)

---

### **5. Variáveis de Ambiente**

Adicione as seguintes variáveis de ambiente:

```env
DB_TYPE=mysql
# ⚠️ IMPORTANTE: Substitua pelos valores reais do seu banco MySQL
MYSQL_HOST=SEU_HOST_AQUI
MYSQL_PORT=3306
MYSQL_DATABASE=SEU_DATABASE_AQUI
MYSQL_USER=SEU_USUARIO_AQUI
MYSQL_PASSWORD=SUA_SENHA_AQUI
```

**Como adicionar:**
1. Role até **Environment Variables**
2. Clique em **Add Environment Variable**
3. Adicione cada variável uma por uma
4. Clique em **Save Changes**

---

### **6. Configurações Avançadas (Opcional)**

#### **Auto-Deploy:**
- ✅ **Auto-Deploy**: Habilitado (deploy automático a cada push)

#### **Health Check Path:**
- **Health Check Path**: `/health` (opcional, mas recomendado)

---

### **7. Deploy**

1. Clique em **Create Web Service**
2. O Render começará a fazer build automaticamente
3. Aguarde o deploy completar
4. Verifique os logs para confirmar que está funcionando

---

## 🔍 Verificar Estrutura do Projeto

O projeto tem a seguinte estrutura:

```
licence-api/
├── api/
│   ├── app.py          ← Arquivo principal
│   ├── requirements.txt ← Dependências
│   ├── config.py
│   ├── db.py
│   └── ...
├── frontend/
├── render.yaml         ← Configuração Render (se usar)
└── README.md
```

**Importante**: O arquivo `app.py` está dentro da pasta `api/`, por isso o comando precisa ser `cd api && python app.py`

---

## ⚠️ Se o Erro "No such file or directory" Persistir

### **Solução 1: Usar caminho relativo**

Mude o **Start Command** para:

```bash
python api/app.py
```

### **Solução 2: Verificar Root Directory**

1. Vá em **Settings** → **Service Settings**
2. Verifique o campo **Root Directory**
3. Deve estar **vazio** (raiz do repositório)
4. Se estiver preenchido, limpe e salve

### **Solução 3: Usar render.yaml**

Se você adicionou o arquivo `render.yaml` ao repositório, o Render pode usar essas configurações automaticamente.

---

## ✅ Checklist de Configuração

- [ ] Repositório: `eudesnoberto/licence-api`
- [ ] Branch: `main`
- [ ] Build Command: `pip install -r api/requirements.txt`
- [ ] Start Command: `cd api && python app.py` (ou `python api/app.py`)
- [ ] Python Version: `3.11.0` (ou similar)
- [ ] Variáveis de ambiente MySQL configuradas (6 variáveis)
- [ ] Auto-Deploy habilitado

---

## 🧪 Testar Após Deploy

Após o deploy completar, teste os endpoints:

```bash
# Health check
curl https://seu-servico.onrender.com/health

# Ping
curl https://seu-servico.onrender.com/ping
```

---

## 📝 Notas Importantes

1. **Primeiro deploy pode demorar** - O Render precisa instalar todas as dependências
2. **Servidor pode "dormir"** - Serviços gratuitos ficam inativos após 15 minutos sem requisições
3. **Logs são importantes** - Sempre verifique os logs se houver problemas

---

**Pronto!** Após configurar tudo, o Render fará o deploy automaticamente. 🚀

