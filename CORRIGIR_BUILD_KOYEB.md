# 🔧 Corrigir Erro de Build no Koyeb

## ❌ Erro Atual

```
[INFO] Running custom build command: 'pip install -r api/requirements.txt'
bash: line 1: pip: command not found
ERROR: failed to build: exit status 127
```

## 🔍 Causa

O Koyeb está tentando executar um **comando de build customizado** após o buildpack já ter instalado as dependências. Nesse ponto, o ambiente não tem `pip` disponível.

## ✅ Solução

### **Opção 1: Usar Docker (Recomendado)**

1. **No Dashboard do Koyeb:**
   - Vá em **Settings** → **Build & Deploy**
   - Em **Build Method**, selecione **"Docker"**
   - **Remova qualquer Build Command customizado** (deixe vazio)
   - Salve

2. **O `koyeb.toml` já está configurado:**
   ```toml
   [build]
   builder = "docker"
   ```

3. **Faça push:**
   ```bash
   git add Dockerfile koyeb.toml .python-version
   git commit -m "fix: Configurar Docker para Koyeb"
   git push
   ```

---

### **Opção 2: Usar Buildpack SEM Build Command Customizado**

1. **No Dashboard do Koyeb:**
   - Vá em **Settings** → **Build & Deploy**
   - Em **Build Method**, selecione **"Buildpack"** ou **"Automatic"**
   - **IMPORTANTE**: Remova qualquer **Build Command** customizado
   - Deixe o campo **Build Command** **VAZIO**
   - O buildpack detectará automaticamente e instalará as dependências

2. **O `Procfile` já está correto:**
   ```
   web: cd api && python app.py
   ```

3. **O `.python-version` foi criado:**
   ```
   3.11
   ```

4. **Faça push:**
   ```bash
   git add .python-version
   git commit -m "fix: Adicionar .python-version para buildpack"
   git push
   ```

---

## 📋 Checklist

- [ ] **Remover Build Command customizado** no dashboard do Koyeb
- [ ] Escolher: Docker OU Buildpack (sem build command)
- [ ] `.python-version` criado (para buildpack)
- [ ] `Dockerfile` criado (para Docker)
- [ ] `koyeb.toml` configurado
- [ ] Push feito para GitHub

---

## 🎯 Recomendação

**Use Docker** (Opção 1) porque:
- ✅ Mais controle sobre o ambiente
- ✅ Não depende de buildpacks
- ✅ Mais fácil de debugar
- ✅ Funciona sempre

---

## ⚠️ Importante

**NÃO configure um Build Command customizado** no dashboard do Koyeb quando usar buildpack. O buildpack já instala as dependências automaticamente. Um build command customizado só causa problemas.

---

**Após corrigir, o build deve funcionar!** 🚀



