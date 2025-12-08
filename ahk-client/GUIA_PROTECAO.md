# 🛡️ Guia de Proteção - AutoHotkey

## 📋 Passo a Passo para Proteger Seu Script

### 1️⃣ Configure as Credenciais

**Opção A: Editar diretamente no código (recomendado para compilação)**

Edite `license_verify.ahk` e altere as linhas 15-19:

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "SUA_API_KEY_AQUI"
g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"
```

**Opção B: Usar arquivo INI (mais flexível)**

Crie/edite `config_license.ini` na mesma pasta:

```ini
[License]
API_URL=https://api.fartgreen.fun
API_KEY=sua_api_key_aqui
SHARED_SECRET=seu_shared_secret_aqui
VERSION=1.0.0
TIMEOUT=10000
```

**⚠️ IMPORTANTE:** Use as mesmas credenciais do backend (`api/.env`)

### 2️⃣ Integre no Seu Script

Adicione estas linhas no **INÍCIO** do seu script (antes de qualquer outro código):

```autohotkey
#SingleInstance,Force

; Inclui o módulo de verificação
#Include license_verify.ahk

; Verifica licença ANTES de continuar
licenseResult := License_Verify()

If (!licenseResult.allow) {
    ; Bloqueia se não tiver licença válida
    License_ShowError(licenseResult.msg . "`n`nDevice ID: " . licenseResult.deviceId)
    ExitApp
}

; Seu código original continua aqui...
```

### 3️⃣ Compile o Script

1. Abra seu script no AutoHotkey
2. Use **Ahk2Exe** (ferramenta do AutoHotkey)
3. Compile em `.exe`
4. **Importante:** Se usar `#Include`, certifique-se de que o `license_verify.ahk` está na mesma pasta OU compile tudo junto

### 4️⃣ Configure Licenças no Dashboard

1. Inicie o backend: `.\iniciar-backend.ps1`
2. Inicie o dashboard: `.\iniciar-frontend.ps1`
3. Acesse: `http://localhost:5173`
4. Login: `admin` / `admin123`
5. Crie uma nova licença:
   - Preencha os dados do cliente
   - O **Device ID** será gerado automaticamente OU você pode usar um específico

### 5️⃣ Distribua o Script

- Distribua o `.exe` compilado
- Na primeira execução, o script gera um `device.id` único
- Você precisa adicionar esse ID no dashboard para liberar o acesso

## 🔍 Como Obter o Device ID do Cliente

### Método 1: Arquivo device.id

O script cria automaticamente um arquivo `device.id` na mesma pasta do executável. Peça ao cliente para enviar esse arquivo.

### Método 2: Dashboard

1. Acesse o dashboard
2. Vá em "Licenças"
3. Veja os acessos recentes - o Device ID aparece nos logs

### Método 3: Mensagem de Erro

Quando o cliente tentar executar sem licença, a mensagem de erro mostra o Device ID.

## ⚙️ Configurações Avançadas

### Modo Offline (Não Recomendado)

Se quiser permitir execução sem internet (menos seguro):

```autohotkey
licenseResult := License_Verify()

If (!licenseResult.allow) {
    If (licenseResult.offline) {
        ; Permite continuar em modo offline
        MsgBox, 48, Modo Offline, Sem conexão. Continuando em modo limitado.
    } Else {
        ; Bloqueia se for erro de licença
        License_ShowError(licenseResult.msg)
        ExitApp
    }
}
```

### Verificação Periódica

Para verificar a licença periodicamente durante a execução:

```autohotkey
; Verifica a cada 5 minutos
SetTimer, VerificarLicenca, 300000

VerificarLicenca:
    licenseResult := License_Verify()
    If (!licenseResult.allow) {
        License_ShowError(licenseResult.msg)
        ExitApp
    }
return
```

## 🐛 Troubleshooting

### Erro: "Erro de conexão"
- ✅ Verifique se a API está rodando (`http://localhost:5000/health`)
- ✅ Verifique se a URL está correta
- ✅ Verifique firewall/antivírus

### Erro: "ID não registrado"
- ✅ Adicione o Device ID no dashboard
- ✅ Ou ative `ALLOW_AUTO_PROVISION=true` no backend (menos seguro)

### Erro: "Assinatura inválida"
- ✅ Verifique se `SHARED_SECRET` está igual no cliente e servidor
- ✅ Verifique se o relógio do sistema está correto

### Erro: "API key inválida"
- ✅ Verifique se `API_KEY` está igual no cliente e servidor

## 📝 Checklist de Segurança

- [ ] Credenciais (`API_KEY` e `SHARED_SECRET`) estão configuradas corretamente
- [ ] Credenciais estão iguais no cliente e servidor
- [ ] Script compilado não expõe as credenciais (use variáveis ou compile tudo)
- [ ] Licenças criadas no dashboard antes de distribuir
- [ ] Device IDs registrados para cada cliente
- [ ] Backend rodando e acessível (local ou produção)

## 🚀 Produção

Para usar em produção:

1. **Configure o backend em produção:**
   - Use Cloudflare Tunnel ou servidor com IP fixo
   - Configure `api.fartgreen.fun` (ou seu domínio)

2. **Atualize a URL no cliente:**
   ```autohotkey
   g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
   ```

3. **Distribua o script compilado**

4. **Gerencie licenças pelo dashboard**

---

**Pronto!** Seu script AutoHotkey agora está protegido com o sistema de licenciamento. 🎉





