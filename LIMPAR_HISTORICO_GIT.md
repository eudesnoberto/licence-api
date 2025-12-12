# 🔒 Limpar Credenciais do Histórico do Git

## ⚠️ Problema

As credenciais foram commitadas no histórico do Git e estão visíveis no GitHub, mesmo após serem removidas dos arquivos atuais.

## 🎯 Solução

Existem duas abordagens:

### **Opção 1: Usar BFG Repo-Cleaner (Recomendado - Mais Rápido)**

1. **Baixar BFG:**
   - Acesse: https://rtyley.github.io/bfg-repo-cleaner/
   - Baixe o arquivo `bfg.jar`

2. **Criar arquivo com credenciais a remover:**
   ```bash
   # Criar arquivo passwords.txt
   echo "108.179.252.54" > passwords.txt
   echo "scpmtc84_api" >> passwords.txt
   echo "nQT-8gW%-qCY" >> passwords.txt
   ```

3. **Limpar histórico:**
   ```bash
   # Fazer backup do repositório
   git clone --mirror https://github.com/eudesnoberto/licence-api.git backup.git
   
   # Limpar histórico
   java -jar bfg.jar --replace-text passwords.txt licence-api.git
   
   # Limpar referências
   cd licence-api.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

### **Opção 2: Usar git filter-branch (Nativo do Git)**

```bash
# Remover credenciais do histórico
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch -r . && git reset --hard" \
  --prune-empty --tag-name-filter cat -- --all

# Limpar referências
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### **Opção 3: Recrear Repositório (Mais Simples)**

Se o histórico não for crítico:

1. **Fazer backup dos arquivos:**
   ```bash
   # Copiar todos os arquivos (exceto .git)
   cp -r . ../protecao-backup
   ```

2. **Deletar repositório no GitHub:**
   - GitHub → Settings → Danger Zone → Delete repository

3. **Criar novo repositório:**
   - Criar novo repositório no GitHub
   - Fazer commit inicial limpo

4. **Push forçado (CUIDADO):**
   ```bash
   git remote set-url origin https://github.com/eudesnoberto/licence-api.git
   git push -f origin main
   ```

## ⚠️ IMPORTANTE

Após limpar o histórico:

1. **Todos os colaboradores** precisam fazer:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

2. **Rotacionar credenciais** (mudar senha do MySQL)

3. **Verificar** se não há mais credenciais:
   ```bash
   git log --all -S "nQT-8gW%-qCY"
   ```

## 🔐 Prevenção Futura

1. **Usar .gitignore** para `.env`
2. **Usar variáveis de ambiente** sempre
3. **Nunca commitar** credenciais
4. **Usar git-secrets** para prevenir commits acidentais

---

**Nota**: A opção mais segura é **rotacionar as credenciais** (mudar senha) após limpar o histórico.



