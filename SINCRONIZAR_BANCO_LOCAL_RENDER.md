# 🔄 Como Sincronizar Banco Local → Render

## 📋 Passo a Passo

### **Passo 1: Exportar Dados do Banco Local**

Execute o script de exportação:

```powershell
cd C:\protecao
python exportar_banco_local.py
```

Isso criará o arquivo `backup_banco_local.json` com todos os dados.

**O que é exportado:**
- ✅ Admin Users (usuários administradores)
- ✅ Users (usuários comuns/revendedores)
- ✅ Devices (todas as licenças)
- ✅ Blocked Devices (dispositivos bloqueados)

---

### **Passo 2: Importar para o Render**

Execute o script de importação:

```powershell
python importar_para_render.py
```

O script vai:
1. Pedir login (admin/admin123)
2. Importar usuários comuns
3. Importar licenças
4. Mostrar resumo

**⚠️ IMPORTANTE:**
- Usuários criados terão senha temporária: `TEMPORARIA123`
- Peça para cada usuário alterar a senha no primeiro acesso
- Admin users precisam ser criados manualmente (se houver outros além do padrão)

---

## 🔧 Requisitos

### **Instalar dependência (se necessário):**

```powershell
pip install requests
```

---

## 📝 O que cada script faz

### **`exportar_banco_local.py`**
- Conecta ao banco SQLite local
- Exporta todas as tabelas para JSON
- Cria arquivo `backup_banco_local.json`

### **`importar_para_render.py`**
- Carrega o backup JSON
- Faz login no Render
- Cria usuários via API
- Cria licenças via API
- Mostra progresso e resumo

---

## ⚠️ Limitações

### **O que NÃO pode ser importado automaticamente:**

1. **Admin Users adicionais**
   - A API não tem endpoint para criar admin_users
   - Solução: Criar manualmente no dashboard ou via SQL

2. **Dispositivos Bloqueados**
   - Precisa bloquear manualmente no dashboard
   - Ou usar endpoint de bloqueio (se existir)

3. **Histórico e Logs**
   - `access_logs` e `license_history` não são importados
   - São dados de auditoria, não críticos

---

## 🎯 Exemplo de Uso Completo

```powershell
# 1. Exportar do local
cd C:\protecao
python exportar_banco_local.py

# Saída esperada:
# ✅ Dados exportados com sucesso!
# 📁 Arquivo: C:\protecao\backup_banco_local.json
# 📊 Estatísticas:
#    - Admin Users: 2
#    - Usuários Comuns: 5
#    - Licenças: 15
#    - Dispositivos Bloqueados: 1

# 2. Importar para Render
python importar_para_render.py

# Digite:
# Usuário admin: admin
# Senha admin: admin123

# Saída esperada:
# ✅ Login realizado com sucesso!
# 📥 Importando Usuários Comuns...
#    ✅ Usuário 'usuario1' criado
#    ✅ Usuário 'usuario2' criado
# ...
# 📥 Importando Licenças...
#    ✅ Licença para 'abc123def456...' criada
# ...
# ✅ Importação concluída!
```

---

## 🔍 Verificar Importação

Após importar, verifique no dashboard do Render:

1. Acesse: `https://fartgreen.fun/#dashboard`
2. Faça login com `admin/admin123`
3. Verifique:
   - Usuários criados na seção "Gerenciar Usuários"
   - Licenças na tabela "Licenças registradas"

---

## 🐛 Resolução de Problemas

### **Erro: "Arquivo de backup não encontrado"**
- Execute primeiro `exportar_banco_local.py`
- Verifique se o arquivo `backup_banco_local.json` foi criado

### **Erro: "Erro de conexão"**
- Verifique se o Render está online
- Teste a URL: `https://licence-api-zsbg.onrender.com/health`
- Verifique sua conexão com internet

### **Erro: "Usuário já existe"**
- Normal! O script pula usuários/licenças que já existem
- Não é um problema, apenas informação

### **Usuários não aparecem**
- Verifique se o login foi bem-sucedido
- Verifique os logs do script
- Tente criar um usuário manualmente no dashboard para testar

---

## 📚 Próximos Passos

Após importar:

1. ✅ Verificar dados no dashboard
2. ✅ Testar login com usuários importados
3. ✅ Pedir para usuários alterarem senhas (TEMPORARIA123)
4. ✅ Bloquear dispositivos manualmente (se necessário)
5. ✅ Criar admin users adicionais (se necessário)

---

**Documento criado em**: 2024-12-15

