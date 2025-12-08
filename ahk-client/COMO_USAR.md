# 🚀 Como Proteger Seu botãoA.exe

## ✅ Solução Rápida (3 passos)

### 1️⃣ Adicione proteção no seu script AHK

No **início** do seu script original, adicione apenas estas 2 linhas:

```autohotkey
#SingleInstance,Force

; Adicione esta linha
#Include license_check.ahk

; Seu código original continua aqui (sem mudanças)
#Include performace.ahk
IniRead, leter, %A_WorkingDir%\config.ini, Teclas, youtube
; ... resto do seu código ...
```

### 2️⃣ Configure as credenciais

Edite `license_check.ahk` (linhas 7-9) e altere:

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "sua_api_key_aqui"
g_LicenseAPI_Secret := "seu_shared_secret_aqui"
```

**Use as mesmas credenciais do `api/.env`**

### 3️⃣ Compile e distribua

- Compile seu script com Ahk2Exe
- Distribua o `.exe` para os clientes
- Na primeira execução, o script cria um arquivo `device.id`

---

## 📋 Cadastrar Licenças no Dashboard

### Método Rápido (Recomendado)

1. **Acesse o dashboard:** `http://localhost:5173`
2. **Faça login:** `admin` / `admin123`
3. **Na seção "Cadastro Rápido":**
   - Cole o Device ID do computador
   - Escolha o tipo de licença (mensal, trimestral, semestral, anual, trienal)
   - Clique em "Criar Licença"

**Pronto!** O computador já está liberado.

### Como obter o Device ID?

**Opção 1:** Peça ao cliente para enviar o arquivo `device.id` (criado na mesma pasta do .exe)

**Opção 2:** Quando o cliente tentar executar sem licença, a mensagem mostra o Device ID

**Opção 3:** Veja no dashboard na tabela de "Licenças registradas" (aparece nos acessos)

---

## 💰 Cards de Preços

O dashboard agora tem cards visuais para:
- **Mensal** - R$ 50/mês
- **Trimestral** - R$ 135/3 meses (10% off)
- **Semestral** - R$ 240/6 meses (20% off)
- **Anual** - R$ 450/ano (mais popular)
- **Trienal** - R$ 1.200/3 anos (melhor valor)

Clique em qualquer card para selecionar o plano no formulário rápido.

---

## 🔧 Fluxo Completo

1. **Você distribui** o `botaoA.exe` protegido
2. **Cliente executa** → script gera `device.id` único
3. **Cliente tenta usar** → bloqueia e mostra Device ID
4. **Cliente envia** o Device ID para você
5. **Você cadastra** no dashboard (cadastro rápido)
6. **Cliente executa novamente** → funciona! ✅

---

## ⚠️ Importante

- **Não modifique** seu código original além de adicionar `#Include license_check.ahk`
- **Mantenha** `license_check.ahk` na mesma pasta do script OU compile tudo junto
- **Use as mesmas credenciais** no cliente e no servidor
- **Cadastre os Device IDs** antes de distribuir (ou use auto-provisionamento)

---

## 🐛 Problemas?

### "Licença inválida" mesmo após cadastrar
- Verifique se o Device ID está correto (sem espaços)
- Verifique se a licença está com status "active" no dashboard
- Verifique se a data de expiração está correta

### "Erro de conexão"
- Verifique se o backend está rodando
- Verifique se a URL está correta (`https://api.fartgreen.fun` ou `http://localhost:5000`)

### Device ID não aparece
- O arquivo `device.id` é criado na primeira execução
- Verifique se o script tem permissão para escrever arquivos

---

**Pronto!** Seu sistema está protegido e você pode gerenciar tudo pelo dashboard. 🎉

