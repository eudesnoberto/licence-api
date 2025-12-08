# 📋 Guia Completo - Como Obter e Cadastrar Device ID

## 🎯 Resumo Rápido

1. **Cliente executa o script protegido** → Gera `device.id` automaticamente
2. **Você obtém o Device ID** → 3 métodos diferentes (veja abaixo)
3. **Cadastra no dashboard** → Cole o ID e escolha o plano
4. **Pronto!** → Cliente pode usar normalmente

---

## 🔍 Método 1: Arquivo device.id (Mais Fácil)

### Passo a Passo:

1. **Cliente executa o script protegido pela primeira vez**
   - O script cria automaticamente um arquivo `device.id` na mesma pasta do `.exe`
   - O script fecha imediatamente (porque não tem licença ainda)

2. **Cliente envia o arquivo `device.id` para você**
   - Pode enviar por WhatsApp, email, etc.
   - O arquivo contém apenas o Device ID (ex: `abc123def456...`)

3. **Você abre o arquivo e copia o conteúdo**
   - Abra com Bloco de Notas
   - Copie o texto (é o Device ID)

4. **Cadastra no dashboard:**
   - Acesse: `http://localhost:5173`
   - Login: `admin` / `admin123`
   - Seção "Cadastro Rápido"
   - Cole o Device ID
   - Escolha o plano
   - Clique em "Criar Licença"

**Pronto!** O cliente pode executar novamente e funcionará.

---

## 🔍 Método 2: Script Auxiliar (Recomendado)

### Passo a Passo:

1. **Crie um script auxiliar `obter_device_id.ahk`** (já criado para você!)

2. **Envie para o cliente:**
   - `obter_device_id.ahk`
   - `license_check.ahk` (mesma pasta)

3. **Cliente executa `obter_device_id.ahk`:**
   - Mostra uma mensagem com o Device ID
   - **Copia automaticamente** para a área de transferência
   - Cliente só precisa colar e enviar para você

4. **Você cadastra no dashboard** (mesmo processo do Método 1)

**Vantagem:** Mais fácil para o cliente, ID já copiado automaticamente.

---

## 🔍 Método 3: Mensagem de Erro

### Passo a Passo:

1. **Cliente executa o script protegido sem licença**
   - Aparece uma mensagem: "Sua licença não é válida ou expirou"
   - **A mensagem mostra o Device ID**

2. **Cliente copia o Device ID da mensagem**
   - Envia para você

3. **Você cadastra no dashboard** (mesmo processo)

**Vantagem:** Não precisa arquivo extra, o próprio script mostra.

---

## 🔍 Método 4: Dashboard (Acessos Recentes)

### Passo a Passo:

1. **Cliente executa o script protegido** (mesmo sem licença)
   - O script tenta verificar no servidor
   - O acesso fica registrado no banco de dados

2. **Você acessa o dashboard:**
   - Vá em "Licenças registradas"
   - Veja os acessos recentes
   - O Device ID aparece na primeira coluna da tabela

3. **Cadastra a licença:**
   - Copie o Device ID da tabela
   - Use no "Cadastro Rápido"

**Vantagem:** Você vê todos os acessos tentados, mesmo sem licença.

---

## 📝 Exemplo Prático Completo

### Cenário: Novo Cliente

**1. Você envia para o cliente:**
- `youtube_tv_protegido.exe` (script protegido compilado)
- `license_check.ahk` (na mesma pasta, se não compilado junto)

**2. Cliente executa pela primeira vez:**
```
Script inicia → Verifica licença → Não encontra → Mostra mensagem com Device ID → Fecha
```

**3. Cliente envia para você:**
```
"Olá, o Device ID é: abc123def456ghi789jkl012mno345pqr678"
```

**4. Você cadastra no dashboard:**
- Acessa: `http://localhost:5173`
- Login: `admin` / `admin123`
- Seção "Cadastro Rápido por Device ID"
- Cola: `abc123def456ghi789jkl012mno345pqr678`
- Seleciona: "Anual - R$ 180,00/ano"
- Clica: "Criar Licença"

**5. Cliente executa novamente:**
```
Script inicia → Verifica licença → Encontra válida → Continua normalmente ✅
```

---

## 🎯 Fluxo Visual

```
┌─────────────────┐
│ Cliente executa │
│   script.exe    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gera device.id  │
│  (automatico)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verifica API    │
│  (sem licença)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Mostra Device   │
│      ID         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cliente envia   │
│  Device ID      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Você cadastra   │
│  no dashboard   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cliente executa │
│   novamente     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Licença válida  │
│   Funciona! ✅  │
└─────────────────┘
```

---

## 💡 Dicas Importantes

### Onde fica o arquivo device.id?
- **Mesma pasta** do executável `.exe`
- Exemplo: Se o `.exe` está em `C:\MeusProgramas\`, o `device.id` também estará lá

### Device ID é único?
- **Sim!** Cada computador gera um Device ID único
- Baseado no hardware (Volume Serial + Computer Name)
- Mesmo computador = mesmo Device ID (sempre)

### Posso usar o mesmo Device ID em vários PCs?
- **Não!** Cada PC precisa de sua própria licença
- Cada PC tem seu próprio Device ID único

### E se o cliente formatar o PC?
- O Device ID **pode mudar** se o Volume Serial mudar
- Você precisará cadastrar novamente com o novo Device ID

---

## 🚀 Script Auxiliar (Mais Fácil)

Use o arquivo `obter_device_id.ahk` que criei:

1. **Envie para o cliente:**
   - `obter_device_id.ahk`
   - `license_check.ahk`

2. **Cliente executa:**
   - Mostra o Device ID
   - **Copia automaticamente** para área de transferência
   - Cliente só precisa colar e enviar

3. **Você cadastra no dashboard**

**Muito mais fácil!** 🎉

---

## ❓ Perguntas Frequentes

**P: O Device ID muda?**
R: Não, é baseado no hardware. Só muda se formatar o PC ou trocar HD.

**P: Posso ver todos os Device IDs tentados?**
R: Sim, no dashboard na tabela "Licenças registradas".

**P: E se o cliente não tiver internet?**
R: O script não funcionará (precisa verificar no servidor). Considere modo offline se necessário.

**P: Quantos Device IDs posso cadastrar?**
R: Quantos quiser! Não há limite.

---

**Agora ficou claro?** Use o método que preferir. Recomendo o **Método 2** (script auxiliar) por ser mais fácil! 🚀





