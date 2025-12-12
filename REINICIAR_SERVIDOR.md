# 🔄 Como Reiniciar o Servidor Flask

## ⚠️ IMPORTANTE

Após alterações no código do backend (`api/app.py`), **é necessário reiniciar o servidor Flask** para que as mudanças tenham efeito.

## 📋 Passos para Reiniciar

### 1. Parar o Servidor Atual

Se o servidor está rodando em um terminal:
- Pressione `Ctrl + C` no terminal onde o servidor está rodando

### 2. Reiniciar o Servidor

#### Opção A: Terminal Local
```powershell
# Ativar ambiente virtual (se estiver usando)
.venv\Scripts\Activate.ps1

# Navegar para a pasta api
cd api

# Iniciar servidor
python app.py
```

#### Opção B: Se estiver usando um serviço/processo
- Reinicie o serviço ou processo que está executando o Flask

### 3. Verificar se Está Funcionando

- Acesse o dashboard
- Tente atualizar o perfil novamente
- O erro "Apenas usuários comuns podem atualizar o perfil" não deve mais aparecer

## 🐛 Se Ainda Estiver com Problema

1. **Verifique os logs do servidor** - pode haver erros de sintaxe ou importação
2. **Limpe o cache do navegador** - pressione `Ctrl + Shift + R` para recarregar forçado
3. **Verifique se o arquivo foi salvo** - confirme que `api/app.py` tem as alterações

## ✅ Após Reiniciar

O admin poderá:
- ✅ Adicionar/atualizar email no perfil
- ✅ Usar recuperação de senha com o email cadastrado
- ✅ Ver o email no perfil

