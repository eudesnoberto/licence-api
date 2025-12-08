# Cliente AutoHotkey com Proteção de Licença

Este diretório contém os arquivos necessários para proteger seu script AutoHotkey com o sistema de licenciamento.

## 📋 Arquivos

- **`license_verify.ahk`** - Módulo de verificação de licença (não modifique)
- **`main_protegido.ahk`** - Exemplo de script protegido (use como base)
- **`config_license.ini`** - Configurações da API (edite com suas credenciais)

## 🚀 Como Usar

### 1. Configure as Credenciais

Edite o arquivo `license_verify.ahk` e altere estas linhas:

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "sua_api_key_aqui"
g_LicenseAPI_Secret := "seu_shared_secret_aqui"
```

**IMPORTANTE:** Use as mesmas credenciais configuradas no backend (`api/.env`)

### 2. Integre no Seu Script

Adicione estas linhas no **início** do seu script principal:

```autohotkey
#SingleInstance,Force

; Inclui o módulo de verificação
#Include license_verify.ahk

; Verifica licença antes de continuar
licenseResult := License_Verify()

If (!licenseResult.allow) {
    ; Bloqueia execução se não houver licença válida
    License_ShowError(licenseResult.msg . "`n`nDevice ID: " . licenseResult.deviceId)
    ExitApp
}

; Seu código original continua aqui...
```

### 3. Compile o Script

1. Abra seu script no AutoHotkey
2. Use **Ahk2Exe** para compilar em `.exe`
3. Distribua o `.exe` junto com o arquivo `license_verify.ahk` (se não compilou junto)

**OU** compile tudo junto incluindo o módulo.

## 🔧 Configuração do Backend

Antes de distribuir, certifique-se de:

1. **Criar licenças no dashboard:**
   - Acesse `http://localhost:5173` (ou seu domínio)
   - Faça login como admin
   - Crie uma nova licença
   - Anote o **Device ID** gerado

2. **Registrar Device IDs:**
   - Quando o cliente executar pela primeira vez, o script gera um `device.id`
   - Você precisa adicionar esse ID no dashboard
   - Ou ative `ALLOW_AUTO_PROVISION=true` no backend (menos seguro)

## 📝 Como Obter o Device ID

O Device ID é gerado automaticamente na primeira execução e salvo em:
- `device.id` (na mesma pasta do script)

Você pode:
1. Pedir ao cliente para enviar esse arquivo
2. Ou verificar no dashboard os acessos recentes

## ⚠️ Importante

- **Nunca distribua** o arquivo `license_verify.ahk` com as credenciais reais
- Use variáveis de ambiente ou compile as credenciais no EXE
- Mantenha `SHARED_SECRET` e `API_KEY` seguros
- Cada computador gera um Device ID único baseado no hardware

## 🐛 Troubleshooting

### Erro: "Erro de conexão"
- Verifique se a API está rodando
- Verifique se a URL está correta
- Verifique firewall/antivírus

### Erro: "ID não registrado"
- Adicione o Device ID no dashboard
- Ou ative auto-provisionamento no backend

### Erro: "Assinatura inválida"
- Verifique se `SHARED_SECRET` está igual no cliente e servidor
- Verifique se o relógio do sistema está correto

## 📞 Suporte

Para mais informações, consulte:
- `README.md` (raiz do projeto) - Guia completo do sistema
- Dashboard: `http://localhost:5173` - Gerenciar licenças





