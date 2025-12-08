# Detecção de Clones - Sistema Anti-Pirataria

## ⚠️ Problema: Clonagem de PC

Se um usuário clonar o disco rígido (fazer uma imagem/clone), o Device ID será o mesmo e a licença funcionará em **duas máquinas diferentes**.

## 🛡️ Soluções Implementadas

### 1. Device ID Melhorado (Hardware Fingerprint)

O sistema agora coleta múltiplas informações únicas do hardware:

- **Volume Serial** (C:)
- **Computer Name**
- **MAC Address** (primeira placa de rede)
- **CPU ID** (quando disponível)
- **Motherboard Serial** (quando disponível)

### 2. Detecção no Backend

O backend agora detecta:

- **Acessos simultâneos** do mesmo Device ID de IPs diferentes
- **Mudanças frequentes de IP/Hostname** (indica clone)
- **Padrões suspeitos** de uso

### 3. Bloqueio Automático

Quando detectado:
- Licença é automaticamente bloqueada
- Admin recebe alerta no dashboard
- Logs detalhados são salvos

---

## 📊 Como Funciona

### Cenário 1: Clone Detectado

```
PC Original (IP: 192.168.1.10) → Device ID: abc123
PC Clonado (IP: 192.168.1.20) → Device ID: abc123 (MESMO!)

Backend detecta:
- Mesmo Device ID
- IPs diferentes
- Acessos simultâneos

Ação: Bloqueia ambas as licenças
```

### Cenário 2: Uso Normal

```
PC Único (IP: 192.168.1.10) → Device ID: abc123
Mesmo PC, IP mudou (IP: 192.168.1.15) → Device ID: abc123

Backend detecta:
- Mesmo Device ID
- IP mudou (normal - DHCP)
- Hostname igual
- Não há acesso simultâneo

Ação: Permite (uso legítimo)
```

---

## 🔧 Configuração

### No Backend (`api/config.py`)

```python
# Detecção de clones
ENABLE_CLONE_DETECTION = True
MAX_SIMULTANEOUS_IPS = 1  # Máximo de IPs diferentes simultâneos
CLONE_DETECTION_WINDOW = 300  # Janela de tempo em segundos (5 min)
```

### No Cliente AHK

O Device ID agora inclui automaticamente mais informações do hardware.

---

## 📝 Logs e Monitoramento

### Dashboard

O dashboard mostra:
- ⚠️ **Alerta** quando clone é detectado
- 📊 **Gráfico** de acessos por IP
- 🔍 **Histórico** de mudanças de IP/Hostname

### Logs do Backend

```
WARNING: Clone detectado - Device ID: abc123
  - IP 1: 192.168.1.10 (Hostname: PC1)
  - IP 2: 192.168.1.20 (Hostname: PC2)
  - Timestamp: 2025-11-29 10:30:00
  - Ação: Licença bloqueada automaticamente
```

---

## 🚨 Ações Automáticas

Quando clone é detectado:

1. **Bloqueio Imediato**: Licença é marcada como `blocked`
2. **Notificação**: Admin recebe alerta
3. **Log Detalhado**: Tudo é registrado para análise
4. **Mensagem ao Cliente**: "Licença bloqueada - uso simultâneo detectado"

---

## ✅ Boas Práticas

### Para Administradores

1. **Monitore o Dashboard**: Verifique alertas regularmente
2. **Analise Padrões**: IPs que mudam muito podem ser suspeitos
3. **Revise Logs**: Acessos simultâneos são sempre suspeitos

### Para Desenvolvedores

1. **Device ID Robusto**: Use múltiplas fontes de hardware
2. **Verificação Contínua**: Não confie apenas na verificação inicial
3. **Logs Detalhados**: Registre tudo para análise posterior

---

## 🔐 Limitações Conhecidas

### O que NÃO detecta:

- **Clones offline**: Se o clone nunca se conectar, não será detectado
- **Clones com mesmo IP**: Se ambos usarem VPN com mesmo IP
- **Clones muito espaçados**: Se usarem em horários diferentes

### O que detecta:

- ✅ Acessos simultâneos de IPs diferentes
- ✅ Mudanças frequentes de IP/Hostname
- ✅ Padrões suspeitos de uso

---

## 💡 Recomendações Adicionais

### 1. Verificação Periódica

Implemente verificação periódica (não apenas no início):

```autohotkey
; Verifica licença a cada 30 minutos
SetTimer, VerificarLicencaPeriodicamente, 1800000
return

VerificarLicencaPeriodicamente:
    isValid := License_Verify()
    If (!isValid) {
        MsgBox, 16, Licenca Invalida, Sua licenca foi revogada.
        ExitApp
    }
return
```

### 2. Limite de IPs

Configure no backend o máximo de IPs permitidos por Device ID.

### 3. Notificações

Configure alertas por email quando clone for detectado.

---

## 📞 Suporte

Se uma licença legítima for bloqueada por engano:

1. Verifique os logs no dashboard
2. Analise o padrão de acesso
3. Entre em contato com o suporte
4. Licença pode ser desbloqueada manualmente

---

**Sistema de detecção de clones ativo e funcionando!** 🛡️




