# 📦 API de Licenciamento - Sistema de Proteção

Sistema completo de proteção de licenças com suporte a:
- ✅ Verificação online/offline
- ✅ Redundância de servidores
- ✅ Detecção de clones
- ✅ Período de graça offline (7 dias)
- ✅ Dashboard de gerenciamento

## 🚀 Deploy Rápido

### **Railway.app:**
1. Conecte este repositório
2. Deploy automático!
3. Configure variáveis de ambiente

### **Render.com:**
1. New > Web Service
2. Conecte este repositório
3. Build: `pip install -r requirements.txt`
4. Start: `cd api && python app.py`

## 📁 Estrutura

```
api/
├── app.py              # Aplicação Flask principal
├── config.py           # Configurações
├── db.py              # Banco de dados SQLite
├── license_service.py # Serviço de licenças
└── email_service.py   # Serviço de emails
```

## ⚙️ Variáveis de Ambiente

```
FLASK_ENV=production
PORT=5000
DB_PATH=/data/license.db
API_KEY=sua_chave
SHARED_SECRET=seu_secret
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
```

## 📚 Documentação

Veja os guias na pasta raiz do projeto para mais informações.

