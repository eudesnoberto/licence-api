# 🔄 Guia: Redundância de Banco de Dados

## 📋 Visão Geral

Este sistema sincroniza o banco de dados entre o servidor principal e o servidor de backup, garantindo que ambos tenham os mesmos dados.

## 🎯 Objetivo

- **Redundância**: Dados disponíveis em ambos os servidores
- **Backup automático**: Dados do principal são copiados para o backup
- **Recuperação**: Se um servidor cair, o outro tem os dados atualizados

---

## 📁 Arquivos Criados

### **1. `sincronizar_bancos.py`**
Script principal de sincronização:
- Busca dados do servidor principal
- Sincroniza para o servidor backup
- Cria/atualiza usuários e licenças

### **2. `sincronizar_automatico.py`**
Wrapper para execução automática:
- Pode ser chamado por cron/task scheduler
- Trata timeouts e erros

### **3. `AGENDAR_SINCRONIZACAO.ps1`**
Script PowerShell para agendar execução automática:
- Cria tarefa agendada no Windows
- Executa a cada 1 hora

---

## 🚀 Como Usar

### **Opção 1: Sincronização Manual**

Execute quando quiser sincronizar:

```powershell
python sincronizar_bancos.py
```

### **Opção 2: Sincronização Automática (Windows)**

1. Abra PowerShell como **Administrador**
2. Execute:

```powershell
cd C:\protecao
.\AGENDAR_SINCRONIZACAO.ps1
```

Isso criará uma tarefa que executa a cada 1 hora.

### **Opção 3: Sincronização Automática (Linux/Mac)**

Adicione ao crontab:

```bash
# Sincronizar a cada hora
0 * * * * /usr/bin/python3 /caminho/para/sincronizar_automatico.py >> /var/log/sync_db.log 2>&1
```

---

## ⚙️ Configuração

Edite `sincronizar_bancos.py` para ajustar:

```python
# Servidores
SERVIDOR_PRINCIPAL = "https://api.fartgreen.fun"
SERVIDOR_BACKUP = "https://licence-api-zsbg.onrender.com"

# Credenciais
ADMIN_USER = "admin"
ADMIN_PASSWORD = "Stage.7997"
```

---

## 🔍 O que é Sincronizado

### **Usuários**
- ✅ Cria usuários que não existem no backup
- ✅ Mantém usuários existentes
- ⚠️  Senhas são resetadas para `TEMPORARIA123` (usuários devem alterar)

### **Licenças**
- ✅ Cria licenças que não existem no backup
- ✅ Atualiza licenças existentes (se dados mudaram)
- ✅ Preserva `created_by` quando possível

---

## ⚠️ Limitações

1. **Senhas de usuários**: Não são sincronizadas (resetadas para `TEMPORARIA123`)
2. **Histórico**: Logs e histórico não são sincronizados
3. **Concorrência**: Se ambos servidores receberem atualizações simultâneas, pode haver conflitos
4. **Direção**: Por padrão, sincroniza apenas Principal → Backup

---

## 🔄 Fluxo de Sincronização

```
1. Login no servidor principal
2. Buscar todos os usuários e licenças
3. Login no servidor backup
4. Buscar dados existentes no backup
5. Comparar e sincronizar:
   - Criar usuários/licenças que não existem
   - Atualizar licenças que mudaram
6. Relatório de sincronização
```

---

## 📊 Exemplo de Saída

```
============================================================
🔄 SISTEMA DE SINCRONIZAÇÃO DE BANCO DE DADOS
============================================================
Principal: https://api.fartgreen.fun
Backup: https://licence-api-zsbg.onrender.com
============================================================

🔄 Sincronizando banco de dados: Principal → Backup

🔐 Fazendo login nos servidores...
   Principal: https://api.fartgreen.fun
   Backup: https://licence-api-zsbg.onrender.com
✅ Login realizado em ambos os servidores!

📥 Buscando dados do servidor principal...
   ✅ 2 usuários encontrados
   ✅ 5 licenças encontradas

📥 Buscando dados do servidor backup...
   ✅ 1 usuários encontrados
   ✅ 2 licenças encontradas

👥 Sincronizando usuários...
   ✅ 2/2 usuários sincronizados

📋 Sincronizando licenças...
   ✅ 5/5 licenças sincronizadas

============================================================
✅ Sincronização concluída!
============================================================
```

---

## 🛠️ Manutenção

### **Verificar Tarefa Agendada (Windows)**

```powershell
Get-ScheduledTask -TaskName SincronizarBancosAPI
```

### **Ver Logs da Última Execução**

```powershell
Get-ScheduledTask -TaskName SincronizarBancosAPI | Get-ScheduledTaskInfo
```

### **Remover Tarefa Agendada**

```powershell
Unregister-ScheduledTask -TaskName SincronizarBancosAPI -Confirm:$false
```

---

## 🔧 Troubleshooting

### **Erro: "Não foi possível fazer login"**
- Verifique se as credenciais estão corretas
- Verifique se os servidores estão online
- Render pode estar "dormindo" (aguarde alguns segundos)

### **Erro: "Timeout"**
- Aumente o timeout no script
- Verifique conexão com internet
- Servidor pode estar lento

### **Usuários não sincronizados**
- Verifique se o endpoint `/admin/users/create` está funcionando
- Verifique permissões do token

### **Licenças não sincronizadas**
- Verifique se o endpoint `/admin/devices/create` está funcionando
- Verifique se `created_by` está sendo preservado

---

## 📝 Próximas Melhorias

- [ ] Sincronização bidirecional
- [ ] Detecção de conflitos
- [ ] Sincronização incremental (apenas mudanças)
- [ ] Sincronização de senhas (criptografadas)
- [ ] Sincronização de histórico e logs
- [ ] Interface web para monitoramento

---

**Documento criado em**: 2024-12-15



