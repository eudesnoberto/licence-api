# 🆔 Como Obter o Device ID - Guia Visual

## 🎯 Resumo em 3 Passos

```
1. Cliente executa script → Gera Device ID automaticamente
2. Você recebe o Device ID (por arquivo ou mensagem)
3. Você cadastra no dashboard → Pronto!
```

---

## 📋 Método 1: Script Auxiliar (MAIS FÁCIL)

### O que fazer:

1. **Envie estes arquivos para o cliente:**
   - `obter_device_id.ahk` ← **Este arquivo**
   - `license_check.ahk` (mesma pasta)

2. **Cliente executa `obter_device_id.ahk`:**
   - Aparece uma janela mostrando o Device ID
   - O ID é **copiado automaticamente** para área de transferência
   - Cliente só precisa colar (Ctrl+V) e enviar para você

3. **Você cadastra no dashboard:**
   - Acessa: `http://localhost:5173`
   - Login: `admin` / `admin123`
   - Seção: **"Cadastro Rápido por Device ID"**
   - Cola o Device ID
   - Escolhe o plano
   - Clica "Criar Licença"

**Pronto!** ✅

---

## 📋 Método 2: Arquivo device.id

### O que fazer:

1. **Cliente executa o script protegido:**
   - Script cria arquivo `device.id` automaticamente
   - Script fecha (porque não tem licença)

2. **Cliente envia o arquivo `device.id`:**
   - Arquivo está na mesma pasta do `.exe`
   - Você abre com Bloco de Notas
   - Copia o conteúdo (é o Device ID)

3. **Você cadastra no dashboard** (mesmo processo acima)

---

## 📋 Método 3: Mensagem de Erro

### O que fazer:

1. **Cliente executa o script protegido:**
   - Aparece mensagem: "Licença inválida"
   - **A mensagem mostra o Device ID**

2. **Cliente copia o Device ID da mensagem:**
   - Envia para você

3. **Você cadastra no dashboard** (mesmo processo)

---

## 🖼️ Exemplo Visual

### Tela do Dashboard:

```
┌─────────────────────────────────────────┐
│  Cadastro Rápido por Device ID          │
├─────────────────────────────────────────┤
│                                         │
│  Device ID *                            │
│  [abc123def456ghi789jkl012...]         │
│                                         │
│  Nome (opcional)                        │
│  [João Silva]                           │
│                                         │
│  E-mail (opcional)                      │
│  [joao@email.com]                       │
│                                         │
│  Tipo de Licença *                      │
│  [Anual - R$ 180,00/ano ▼]             │
│                                         │
│  [     Criar Licença     ]              │
└─────────────────────────────────────────┘
```

---

## ❓ Perguntas Frequentes

**P: Onde fica o arquivo device.id?**
R: Na mesma pasta do executável `.exe`

**P: O Device ID muda?**
R: Não, é único por computador (baseado no hardware)

**P: Posso ver todos os Device IDs tentados?**
R: Sim, no dashboard na tabela "Licenças registradas"

**P: Quantos Device IDs posso cadastrar?**
R: Quantos quiser! Não há limite.

---

## 🚀 Dica Pro

**Use o script `obter_device_id.ahk`** - É o método mais fácil!
- Cliente executa
- ID é copiado automaticamente
- Só precisa colar e enviar

---

**Agora ficou claro?** 🎉





