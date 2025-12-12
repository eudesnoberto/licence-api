# 🚨 SOLUÇÃO RÁPIDA: Remover Credenciais do Histórico Git

## ⚠️ URGENTE

As credenciais estão expostas no histórico do Git no GitHub. Siga estes passos:

---

## 🔧 Solução Rápida (5 minutos)

### **Passo 1: Fazer Backup**

```powershell
# Criar backup completo
cd C:\protecao
Copy-Item -Path . -Destination ..\protecao-backup-completo -Recurse
```

### **Passo 2: Limpar Histórico Local**

```powershell
# Executar script de limpeza
.\LIMPAR_CREDENCIAIS_GIT.ps1
```

**OU manualmente:**

```bash
# Remover credenciais do histórico
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch -r ." --prune-empty --tag-name-filter cat -- --all

# Limpar referências
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### **Passo 3: Push Forçado (CUIDADO!)**

```bash
# ⚠️ Isso irá reescrever o histórico no GitHub
git push -f origin main
```

### **Passo 4: ROTACIONAR CREDENCIAIS (OBRIGATÓRIO!)**

**Mude a senha do MySQL no HostGator AGORA:**
1. Acesse cPanel do HostGator
2. Vá em "MySQL Databases"
3. Altere a senha do usuário `scpmtc84_api`
4. Atualize as variáveis de ambiente em:
   - Render
   - Koyeb
   - Servidor local (se aplicável)

---

## 🎯 Solução Alternativa (Mais Segura)

Se não quiser mexer no histórico, **ROTACIONAR as credenciais** é suficiente:

1. **Mude a senha do MySQL** (mais importante!)
2. **Atualize variáveis de ambiente** nos servidores
3. As credenciais antigas no histórico ficarão inválidas

---

## ✅ Verificar se Funcionou

```bash
# Verificar se ainda há credenciais no histórico
git log --all -S "nQT-8gW%-qCY"
git log --all -S "108.179.252.54"
```

Se não retornar nada, está limpo!

---

## 📋 Checklist

- [ ] Backup criado
- [ ] Histórico limpo localmente
- [ ] Push forçado feito
- [ ] **SENHA DO MYSQL ALTERADA** (CRÍTICO!)
- [ ] Variáveis de ambiente atualizadas nos servidores
- [ ] Testado que aplicação ainda funciona

---

**IMPORTANTE**: Mesmo limpando o histórico, **ROTACIONAR as credenciais é obrigatório** porque elas já foram expostas!



