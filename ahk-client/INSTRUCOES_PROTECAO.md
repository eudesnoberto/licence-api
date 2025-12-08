# 🛡️ Como Proteger Seu Script YouTube TV

## ✅ Proteção Implementada

Seu script `youtube_tv_protegido.ahk` já está protegido! Ele verifica a licença **antes** de executar qualquer código.

## 🔧 Como Funciona

1. **Script inicia** → Verifica licença no servidor
2. **Se licença válida** → Continua execução normal
3. **Se licença inválida/inexistente** → **Fecha o app** (ExitApp)

## 📋 Passos para Usar

### 1️⃣ Configure as Credenciais

Edite o arquivo `license_check.ahk` (linhas 7-9):

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "sua_api_key_aqui"
g_LicenseAPI_Secret := "seu_shared_secret_aqui"
```

**Use as mesmas credenciais do `api/.env`**

### 2️⃣ Compile o Script

1. Abra `youtube_tv_protegido.ahk` no AutoHotkey
2. Use **Ahk2Exe** para compilar em `.exe`
3. **Importante:** Certifique-se de que `license_check.ahk` está na mesma pasta OU compile tudo junto

### 3️⃣ Distribua para o Cliente

- Envie o `.exe` compilado
- Na primeira execução, o script cria um arquivo `device.id` na mesma pasta

### 4️⃣ Cadastre a Licença no Dashboard

1. **Acesse:** `http://localhost:5173` (ou seu domínio)
2. **Login:** `admin` / `admin123`
3. **Na seção "Cadastro Rápido":**
   - Cole o **Device ID** do computador
   - Escolha o tipo de licença (mensal, trimestral, semestral, anual, trienal)
   - Clique em "Criar Licença"

**Pronto!** O computador está liberado e o script funcionará normalmente.

---

## 🔍 Como Obter o Device ID

### Opção 1: Arquivo device.id
- O script cria automaticamente `device.id` na mesma pasta do `.exe`
- Peça ao cliente para enviar esse arquivo

### Opção 2: Mensagem de Erro
- Quando o cliente tentar executar sem licença, aparece uma mensagem com o Device ID
- O script fecha automaticamente após mostrar a mensagem

### Opção 3: Dashboard
- Veja os acessos recentes na tabela "Licenças registradas"
- O Device ID aparece na primeira coluna

---

## ⚠️ Comportamento

### ✅ Com Licença Válida
- Script verifica licença silenciosamente
- Se válida, continua execução normal
- Não mostra nenhuma mensagem

### ❌ Sem Licença ou Licença Inválida
- Script mostra mensagem: "Sua licença não é válida ou expirou"
- Exibe o Device ID na mensagem
- **Fecha o app automaticamente** (ExitApp)
- Cliente não consegue usar o programa

---

## 🔄 Verificação Periódica (Opcional)

Se quiser verificar a licença periodicamente durante a execução, adicione no final do seu código:

```autohotkey
; Verifica a cada 5 minutos
SetTimer, VerificarLicencaPeriodica, 300000

VerificarLicencaPeriodica:
    If (!License_Verify()) {
        deviceId := License_GetDeviceId()
        MsgBox, 16, Licença Expirada, Sua licença expirou.`n`nDevice ID: %deviceId%
        ExitApp
    }
return
```

---

## 📝 Checklist

- [ ] `license_check.ahk` configurado com credenciais corretas
- [ ] Script compilado com `#Include license_check.ahk`
- [ ] `license_check.ahk` na mesma pasta do executável (ou compilado junto)
- [ ] Backend rodando e acessível
- [ ] Device ID cadastrado no dashboard antes de distribuir

---

## 🐛 Troubleshooting

### Script fecha imediatamente
- **Causa:** Licença não cadastrada ou inválida
- **Solução:** Cadastre o Device ID no dashboard

### "Erro de conexão"
- **Causa:** Backend não está rodando ou URL incorreta
- **Solução:** Verifique se a API está acessível (`http://localhost:5000/health`)

### Device ID não aparece
- **Causa:** Script não tem permissão para criar arquivo
- **Solução:** Execute como administrador ou verifique permissões da pasta

---

**Pronto!** Seu script está protegido. Ele só funcionará em computadores com licença válida cadastrada no dashboard. 🎉





