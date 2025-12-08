# Configuração de IP Real do Cliente

## 🔍 Problema

Quando o backend está atrás de um proxy (Cloudflare Tunnel, nginx, etc.), o `request.remote_addr` retorna o IP do proxy (geralmente `127.0.0.1` ou IP interno), não o IP real do cliente.

## ✅ Solução Implementada

O sistema agora usa a função `get_client_ip()` que verifica múltiplos headers na seguinte ordem:

1. **CF-Connecting-IP** (Cloudflare real)
2. **X-Forwarded-For** (padrão para proxies)
3. **X-Real-IP** (alguns proxies)
4. **request.remote_addr** (após ProxyFix)

### ProxyFix

O Flask foi configurado com `ProxyFix` do Werkzeug para processar automaticamente os headers `X-Forwarded-For` e atualizar `request.remote_addr` corretamente.

## 🧪 Como Testar

### 1. Verificar Headers Recebidos

Adicione um log temporário no endpoint `/verify`:

```python
logger.info(f"Headers: X-Forwarded-For={request.headers.get('X-Forwarded-For')}, CF-Connecting-IP={request.headers.get('CF-Connecting-IP')}, remote_addr={request.remote_addr}")
```

### 2. Testar Localmente

Quando testa localmente (`http://127.0.0.1:5000`), o IP sempre será `127.0.0.1` porque você está na mesma máquina. Isso é **normal**.

### 3. Testar em Produção

Quando o cliente acessa via `https://api.fartgreen.fun`:

- O Cloudflare Tunnel deve passar o IP real no header `X-Forwarded-For`
- O `get_client_ip()` deve capturar corretamente

## 🔧 Configuração do Cloudflare Tunnel

O Cloudflare Tunnel **deve** passar o IP real automaticamente. Se não estiver funcionando:

### Verificar Configuração do Tunnel

1. Verifique o arquivo de configuração do `cloudflared`:

```yaml
tunnel: <tunnel-id>
credentials-file: C:\Users\...\.cloudflared\<tunnel-id>.json

ingress:
  - hostname: api.fartgreen.fun
    service: http://localhost:5000
    originRequest:
      # Garante que headers são preservados
      noHappyEyeballs: false
      keepAliveConnections: 10
      keepAliveTimeout: 90s
```

### Testar Manualmente

Faça uma requisição e verifique os headers:

```bash
curl -H "X-Forwarded-For: 1.2.3.4" https://api.fartgreen.fun/health
```

## 📊 Verificar no Dashboard

Após fazer uma requisição, verifique no dashboard:

1. Acesse a tabela de licenças
2. Veja a coluna **IP**
3. Deve mostrar o IP real do cliente (não `127.0.0.1`)

## 🐛 Troubleshooting

### IP ainda mostra `127.0.0.1`

**Possíveis causas:**

1. **Testando localmente**: Normal, você está na mesma máquina
2. **Cloudflare Tunnel não configurado**: Verifique a configuração
3. **Headers não sendo passados**: Adicione logs para verificar

**Solução:**

1. Verifique os logs do backend:
   ```
   INFO:__main__:IP obtido via X-Forwarded-For: <IP>
   ```

2. Se não aparecer, o Cloudflare Tunnel pode não estar passando os headers corretamente

3. Em desenvolvimento local, use um proxy reverso (nginx) ou teste diretamente de outra máquina

### IP mostra IP interno (192.168.x.x, 10.x.x.x)

**Causa:** Cliente está em rede local/NAT

**Solução:** Isso é **normal** para clientes em redes locais. O importante é que seja o IP real do cliente (não do proxy).

### IP mostra "unknown"

**Causa:** Nenhum header foi encontrado

**Solução:**
1. Verifique se o Cloudflare Tunnel está configurado corretamente
2. Adicione logs para ver quais headers estão chegando
3. Verifique se o ProxyFix está funcionando

## 📝 Logs de Debug

Para ativar logs detalhados de IP, adicione no código:

```python
logger.setLevel(logging.DEBUG)
```

Isso mostrará qual método foi usado para obter o IP:

```
DEBUG:__main__:IP obtido via X-Forwarded-For: 177.123.45.67
```

## ✅ Verificação Final

Após implementar:

1. ✅ Cliente faz requisição de máquina remota
2. ✅ Backend captura IP real (não `127.0.0.1`)
3. ✅ Dashboard mostra IP correto na coluna "IP"
4. ✅ Detecção de clones funciona corretamente

---

**Sistema configurado para capturar IP real do cliente!** 🌐




