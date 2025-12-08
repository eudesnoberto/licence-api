# ✅ Executar Arquivo Separadamente

## 🎯 Resposta: SIM, pode ser executado separadamente!

O arquivo `youtube_tv_standalone.ahk` é **standalone** (tudo em um arquivo), então pode ser executado sozinho.

---

## 📋 O que você precisa

### Arquivos obrigatórios:

1. **`youtube_tv_standalone.ahk`** ← Arquivo principal (já tem tudo)
2. **`performace.ahk`** ← Seu arquivo original (precisa estar na mesma pasta)

### Arquivos opcionais (se seu código usar):

- `Comandos.exe`
- `blocked.exe`
- `clicks.exe`
- `notification.exe`
- `timetemporary.exe`
- `images.exe`
- `psrockola4.exe`

---

## 🚀 Como executar

### Opção 1: Executar diretamente

```powershell
# Na pasta onde está o arquivo
"C:\Program Files\AutoHotkey\AutoHotkeyA32.exe" "C:\youtube\youtube_tv_standalone.ahk"
```

### Opção 2: Compilar e executar

1. Abra `youtube_tv_standalone.ahk` no AutoHotkey
2. Use **Ahk2Exe** para compilar em `.exe`
3. Execute o `.exe` diretamente

**Vantagem:** Não precisa do AutoHotkey instalado no PC cliente.

---

## 📁 Estrutura de Pastas

```
C:\youtube\
├── youtube_tv_standalone.ahk  ← Arquivo principal
├── performace.ahk              ← Seu arquivo original (mesma pasta)
├── device.id                   ← Gerado automaticamente na primeira execução
├── Comandos.exe                ← Seus executáveis
├── blocked.exe
├── clicks.exe
└── ... (outros arquivos que seu código usa)
```

---

## ⚠️ Importante

### O arquivo `performace.ahk`:

- **Precisa estar na mesma pasta** do `youtube_tv_standalone.ahk`
- Se não estiver, o script continua mas pode dar erro se o código depender dele
- O script agora verifica se existe antes de incluir

### Se não tiver `performace.ahk`:

- O script vai continuar sem ele
- Se seu código depender dele, pode dar erro
- **Solução:** Copie o `performace.ahk` para a mesma pasta

---

## ✅ Checklist

- [ ] `youtube_tv_standalone.ahk` na pasta
- [ ] `performace.ahk` na mesma pasta (se necessário)
- [ ] Credenciais configuradas (linhas 12-13)
- [ ] Backend rodando (`python app.py`)
- [ ] Licença cadastrada no dashboard (para o Device ID)

---

## 🎯 Resumo

**SIM, pode executar separadamente!**

- ✅ Tudo em um arquivo (standalone)
- ✅ Não precisa de `license_check.ahk` separado
- ✅ Precisa do `performace.ahk` na mesma pasta (seu código original)
- ✅ Pode compilar em `.exe` e distribuir

**Pronto para usar!** 🚀





