# 🔍 Debug SHA256 - Como Verificar

## 📋 Arquivos de Debug

Após executar o script, verifique estes arquivos:

### 1. `%TEMP%\license_sig_debug.txt`
Contém:
- Texto combinado usado para gerar assinatura
- Assinatura gerada
- Tamanho da assinatura

### 2. `%TEMP%\license_sig_error.txt`
Contém erros se a geração falhar

---

## 🔍 Como Verificar

1. **Execute o script protegido**
2. **Abra o PowerShell:**
   ```powershell
   notepad $env:TEMP\license_sig_debug.txt
   ```

3. **Verifique:**
   - Se `Combined:` tem o texto correto
   - Se `Signature:` tem 64 caracteres hexadecimais
   - Se `Tamanho:` é 64

---

## ✅ Assinatura Válida

Uma assinatura SHA256 válida deve ter:
- **64 caracteres** hexadecimais (0-9, a-f)
- Exemplo: `a1b2c3d4e5f6...` (64 caracteres)

---

## ❌ Problemas Comuns

### Assinatura vazia ou muito curta
- Problema: PowerShell não está executando corretamente
- Solução: Verifique se PowerShell está instalado e acessível

### Caracteres especiais no texto
- Problema: Escape incorreto
- Solução: O código já trata isso, mas verifique o arquivo de debug

---

## 🧪 Teste Manual

Teste a função SHA256 manualmente:

```powershell
$text = "2049365993desktop-j65uer12025112|1.0.0|20251128221909|BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$hashBytes = $sha256.ComputeHash($bytes)
$hashString = [System.BitConverter]::ToString($hashBytes) -replace '-',''
$hashString.ToLower()
```

**Deve retornar 64 caracteres hexadecimais!**

---

**Use esses arquivos de debug para identificar o problema!** 🔍





