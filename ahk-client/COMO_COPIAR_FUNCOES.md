# Como Copiar as Funções de Licenciamento

Este guia mostra exatamente quais linhas copiar do arquivo `youtube_tv_standalone.ahk`.

## 📋 Funções Necessárias

Você precisa copiar **3 funções** do arquivo original:

### 1. `License_GetDeviceId()` 
**Localização:** Aproximadamente linhas 23-100

**O que faz:** Gera ou recupera o Device ID único do computador.

### 2. `License_SHA256(text)`
**Localização:** Aproximadamente linhas 102-180

**O que faz:** Calcula o hash SHA256 de uma string (usado para assinatura criptográfica).

### 3. `License_Verify()`
**Localização:** Aproximadamente linhas 209-431

**O que faz:** Verifica a licença no servidor e retorna `true` se válida, `false` se inválida.

---

## 🔍 Como Encontrar as Funções

### Método 1: Buscar no Editor

1. Abra o arquivo `youtube_tv_standalone.ahk` no seu editor
2. Use Ctrl+F para buscar:
   - `License_GetDeviceId()`
   - `License_SHA256(`
   - `License_Verify()`

### Método 2: Visual

As funções começam com:
```autohotkey
License_GetDeviceId() {
    ; código aqui
}
```

E terminam com:
```autohotkey
    return valor
}
```

---

## 📝 Passo a Passo para Copiar

### Passo 1: Abrir o Arquivo Original

Abra: `C:\protecao\ahk-client\youtube_tv_standalone.ahk`

### Passo 2: Copiar `License_GetDeviceId()`

1. Procure por `License_GetDeviceId() {`
2. Selecione desde essa linha até o `}` correspondente
3. Copie (Ctrl+C)

**Dica:** A função termina quando você encontra `return deviceId` seguido de `}`

### Passo 3: Copiar `License_SHA256()`

1. Procure por `License_SHA256(text) {`
2. Selecione desde essa linha até o `}` correspondente
3. Copie (Ctrl+C)

**Dica:** A função termina quando você encontra `return hash` seguido de `}`

### Passo 4: Copiar `License_Verify()`

1. Procure por `License_Verify() {`
2. Selecione desde essa linha até o `}` correspondente
3. Copie (Ctrl+C)

**Dica:** A função termina quando você encontra `return false` ou `return true` seguido de `}`

### Passo 5: Colar no Seu Script

1. Abra seu script
2. Cole as 3 funções (Ctrl+V)
3. Certifique-se de que estão ANTES do código de verificação

---

## ✅ Estrutura Final do Seu Script

Seu script deve ter esta estrutura:

```autohotkey
; ============================================================================
; CONFIGURAÇÃO
; ============================================================================
global g_LicenseAPI_BaseURL := "..."
global g_LicenseAPI_Key := "..."
; ... outras variáveis

; ============================================================================
; FUNÇÕES DE LICENCIAMENTO (COPIADAS AQUI)
; ============================================================================
License_GetDeviceId() {
    ; ... código copiado
}

License_SHA256(text) {
    ; ... código copiado
}

License_Verify() {
    ; ... código copiado
}

; ============================================================================
; VERIFICAÇÃO DE LICENÇA
; ============================================================================
deviceId := License_GetDeviceId()
isValid := License_Verify()
If (!isValid) {
    ; ... código de erro
    ExitApp
}

; ============================================================================
; SEU CÓDIGO ORIGINAL
; ============================================================================
; ... resto do seu script
```

---

## ⚠️ Erros Comuns

### Erro: "Function not found"

**Causa:** Função não foi copiada ou está em local errado

**Solução:** 
- Verifique se todas as 3 funções foram copiadas
- Certifique-se de que estão ANTES de serem chamadas

### Erro: "Variable not found"

**Causa:** Variáveis globais não foram definidas

**Solução:**
- Verifique se todas as variáveis `g_LicenseAPI_*` foram definidas
- Certifique-se de que estão no início do script

### Erro: "Missing closing brace"

**Causa:** Função não foi copiada completamente

**Solução:**
- Verifique se copiou até o `}` final de cada função
- Use um editor com destaque de sintaxe para verificar

---

## 🎯 Exemplo Visual

```
youtube_tv_standalone.ahk (arquivo original)
│
├─ [Linha 1-22] Configurações e comentários
│
├─ [Linha 23-100] License_GetDeviceId() ← COPIE ESTA
│
├─ [Linha 102-180] License_SHA256() ← COPIE ESTA
│
├─ [Linha 209-431] License_Verify() ← COPIE ESTA
│
└─ [Linha 432+] Código de verificação e resto do script
```

---

## 💡 Dica Pro

Se você tem vários scripts para proteger, considere:

1. Criar um arquivo `license_functions.ahk` com todas as funções
2. Usar `#Include license_functions.ahk` em cada script
3. Isso evita duplicação e facilita atualizações

---

**Pronto!** Agora você sabe exatamente o que copiar e onde colar.




