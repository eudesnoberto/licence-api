# 📋 Análise Completa do Sistema de Licenciamento

## 🎯 Visão Geral

Este documento descreve detalhadamente como funciona o sistema de proteção de licenças implementado, desde a geração do Device ID até a verificação online/offline e proteção contra clonagem.

---

## 🔑 Componentes Principais

### 1. **Device ID (Identificador Único do Dispositivo)**

#### Como é Gerado:
- **Fonte de dados**: Serial do volume C: + Nome do computador + Timestamp + TickCount
- **Algoritmo**: SHA256 hash dos dados combinados
- **Formato**: 32 caracteres hexadecimais (primeiros 32 chars do hash SHA256)
- **Armazenamento**: Arquivo `device.id` na pasta do script ou `%APPDATA%\LicenseSystem\`

#### Características:
- ✅ **Único por máquina**: Baseado em hardware (serial do disco)
- ✅ **Persistente**: Salvo em arquivo para reutilização
- ✅ **Determinístico**: Mesma máquina = mesmo Device ID
- ✅ **Não modificável facilmente**: Requer alteração de hardware ou manipulação de arquivo

#### Código (AHK):
```autohotkey
License_GetDeviceId() {
    DriveGet, volSerial, Serial, C:
    EnvGet, computerName, COMPUTERNAME
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := volSerial . computerName . timestamp . A_TickCount
    hash := SHA256(combined)
    deviceId := SubStr(hash, 1, 32)
    return deviceId
}
```

---

## 🔐 2. Sistema de Autenticação e Assinatura

### Assinatura da Requisição (Cliente → Servidor)

#### Como Funciona:
1. **Cliente gera timestamp**: `yyyyMMddHHmmss` (ex: `20241215143025`)
2. **Combina dados**: `deviceId|version|timestamp|SHARED_SECRET`
3. **Gera assinatura**: SHA256 da string combinada
4. **Envia na URL**: `?id=...&version=...&ts=...&sig=...&api_key=...`

#### Validação no Servidor:
```python
expected = hashlib.sha256(
    f"{id_}|{version}|{ts}|{config.SHARED_SECRET}".encode("utf-8")
).hexdigest()

if not hmac.compare_digest(expected, sig):
    return {"allow": False, "msg": "Assinatura inválida."}
```

#### Proteções:
- ✅ **Timestamp**: Previne replay attacks (requisições antigas)
- ✅ **Time Skew**: Máximo de diferença permitida (padrão: 24 horas)
- ✅ **API Key**: Chave adicional para autenticação
- ✅ **HMAC-SHA256**: Assinatura criptográfica segura

---

## 🌐 3. Fluxo de Verificação Online

### Endpoint: `GET /verify`

#### Parâmetros Obrigatórios:
- `id`: Device ID
- `version`: Versão do cliente
- `ts`: Timestamp (formato: `yyyyMMddHHmmss`)
- `sig`: Assinatura SHA256
- `api_key`: Chave de API

#### Parâmetros Opcionais (Telemetria):
- `hostname`: Nome do computador
- `username`: Usuário do Windows
- `osbuild`: Build do sistema operacional
- `ram_total`, `ram_free`: Memória RAM
- `cpu_load`: Carga do processador
- `client_time`: Hora do cliente

#### Fluxo de Processamento:

```
1. VALIDAÇÃO INICIAL
   ├─ Verifica parâmetros obrigatórios
   ├─ Valida API Key (se configurado)
   ├─ Valida Timestamp (time skew)
   └─ Valida Assinatura (HMAC-SHA256)

2. BUSCA DO DISPOSITIVO
   ├─ Busca Device ID no banco de dados
   ├─ Se não existe:
   │  ├─ Auto-provisiona (se ALLOW_AUTO_PROVISION = True)
   │  └─ Cria com status "pending", tipo "mensal"
   └─ Se existe: Usa registro existente

3. VERIFICAÇÕES DE SEGURANÇA
   ├─ Blocklist hardcoded (config.HARDCODED_BLOCKLIST)
   ├─ Blocklist no banco (tabela blocked_devices)
   └─ Detecção de clones (detect_clone_usage)

4. AVALIAÇÃO DA LICENÇA
   ├─ Verifica status (blocked → negado)
   ├─ Verifica expiração (end_date < hoje → negado)
   ├─ Verifica status "pending" → negado
   └─ Se tudo OK → permitido

5. DETECÇÃO DE CLONES
   ├─ Analisa acessos recentes (últimos X segundos)
   ├─ Verifica IPs únicos simultâneos
   ├─ Verifica mudança suspeita de IP + Hostname
   └─ Se detectado: Bloqueia automaticamente

6. ATUALIZAÇÃO DE MÉTRICAS
   ├─ Atualiza last_seen_at, last_seen_ip, last_hostname
   ├─ Registra log de acesso (access_logs)
   └─ Salva telemetria (JSON)

7. GERAÇÃO DE TOKEN OFFLINE
   ├─ Cria payload JSON com informações da licença
   ├─ Assina com HMAC-SHA256 usando SHARED_SECRET
   └─ Retorna token para cache no cliente

8. RESPOSTA
   └─ JSON com: allow, msg, config, license_token
```

---

## 📊 4. Avaliação de Licença (evaluate_license)

### Estados Possíveis:

| Status | Descrição | Resultado |
|--------|-----------|-----------|
| `blocked` | Licença bloqueada manualmente ou por clone | ❌ Negado |
| `pending` | Aguardando aprovação/ativação | ❌ Negado |
| `active` | Licença ativa | ✅ Permitido (se não expirada) |
| `expired` | Licença expirada | ❌ Negado |

### Verificação de Expiração:

```python
if license_type != "vitalicia" and end_date:
    today = date.today()
    expires = datetime.strptime(end_date, "%Y-%m-%d").date()
    if today > expires:
        return {"allow": False, "msg": "Licença expirada"}
```

### Tipos de Licença:

| Tipo | Duração | end_date |
|------|---------|----------|
| `mensal` | 1 mês | Calculado |
| `trimestral` | 3 meses | Calculado |
| `semestral` | 6 meses | Calculado |
| `anual` | 1 ano | Calculado |
| `trianual` | 3 anos | Calculado |
| `vitalicia` | Ilimitado | `null` |

---

## 🛡️ 5. Detecção de Clones

### Como Funciona:

#### Algoritmo:
1. **Busca acessos recentes**: Últimos X segundos (configurável: `CLONE_DETECTION_WINDOW`)
2. **Agrupa por IP**: Conta IPs únicos que acessaram no período
3. **Verifica limite**: Se mais de `MAX_SIMULTANEOUS_IPS` IPs → Clone detectado
4. **Verifica mudança suspeita**: IP + Hostname mudaram simultaneamente

#### Código:
```python
def detect_clone_usage(device_id: str, current_ip: str, current_hostname: str):
    # Busca acessos recentes
    window_start = datetime.now() - timedelta(seconds=CLONE_DETECTION_WINDOW)
    
    # Conta IPs únicos
    unique_ips = set()
    for access in recent_accesses:
        unique_ips.add(access.ip)
    
    # Se mais IPs que o permitido → Clone
    if len(unique_ips) > MAX_SIMULTANEOUS_IPS:
        return (True, "Uso simultâneo detectado")
    
    # Verifica mudança suspeita
    if (current_ip != last_ip and 
        current_hostname != last_hostname and 
        len(recent_accesses) > 1):
        return (True, "Mudança suspeita detectada")
```

#### Ações ao Detectar Clone:
1. ✅ **Bloqueia automaticamente**: Status → `blocked`
2. ✅ **Registra no log**: Mensagem de clone detectado
3. ✅ **Retorna erro**: Cliente recebe `allow: false`

---

## 💾 6. Sistema Offline (Modo Graça)

### Como Funciona:

#### Token de Licença:
- **Formato**: JSON com `payload`, `payload_raw`, `signature`
- **Assinatura**: HMAC-SHA256 do `payload_raw` usando `SHARED_SECRET`
- **Conteúdo**: Device ID, tipo, status, data de expiração, features

#### Fluxo Offline:

```
1. CLIENTE SALVA TOKEN
   ├─ Recebe license_token do servidor
   ├─ Salva em arquivo (license_token.json)
   └─ Local: Script dir ou %APPDATA%\LicenseSystem\

2. VERIFICAÇÃO OFFLINE
   ├─ Tenta conexão online primeiro
   ├─ Se falhar: Carrega token salvo
   ├─ Valida assinatura (simplificada)
   ├─ Verifica Device ID corresponde
   ├─ Verifica status = "active"
   └─ Verifica expiração (com período de graça)

3. PERÍODO DE GRAÇA
   ├─ Padrão: 7 dias
   ├─ Permite uso mesmo se servidor offline
   └─ Após período: Requer conexão online
```

#### Validações Offline:

```autohotkey
License_Verify_Offline(licenseTokenJson) {
    // 1. Extrai payload e signature
    // 2. Verifica Device ID corresponde
    // 3. Verifica status = "active"
    // 4. Verifica expiração (com graça de 7 dias)
    // 5. Retorna true/false
}
```

#### Período de Graça:
- **Duração**: 7 dias (configurável: `g_LicenseOffline_GracePeriodDays`)
- **Objetivo**: Permitir uso quando servidor está offline
- **Limitação**: Após período, requer conexão online obrigatória

---

## 📝 7. Estrutura do Banco de Dados

### Tabela: `devices`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | PK auto-incremento |
| `device_id` | TEXT | Device ID único (UNIQUE) |
| `owner_name` | TEXT | Nome do proprietário |
| `cpf` | TEXT | CPF do cliente |
| `email` | TEXT | E-mail do cliente |
| `address` | TEXT | Endereço completo |
| `license_type` | TEXT | Tipo: mensal, anual, vitalicia, etc. |
| `status` | TEXT | active, pending, blocked, expired |
| `start_date` | TEXT | Data de início (ISO) |
| `end_date` | TEXT | Data de fim (ISO, null para vitalicia) |
| `created_by` | TEXT | Usuário que criou a licença |
| `last_seen_at` | TEXT | Último acesso (ISO) |
| `last_seen_ip` | TEXT | Último IP de acesso |
| `last_hostname` | TEXT | Último hostname |
| `last_version` | TEXT | Última versão do cliente |

### Tabela: `access_logs`

Registra **todos** os acessos para:
- 📊 Análise de uso
- 🛡️ Detecção de clones
- 📈 Métricas e estatísticas

| Campo | Descrição |
|-------|-----------|
| `device_id` | Device ID que acessou |
| `ip` | IP de origem |
| `hostname` | Nome do computador |
| `allowed` | Se foi permitido (0/1) |
| `message` | Mensagem de resposta |
| `telemetry_json` | Dados de telemetria (JSON) |
| `created_at` | Timestamp do acesso |

### Tabela: `blocked_devices`

Lista negra de dispositivos bloqueados manualmente.

---

## 🔄 8. Fluxo Completo (Cliente → Servidor)

### 1. **Inicialização do Cliente (AHK)**

```autohotkey
; Gera Device ID (ou carrega do arquivo)
deviceId := License_GetDeviceId()

; Gera timestamp e assinatura
timestamp := FormatTime(..., "yyyyMMddHHmmss")
signature := SHA256(deviceId . "|" . version . "|" . timestamp . "|" . SECRET)

; Monta URL
url := API_BASE_URL . "/verify?id=" . deviceId . "&version=" . version . "&ts=" . timestamp . "&sig=" . signature
```

### 2. **Requisição HTTP**

```
GET /verify?id=abc123...&version=1.0.0&ts=20241215143025&sig=def456...&api_key=...
```

### 3. **Processamento no Servidor**

```
1. Valida assinatura
2. Busca dispositivo
3. Avalia licença
4. Detecta clones
5. Atualiza métricas
6. Gera token offline
7. Retorna JSON
```

### 4. **Resposta do Servidor**

```json
{
  "allow": true,
  "msg": "Licença ativa.",
  "config": {
    "interval": 60,
    "features": ["core"],
    "license_expires_at": "2025-12-15"
  },
  "license_token": {
    "payload": {...},
    "payload_raw": "{...}",
    "signature": "abc123..."
  }
}
```

### 5. **Cliente Processa Resposta**

```autohotkey
If (allow = true) {
    ; Salva token para uso offline
    License_SaveToken(license_token)
    ; Continua execução
} Else {
    ; Exibe erro e encerra
    MsgBox, Licença inválida: %msg%
    ExitApp
}
```

---

## 🔒 9. Segurança

### Proteções Implementadas:

1. **✅ Assinatura HMAC-SHA256**
   - Previne requisições falsificadas
   - Valida autenticidade do cliente

2. **✅ Timestamp com Time Skew**
   - Previne replay attacks
   - Valida sincronização de relógio

3. **✅ API Key**
   - Camada adicional de autenticação
   - Previne acesso não autorizado

4. **✅ Detecção de Clones**
   - Identifica uso simultâneo
   - Bloqueia automaticamente

5. **✅ Blocklist**
   - Lista negra de dispositivos
   - Bloqueio manual/automático

6. **✅ Device ID Baseado em Hardware**
   - Difícil de falsificar
   - Único por máquina

7. **✅ Token Offline Assinado**
   - Validação local sem servidor
   - Período de graça limitado

---

## 📈 10. Tipos de Licença e Cálculo de Expiração

### Cálculo de `end_date`:

```python
def calculate_end_date(license_type: str, start_date: str):
    if license_type == "vitalicia":
        return None  # Sem expiração
    
    # Parse do período (ex: "P1M" = 1 mês, "P1Y" = 1 ano)
    period = LICENSE_PERIODS[license_type]
    
    # Adiciona meses/anos à data de início
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    # ... cálculos de data ...
    
    return end.isoformat()
```

### Exemplos:

| Tipo | Período | Exemplo |
|------|---------|---------|
| Mensal | P1M | 15/12/2024 → 15/01/2025 |
| Trimestral | P3M | 15/12/2024 → 15/03/2025 |
| Semestral | P6M | 15/12/2024 → 15/06/2025 |
| Anual | P1Y | 15/12/2024 → 15/12/2025 |
| Trianual | P3Y | 15/12/2024 → 15/12/2027 |
| Vitalicia | - | Sem expiração |

---

## 🎯 11. Casos de Uso

### Cenário 1: Primeira Execução
1. Cliente gera Device ID
2. Faz requisição ao servidor
3. Servidor auto-provisiona (status: `pending`)
4. Cliente recebe `allow: false, msg: "Licença aguardando aprovação"`
5. Admin ativa licença no dashboard
6. Próxima verificação: `allow: true`

### Cenário 2: Licença Ativa
1. Cliente verifica licença
2. Servidor valida: status `active`, não expirada
3. Retorna `allow: true` + token offline
4. Cliente salva token e continua

### Cenário 3: Servidor Offline
1. Cliente tenta conexão online → falha
2. Carrega token offline salvo
3. Valida localmente (Device ID, status, expiração)
4. Se válido e dentro do período de graça → permite
5. Se período expirado → bloqueia

### Cenário 4: Clone Detectado
1. Dois IPs diferentes acessam com mesmo Device ID
2. Servidor detecta uso simultâneo
3. Bloqueia automaticamente (status → `blocked`)
4. Próximas requisições: `allow: false`

### Cenário 5: Licença Expirada
1. Cliente verifica licença
2. Servidor compara `end_date` com hoje
3. Se `hoje > end_date` → `allow: false, msg: "Licença expirada"`
4. Cliente bloqueia execução

---

## 📊 12. Métricas e Logs

### Logs de Acesso (`access_logs`):
- **Todos os acessos** são registrados
- Inclui: IP, hostname, versão, telemetria
- Usado para: Detecção de clones, análise de uso, auditoria

### Atualização de Métricas:
- `last_seen_at`: Último acesso
- `last_seen_ip`: Último IP
- `last_hostname`: Último hostname
- `last_version`: Última versão do cliente

---

## 🔧 13. Configurações Importantes

### No Servidor (`config.py`):

```python
# Segurança
REQUIRE_API_KEY = True
API_KEY = "sua_chave_secreta"
REQUIRE_SIGNATURE = True
SHARED_SECRET = "seu_secret_compartilhado"
MAX_TIME_SKEW = 86400  # 24 horas em segundos

# Auto-provisionamento
ALLOW_AUTO_PROVISION = True  # Cria dispositivo automaticamente

# Detecção de clones
ENABLE_CLONE_DETECTION = True
CLONE_DETECTION_WINDOW = 300  # 5 minutos
MAX_SIMULTANEOUS_IPS = 1  # Máximo de IPs simultâneos
```

### No Cliente (AHK):

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "sua_chave"
g_LicenseAPI_Secret := "seu_secret"
g_LicenseAPI_Version := "1.0.0"
g_LicenseOffline_GracePeriodDays := 7
```

---

## ✅ 14. Resumo Executivo

### O Sistema Funciona Assim:

1. **🔑 Identificação**: Cada máquina tem um Device ID único baseado em hardware
2. **🔐 Autenticação**: Requisições são assinadas com HMAC-SHA256
3. **🌐 Verificação Online**: Servidor valida licença em tempo real
4. **💾 Modo Offline**: Token assinado permite uso sem servidor (período de graça)
5. **🛡️ Proteção**: Detecção de clones, blocklist, validação de expiração
6. **📊 Logs**: Todos os acessos são registrados para auditoria

### Pontos Fortes:
- ✅ Segurança robusta (HMAC, timestamps, API keys)
- ✅ Proteção contra clonagem
- ✅ Funciona offline (período de graça)
- ✅ Fácil integração (AHK, C#, etc.)
- ✅ Dashboard completo para gerenciamento
- ✅ Logs detalhados para auditoria

### Limitações:
- ⚠️ Device ID pode ser copiado (arquivo `device.id`)
- ⚠️ Período de graça offline limitado
- ⚠️ Requer conexão periódica com servidor
- ⚠️ Detecção de clones baseada em IP (pode ter falsos positivos com VPN)

---

## 📚 15. Referências Técnicas

- **HMAC-SHA256**: RFC 2104
- **Device ID**: Baseado em hardware (serial do disco)
- **Token Offline**: JWT-like com assinatura HMAC
- **Time Skew**: Prevenção de replay attacks
- **Clone Detection**: Análise de IPs simultâneos

---

**Documento gerado em**: 2024-12-15  
**Versão do Sistema**: 1.0.0  
**Autor**: Sistema de Licenciamento Easy Play Rockola

