# 🔧 Solução: Erro de Build no Koyeb (Exit Code 51)

## ❌ Problema

O Koyeb está falhando no build com:
```
The "build" step of buildpacks failed with exit code 51
```

Isso acontece quando o Koyeb tenta usar **buildpacks automáticos** (nixpacks) mas não consegue detectar corretamente a estrutura da aplicação Python.

---

## ✅ Soluções

### **Solução 1: Usar Dockerfile (Recomendado)**

O Koyeb agora tem um `Dockerfile` na raiz do projeto. Configure o Koyeb para usar Docker:

1. **No Dashboard do Koyeb:**
   - Vá em **Settings** → **Build & Deploy**
   - Em **Build Method**, selecione **"Docker"** (não "Automatic" ou "Nixpacks")
   - Salve

2. **OU** use o `koyeb.toml` atualizado:
   ```toml
   [build]
   builder = "docker"
   ```

3. **Faça push do Dockerfile:**
   ```bash
   git add Dockerfile koyeb.toml
   git commit -m "fix: Adicionar Dockerfile para Koyeb"
   git push
   ```

---

### **Solução 2: Ajustar Buildpacks (Alternativa)**

Se preferir usar buildpacks, ajuste o `koyeb.toml`:

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r api/requirements.txt"

[run]
command = "cd api && python app.py"
```

E certifique-se de que o Koyeb detecta Python corretamente.

---

### **Solução 3: Usar Python Buildpack Explicitamente**

No dashboard do Koyeb:

1. **Settings** → **Build & Deploy**
2. **Build Command**: `pip install -r api/requirements.txt`
3. **Run Command**: `cd api && python app.py`
4. **Buildpack**: Selecione **"Python"** explicitamente

---

## 🔍 Verificar Estrutura do Projeto

O Koyeb precisa encontrar:
- ✅ `api/requirements.txt` (existe)
- ✅ `api/app.py` (existe)
- ✅ `Dockerfile` (agora existe na raiz)

---

## 📝 Checklist

- [ ] Dockerfile criado na raiz
- [ ] `koyeb.toml` atualizado com `builder = "docker"`
- [ ] Build Method no Koyeb configurado para "Docker"
- [ ] Variáveis de ambiente configuradas (MySQL)
- [ ] Push feito para GitHub

---

## 🚀 Após Configurar

1. O Koyeb fará deploy automático
2. Verifique os logs para confirmar que está funcionando
3. Teste o endpoint `/ping` ou `/health`

---

## ⚠️ Nota Importante

O `Dockerfile` está configurado para:
- Usar Python 3.11
- Instalar dependências do `requirements.txt`
- Copiar código de `api/`
- Iniciar com `python app.py`

Se o `app.py` usar uma porta específica, o Koyeb injeta a variável `PORT` automaticamente. Verifique se o `app.py` está configurado para usar `os.environ.get('PORT', 8000)`.

---

**Pronto!** Após configurar o Docker, o build deve funcionar. 🎯

