# API `/verify` – Referência Técnica

## Endpoint

`GET https://fartgreen.fun/verify`

## Parâmetros obrigatórios

| Parâmetro | Descrição |
|-----------|-----------|
| `id` | ID único do dispositivo (gerado pelo cliente AHK). |
| `version` | Versão do aplicativo cliente (ex.: `1.0.0`). |
| `ts` | Timestamp UTC no formato `yyyyMMddHHmmss` (uso de `A_NowUTC`). |
| `sig` | Assinatura SHA-256 de `id|version|ts|SHARED_SECRET` (se `REQUIRE_SIGNATURE=true`). |

## Parâmetros opcionais

| Parâmetro | Descrição |
|-----------|-----------|
| `api_key` | Requerido se `REQUIRE_API_KEY=true` (também aceito no header `X-API-Key`). |
| `hostname`, `username`, `osbuild`, `ram_total`, `ram_free`, `cpu_load`, `client_time` | Telemetria auxiliar para antifalsificação/logs. |

## Respostas

```json
{
  "allow": true,
  "msg": "Licença ativa.",
  "config": {
    "interval": 30,
    "features": ["core","premium"],
    "message": "",
    "license_expires_at": "2025-12-31",
    "update": {
      "url": "https://fartgreen.fun/builds/app.exe",
      "sha256": "ab12...",
      "version": "1.1.0"
    }
  }
}
```

| Campo | Descrição |
|-------|-----------|
| `allow` | `true` libera o app; `false` obriga encerramento. |
| `msg` | Mensagem amigável para o usuário (opcional). |
| `config.interval` | Intervalo em segundos para nova verificação (mínimo 15). |
| `config.features` | Lista de recursos liberados (usada no cliente via `License_FeatureEnabled`). |
| `config.message` | Mensagem adicional, útil para avisos remotos. |
| `config.license_expires_at` | Data de expiração calculada; `null` para vitalícia. |
| `config.update` | Bloco opcional contendo URL/hash/versão para autoupdate. |

## Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | Requisição processada (allow true/false). |
| 400 | Parâmetros inválidos ou timestamp fora da janela. |
| 403 | Falha de autenticação (API key/assinatura) ou dispositivo bloqueado. |
| 500 | Erro inesperado no servidor. |

## Segurança embutida

1. **API key** – query string e header (habilite em `config.php`).
2. **Assinatura SHA-256** – impede alteração dos parâmetros.
3. **Timestamp + MAX_TIME_SKEW** – evita replay attack.
4. **Telemetria** – hostname, usuário e métricas ajudam a detectar clonagem.
5. **Blocklists** – tabela `blocked_devices` + array `$HARDCODED_BLOCKLIST`.

## Estrutura de dados

### Tabela `devices` (resumo)

| Campo | Tipo | Observação |
|-------|------|------------|
| `device_id` | VARCHAR(128) | ID único gerado pelo cliente. |
| `license_type` | ENUM | `mensal`, `trimestral`, `semestral`, `anual`, `trianual`, `vitalicia`. |
| `status` | ENUM | `active`, `blocked`, `pending`. |
| `start_date` / `end_date` | DATE | `end_date` pode ser `NULL` para vitalícia; o backend calcula automaticamente para demais tipos. |
| `custom_interval` | INT | Sobrescreve `config.interval` quando > 0. |
| `features` | TEXT | CSV simples (`core,premium`). O backend converte para array. |
| `update_url`, `update_hash`, `update_version` | TEXT | Usado para acionar o autoupdater. |

### Tabela `access_logs`

- Registra cada `/verify` com IP, host, versão, telemetria e resultado (`allowed`).
- Útil para auditoria e alertas de segurança.

### Tabela `blocked_devices`

- Controle emergencial para revogar acesso de um ID sem alterar o registro principal.

## Licenças (períodos padrão)

| Tipo | Duração | Observação |
|------|---------|------------|
| mensal | 1 mês | `P1M` |
| trimestral | 3 meses | `P3M` |
| semestral | 6 meses | `P6M` |
| anual | 12 meses | `P1Y` |
| trianual | 36 meses | `P3Y` |
| vitalicia | infinita | `end_date = NULL` |

## Exemplo de cadastro manual

```sql
INSERT INTO devices (
  device_id, owner_name, license_type, status,
  start_date, end_date, custom_interval, features,
  update_url, update_hash, update_version
) VALUES (
  'A1B2C3D4E5',
  'Empresa XPTO',
  'anual',
  'active',
  '2025-01-01',
  '2026-01-01',
  45,
  'core,premium',
  'https://fartgreen.fun/builds/app-1.1.exe',
  '9d2e7b3c4a...',
  '1.1.0'
);
```

## Expansões futuras

- Endpoint `/admin` para CRUD de licenças e painel web.
- Webhook para alertar quando um ID for bloqueado/expirar.
- Assinatura dupla (cliente → servidor e servidor → cliente) usando tokens rotativos.





