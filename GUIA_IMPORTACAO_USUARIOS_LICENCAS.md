# 📥 Guia de Importação: Usuários e Licenças para Render

## 📋 Situação Atual

### **Usuários no Banco Local:**
- ✅ **sergio** (role: user) - usuário comum
- ✅ **admin** (já existe no Render)

### **Licenças no Banco Local:**
1. **Licença 1** (Device: `2049365993desktop-j65uer12025112`)
   - Owner: Francieudes Silva N. Alves
   - `created_by`: `null` → Será atribuída ao **admin**
   - Admin verá esta licença

2. **Licença 2** (Device: `02592614b69110a201bf84c68d1c9247`)
   - Owner: Sergio Lucindo Santos
   - `created_by`: `sergio` → Será mantida como **sergio**
   - Apenas sergio verá esta licença

---

## 🚀 Passo a Passo para Importar

### **Passo 1: Verificar Backup**

O arquivo `backup_banco_local.json` já existe e contém:
- ✅ 1 usuário comum (sergio)
- ✅ 2 licenças (1 do admin, 1 do sergio)

### **Passo 2: Executar Importação**

```powershell
cd C:\protecao
python importar_para_render.py
```

**O script vai:**
1. ✅ Fazer login no Render (admin/Stage.7997)
2. ✅ Criar usuário "sergio" com senha temporária: `TEMPORARIA123`
3. ✅ Importar licença 1 com `created_by = 'admin'`
4. ✅ Importar licença 2 com `created_by = 'sergio'`
5. ✅ Se licenças já existirem, atualizar o campo `created_by`

### **Passo 3: Verificar Resultado**

Após a importação:

1. **Login como Admin:**
   - Verá **TODAS as 2 licenças**
   - Pode gerenciar todas

2. **Login como Sergio:**
   - Verá apenas **1 licença** (a que ele criou)
   - Não verá a licença do admin

---

## 🔐 Credenciais Após Importação

### **Admin:**
- Usuário: `admin`
- Senha: `Stage.7997` (ou a que você configurou)

### **Sergio:**
- Usuário: `sergio`
- Senha: `TEMPORARIA123` (temporária - deve alterar no primeiro acesso)

---

## ⚠️ Importante

### **Permissões:**

1. **Admin (`admin`):**
   - ✅ Vê **TODAS** as licenças
   - ✅ Pode criar, editar, desativar e excluir qualquer licença
   - ✅ Pode criar novos usuários

2. **Usuário Comum (`sergio`):**
   - ✅ Vê apenas licenças com `created_by = 'sergio'`
   - ✅ Pode criar novas licenças (serão atribuídas a ele)
   - ✅ Pode editar/desativar apenas suas próprias licenças
   - ❌ **NÃO** pode excluir licenças (apenas admin)
   - ❌ **NÃO** vê licenças de outros usuários

### **Campo `created_by`:**

- Se `created_by = null` → Atribuído ao `admin` (admin vê todas)
- Se `created_by = 'sergio'` → Mantido como `sergio` (sergio vê apenas as suas)
- Se `created_by = 'admin'` → Mantido como `admin` (admin vê todas)

---

## 🔄 Se Precisar Reimportar

Se algo der errado, você pode:

1. **Deletar licenças no Render** (via dashboard)
2. **Deletar usuário sergio** (se necessário)
3. **Executar importação novamente**

---

## 📊 Resumo da Importação

```
✅ Usuários: 1 (sergio)
✅ Licenças: 2
   - 1 para admin (created_by = 'admin')
   - 1 para sergio (created_by = 'sergio')
```

---

## 🎯 Resultado Esperado

Após importação bem-sucedida:

### **Dashboard do Admin:**
- Verá 2 licenças na tabela
- Coluna "Criado por" mostrará: `admin` e `sergio`

### **Dashboard do Sergio:**
- Verá apenas 1 licença na tabela
- A licença do admin não aparecerá

---

## ✅ Checklist Final

- [ ] Backup `backup_banco_local.json` existe
- [ ] Servidor Render está online
- [ ] Login admin funciona no Render
- [ ] Script de importação executado
- [ ] Usuário "sergio" criado
- [ ] 2 licenças importadas
- [ ] Campo `created_by` preservado corretamente
- [ ] Admin vê todas as licenças
- [ ] Sergio vê apenas sua licença

---

**Pronto para importar!** 🚀

Execute: `python importar_para_render.py`



