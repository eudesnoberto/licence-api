# 📤 Comandos Git para Subir para GitHub

## 🚀 Comandos Rápidos

### **Se o repositório já existe no GitHub (vazio):**

```bash
# 1. Navegue até a pasta
cd C:\protecao

# 2. Inicialize Git (se ainda não foi feito)
git init

# 3. Adicione o repositório remoto
git remote add origin https://github.com/eudesnoberto/licence-api.git

# 4. Adicione todos os arquivos
git add .

# 5. Commit
git commit -m "Initial commit - API de licenciamento com redundância"

# 6. Push para GitHub
git push -u origin main
```

### **Se der erro "branch main não existe":**

```bash
# Crie a branch main
git branch -M main

# Depois faça push
git push -u origin main
```

### **Se já existe conteúdo no GitHub:**

```bash
# 1. Puxe o conteúdo existente
git pull origin main --allow-unrelated-histories

# 2. Resolva conflitos se houver
# 3. Adicione seus arquivos
git add .

# 4. Commit
git commit -m "Adiciona API de licenciamento"

# 5. Push
git push origin main
```

---

## 📁 Estrutura Recomendada no GitHub

```
licence-api/
├── .gitignore
├── README.md
├── requirements.txt
├── Procfile
├── runtime.txt
└── api/
    ├── app.py
    ├── config.py
    ├── db.py
    ├── license_service.py
    ├── email_service.py
    └── requirements.txt (opcional - pode ter versões específicas)
```

---

## ✅ Verificar se Funcionou

1. Acesse: https://github.com/eudesnoberto/licence-api
2. Verifique se os arquivos aparecem
3. Deve ver pasta `api/` com os arquivos Python

---

## 🔄 Atualizações Futuras

Para atualizar o repositório depois:

```bash
cd C:\protecao
git add .
git commit -m "Descrição da mudança"
git push origin main
```

---

**Pronto!** Agora você pode fazer deploy no Render! 🚀

