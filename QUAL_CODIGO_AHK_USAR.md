# 🎯 Qual Código AHK Usar?

## 📋 Recomendação Principal

### **Use: `SOLUCAO_COM_REDUNDANCIA.ahk`**

Este é o arquivo mais completo e atualizado, com:
- ✅ Redundância de servidores (tenta principal, depois backup)
- ✅ Modo offline (7 dias de graça)
- ✅ Todas as funções necessárias
- ✅ Servidores já configurados

---

## 📁 Arquivos Disponíveis

### **1. `SOLUCAO_COM_REDUNDANCIA.ahk`** ⭐ RECOMENDADO
- **Para**: Uso em produção com múltiplos servidores
- **Recursos**: Redundância, offline, todas as funções
- **Servidores configurados**: 
  - Principal: `https://api.fartgreen.fun`
  - Backup: `https://licence-api-zsbg.onrender.com`

### **2. `SOLUCAO_COMPLETA.ahk`**
- **Para**: Uso simples com um servidor
- **Recursos**: Todas as funções, mas sem redundância
- **Servidor**: Configurar manualmente

### **3. `CODIGO_PARA_COPIAR.ahk`**
- **Para**: Integração em código existente
- **Recursos**: Apenas funções e configurações (sem lógica principal)

---

## 🚀 Como Usar

### **Opção 1: Usar Arquivo Completo (Mais Fácil)**

1. Abra `SOLUCAO_COM_REDUNDANCIA.ahk`
2. Copie TODO o conteúdo
3. Cole no início do seu script AHK
4. Adicione a verificação no início do seu código:

```autohotkey
; ============================================================================
; SEU CÓDIGO AQUI
; ============================================================================

; Verificação de licença no início
if (!License_Verify()) {
    ExitApp  ; Fecha se licença inválida
}

; Seu código continua aqui...
```

### **Opção 2: Integrar em Código Existente**

1. Abra `CODIGO_PARA_COPIAR.ahk`
2. Copie as seções:
   - Configurações (linhas 1-25)
   - Todas as funções (linhas 27-100)
3. Cole no início do seu script
4. Adicione verificação:

```autohotkey
; Verificação de licença
if (!License_Verify()) {
    ExitApp
}
```

---

## ⚙️ Configuração Necessária

### **1. Device ID**
O código gera automaticamente, mas você pode definir manualmente:

```autohotkey
; Opcional: definir Device ID manual
; g_LicenseDeviceId := "SEU_DEVICE_ID_AQUI"
```

### **2. Servidores** (já configurado em SOLUCAO_COM_REDUNDANCIA.ahk)

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api.fartgreen.fun"
g_LicenseAPI_Servers[2] := "https://licence-api-zsbg.onrender.com"
```

### **3. API Key e Secret** (já configurado)

```autohotkey
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
```

---

## 📝 Exemplo de Uso Completo

```autohotkey
; ============================================================================
; INCLUIR CÓDIGO DE LICENÇA
; ============================================================================
; Copie TODO o conteúdo de SOLUCAO_COM_REDUNDANCIA.ahk aqui
; OU use #Include:
; #Include SOLUCAO_COM_REDUNDANCIA.ahk

; ============================================================================
; SEU CÓDIGO
; ============================================================================

; Verificar licença no início
if (!License_Verify()) {
    ; Se licença inválida, fecha o programa
    ExitApp
}

; Seu código continua aqui...
MsgBox, Licença válida! Programa funcionando...
; ... resto do seu código ...
```

---

## 🔍 Verificar se Está Funcionando

O código cria arquivos de log para debug:

- `license_debug.txt` - Logs gerais
- `license_server_used.txt` - Qual servidor foi usado
- `license_offline_success.txt` - Se usou modo offline
- `license_offline_failed.txt` - Se modo offline falhou

Verifique esses arquivos se houver problemas.

---

## ⚠️ Importante

1. **Salve como UTF-8 com BOM** antes de compilar
   - Isso evita problemas de codificação

2. **Teste primeiro sem compilar**
   - Execute o `.ahk` diretamente
   - Verifique os logs
   - Só compile depois que funcionar

3. **Device ID**
   - O código gera automaticamente
   - Use o mesmo Device ID para cadastrar no dashboard

---

## 📚 Documentação Adicional

- `GUIA_RAPIDO_INTEGRACAO.md` - Guia passo a passo
- `CODIGO_PARA_COPIAR.ahk` - Template para integração
- `SOLUCAO_COMPLETA.ahk` - Solução sem redundância

---

**Resumo**: Use `SOLUCAO_COM_REDUNDANCIA.ahk` - é o mais completo e já está configurado! 🚀

