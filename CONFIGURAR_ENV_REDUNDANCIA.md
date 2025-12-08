# 🔧 Configurar Redundância via .env

## 📋 Como Funciona

O sistema agora suporta configuração de servidores via arquivo `.env`, permitindo fácil configuração de redundância sem modificar o código.

---

## 🚀 Passo a Passo

### **Passo 1: Criar arquivo .env**

Na pasta `frontend/`, crie um arquivo chamado `.env`:

```bash
cd C:\protecao\frontend
```

Crie o arquivo `.env` com o seguinte conteúdo:

```env
# ============================================================================
# CONFIGURAÇÃO DE SERVIDORES COM REDUNDÂNCIA
# ============================================================================

# Servidor Principal
VITE_API_SERVER_PRIMARY=https://api.fartgreen.fun

# Servidor Backup 1 (Render)
VITE_API_SERVER_BACKUP1=https://licence-api-zsbg.onrender.com

# Servidor Backup 2 (Opcional - descomente se tiver)
# VITE_API_SERVER_BACKUP2=https://seu-servidor-backup2.com
```

### **Passo 2: Reiniciar o servidor de desenvolvimento**

Após criar/editar o `.env`, você precisa reiniciar o servidor Vite:

```powershell
# Parar o servidor (Ctrl+C)
# Depois iniciar novamente:
npm run dev
```

---

## 📝 Opções de Configuração

### **Opção 1: Servidores Individuais (Recomendado)**

```env
VITE_API_SERVER_PRIMARY=https://api.fartgreen.fun
VITE_API_SERVER_BACKUP1=https://licence-api-zsbg.onrender.com
VITE_API_SERVER_BACKUP2=https://seu-backup2.com
```

### **Opção 2: Lista Completa (Alternativa)**

```env
VITE_API_SERVERS=https://api.fartgreen.fun,https://licence-api-zsbg.onrender.com,https://seu-backup2.com
```

---

## ✅ Verificação

Após configurar, abra o console do navegador (F12) e você verá:

```
✅ Servidores carregados do .env: ['https://api.fartgreen.fun', 'https://licence-api-zsbg.onrender.com']
📡 Servidores API configurados: ['https://api.fartgreen.fun', 'https://licence-api-zsbg.onrender.com']
```

---

## 🔄 Ordem de Prioridade

O sistema tentará os servidores nesta ordem:

1. **Servidor Principal** (`VITE_API_SERVER_PRIMARY`)
2. **Backup 1** (`VITE_API_SERVER_BACKUP1`)
3. **Backup 2** (`VITE_API_SERVER_BACKUP2`) - se configurado

---

## ⚠️ Importante

1. **Arquivo `.env` não é versionado** (está no `.gitignore`)
2. **Reinicie o servidor** após alterar o `.env`
3. **Use `.env.example`** como template (já está criado)
4. **Valores padrão** serão usados se `.env` não existir

---

## 🎯 Valores Padrão (se .env não existir)

Se o arquivo `.env` não existir, o sistema usará:

```javascript
[
  'https://api.fartgreen.fun',                    // Servidor Principal
  'https://licence-api-zsbg.onrender.com',       // Backup 1 (Render)
]
```

---

## 📁 Estrutura de Arquivos

```
frontend/
├── .env              ← Crie este arquivo (não versionado)
├── .env.example      ← Template (já existe)
└── src/
    └── main.ts       ← Código que lê o .env
```

---

## 🔍 Troubleshooting

### **Servidores não estão sendo carregados do .env**

1. Verifique se o arquivo está em `frontend/.env` (não na raiz)
2. Reinicie o servidor Vite após criar/editar o `.env`
3. Verifique o console do navegador para ver quais servidores foram carregados

### **Erro: "Cannot find module"**

- Certifique-se de que o arquivo `.env` está na pasta `frontend/`
- Reinicie o servidor de desenvolvimento

---

**Pronto!** Agora você pode configurar a redundância facilmente via arquivo `.env`! 🚀

