# 🚀 Guia: Hospedagem Gratuita e Redundância de Servidores

## 📋 Opções de Hospedagem Gratuita para API Python/Flask

### 1. **Railway.app** ⭐ RECOMENDADO
- ✅ **Gratuito**: $5 de crédito grátis por mês
- ✅ **Fácil deploy**: Conecta com GitHub
- ✅ **Banco SQLite**: Suporta nativamente
- ✅ **Domínio**: Subdomínio `.railway.app` grátis
- ✅ **SSL**: HTTPS automático
- ✅ **Sem cartão**: Não precisa de cartão de crédito inicialmente

**Como usar:**
1. Acesse: https://railway.app
2. Conecte com GitHub
3. Crie novo projeto
4. Deploy do repositório
5. Configure variáveis de ambiente
6. Deploy automático!

---

### 2. **Render.com** ⭐ RECOMENDADO
- ✅ **Gratuito**: Plano free tier disponível
- ✅ **Auto-deploy**: De GitHub
- ✅ **SSL**: HTTPS automático
- ✅ **Banco**: PostgreSQL gratuito (ou SQLite)
- ✅ **Limite**: Pode "dormir" após 15min de inatividade

**Como usar:**
1. Acesse: https://render.com
2. Conecte com GitHub
3. New > Web Service
4. Selecione repositório
5. Configure build/start commands
6. Deploy!

---

### 3. **Fly.io**
- ✅ **Gratuito**: 3 VMs compartilhadas grátis
- ✅ **Global**: Deploy em múltiplas regiões
- ✅ **Performance**: Muito rápido
- ✅ **Docker**: Suporta containers

**Como usar:**
1. Acesse: https://fly.io
2. Instale CLI: `curl -L https://fly.io/install.sh | sh`
3. `fly launch`
4. Deploy!

---

### 4. **PythonAnywhere**
- ✅ **Gratuito**: Plano Beginner grátis
- ✅ **Python**: Ambiente Python nativo
- ✅ **Limite**: 1 app web, 512MB storage
- ✅ **Domínio**: `.pythonanywhere.com`

**Como usar:**
1. Acesse: https://www.pythonanywhere.com
2. Crie conta gratuita
3. Upload arquivos via web interface
4. Configure web app
5. Deploy!

---

### 5. **Replit**
- ✅ **Gratuito**: Plano Hacker grátis
- ✅ **Editor online**: Desenvolva direto no navegador
- ✅ **Deploy**: Um clique
- ✅ **Banco**: SQLite ou PostgreSQL

**Como usar:**
1. Acesse: https://replit.com
2. Importe repositório GitHub
3. Configure run command
4. Deploy!

---

## 🔄 Sistema de Redundância (Múltiplos Servidores)

### Como Funciona

O cliente AHK tentará conectar em **ordem de prioridade**:
1. **Servidor Principal**: Tenta primeiro
2. **Servidor Backup 1**: Se principal falhar
3. **Servidor Backup 2**: Se backup 1 falhar
4. **Modo Offline**: Se todos falharem (usa token salvo)

### Vantagens

- ✅ **Alta Disponibilidade**: Se um servidor cair, outro assume
- ✅ **Distribuição de Carga**: Reduz sobrecarga em um único servidor
- ✅ **Resiliência**: Sistema continua funcionando mesmo com falhas
- ✅ **Offline**: Funciona mesmo se todos os servidores estiverem offline (período de graça)

---

## 📝 Configuração no Cliente AHK

### Antes (Servidor Único):
```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
```

### Depois (Múltiplos Servidores):
```autohotkey
; Array de servidores (em ordem de prioridade)
g_LicenseAPI_Servers := [
    "https://api1.fartgreen.fun",    ; Servidor Principal
    "https://api2.fartgreen.fun",    ; Backup 1
    "https://api3.fartgreen.fun"     ; Backup 2
]
```

---

## 🛠️ Implementação da Redundância

O sistema será atualizado para:
1. Tentar servidor principal primeiro
2. Se falhar, tentar backup 1
3. Se falhar, tentar backup 2
4. Se todos falharem, usar modo offline

---

## 📊 Comparação de Serviços

| Serviço | Gratuito | SQLite | HTTPS | Deploy Fácil | Limite |
|---------|----------|--------|-------|--------------|--------|
| Railway | ✅ $5/mês | ✅ | ✅ | ⭐⭐⭐⭐⭐ | Médio |
| Render | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ | Dorme após 15min |
| Fly.io | ✅ | ✅ | ✅ | ⭐⭐⭐ | 3 VMs |
| PythonAnywhere | ✅ | ✅ | ✅ | ⭐⭐⭐ | 1 app |
| Replit | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | Médio |

---

## 🎯 Recomendação

**Para começar:**
1. **Railway.app** - Mais fácil e confiável
2. **Render.com** - Boa alternativa

**Para redundância:**
- Use **Railway** como servidor principal
- Use **Render** como backup 1
- Use **Fly.io** como backup 2 (opcional)

---

## 📚 Próximos Passos

1. Escolha um serviço de hospedagem
2. Faça deploy da API
3. Configure múltiplos servidores
4. Atualize o cliente AHK com suporte a redundância

---

**Documento criado em**: 2024-12-15

