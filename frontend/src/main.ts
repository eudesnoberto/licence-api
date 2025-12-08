import './style.css'

// ============================================================================
// CONFIGURAÇÃO DE SERVIDORES COM REDUNDÂNCIA
// ============================================================================
// Array de servidores em ordem de prioridade
// O sistema tentará cada servidor até encontrar um que funcione
// 
// CONFIGURAÇÃO VIA .env (RECOMENDADO):
// - VITE_API_SERVER_PRIMARY: Servidor principal
// - VITE_API_SERVER_BACKUP1: Servidor backup 1
// - VITE_API_SERVER_BACKUP2: Servidor backup 2 (opcional)
// - VITE_API_SERVERS: Lista completa separada por vírgula (alternativa)
// ============================================================================

// Carregar servidores do .env ou usar padrão
function loadApiServers(): string[] {
  const servers: string[] = []
  
  // Opção 1: Lista completa via VITE_API_SERVERS
  const serversList = import.meta.env.VITE_API_SERVERS as string | undefined
  if (serversList) {
    const parsed = serversList.split(',').map(s => s.trim()).filter(s => s.length > 0)
    if (parsed.length > 0) {
      console.log('✅ Servidores carregados via VITE_API_SERVERS:', parsed)
      return parsed
    }
  }
  
  // Opção 2: Servidores individuais
  const primary = import.meta.env.VITE_API_SERVER_PRIMARY as string | undefined
  const backup1 = import.meta.env.VITE_API_SERVER_BACKUP1 as string | undefined
  const backup2 = import.meta.env.VITE_API_SERVER_BACKUP2 as string | undefined
  
  if (primary) servers.push(primary)
  if (backup1) servers.push(backup1)
  if (backup2) servers.push(backup2)
  
  // Se nenhum servidor foi configurado no .env, usar padrão
  if (servers.length === 0) {
    console.log('ℹ️  Usando servidores padrão (nenhum .env configurado)')
    return [
      'https://api.fartgreen.fun',                                    // Servidor Principal
      'https://licence-api-zsbg.onrender.com',                         // Backup 1 (Render)
      'https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app',      // Backup 2 (Koyeb)
    ]
  }
  
  console.log('✅ Servidores carregados do .env:', servers)
  return servers
}

const API_SERVERS: string[] = loadApiServers()

// Servidor atual que está funcionando (cache)
let currentWorkingServer: string | null = null

// ============================================================================
// FUNÇÃO DE FALLBACK PARA MÚLTIPLOS SERVIDORES
// ============================================================================
interface FetchOptions extends RequestInit {
  timeout?: number
}

async function fetchWithFallback(
  endpoint: string,
  options: FetchOptions = {}
): Promise<Response> {
  // Se temos um servidor que funcionou antes, tentar ele primeiro
  // Mas se falhar, tentar todos os outros
  let servers: string[]
  if (currentWorkingServer && API_SERVERS.includes(currentWorkingServer)) {
    // Tentar servidor que funcionou antes primeiro
    servers = [currentWorkingServer, ...API_SERVERS.filter(s => s !== currentWorkingServer)]
  } else {
    // Tentar todos em ordem
    servers = API_SERVERS
  }
  
  const timeout = options.timeout || 10000 // 10 segundos padrão
  const { timeout: _, ...fetchOptions } = options
  
  let lastError: Error | null = null
  let lastServerTried: string | null = null
  let corsError = false
  
  for (let i = 0; i < servers.length; i++) {
    const server = servers[i]
    const url = `${server}${endpoint}`
    
    // Criar AbortController para timeout
    const controller = new AbortController()
    let timeoutId: number | null = window.setTimeout(() => controller.abort(), timeout)
    
    try {
      // Tentar fetch sem mode cors primeiro (pode funcionar em alguns casos)
      let response: Response
      try {
        response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal,
          mode: 'cors',
          credentials: 'omit',
        })
      } catch (corsError: any) {
        // Se falhar com CORS, tentar sem especificar mode
        if (corsError.message && corsError.message.includes('Failed to fetch')) {
          console.warn(`⚠️  CORS error com ${server}, tentando sem mode...`)
          response = await fetch(url, {
            ...fetchOptions,
            signal: controller.signal,
          })
        } else {
          throw corsError
        }
      }
      
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      
      // Se a resposta foi bem-sucedida, salvar servidor e retornar
      if (response.ok || response.status < 500) {
        currentWorkingServer = server
        localStorage.setItem('apiWorkingServer', server)
        return response
      }
      
      // Se erro 4xx (não autorizado, etc), não tentar outros servidores
      if (response.status >= 400 && response.status < 500) {
        return response
      }
      
      // Erro 5xx, tentar próximo servidor
      lastError = new Error(`Servidor ${server} retornou erro ${response.status}`)
    } catch (error: any) {
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      
      // Erro de rede ou timeout
      let errorMessage = ''
      if (error.name === 'AbortError') {
        errorMessage = `Timeout ao conectar com ${server}`
      } else if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('CORS'))) {
        errorMessage = `Erro de conexão com ${server} (CORS ou servidor offline)`
        corsError = true
        // Se for erro de CORS, limpar cache deste servidor
        if (currentWorkingServer === server) {
          currentWorkingServer = null
          localStorage.removeItem('apiWorkingServer')
        }
      } else {
        errorMessage = `Erro ao conectar com ${server}: ${error.message || 'Erro desconhecido'}`
      }
      
      lastError = new Error(errorMessage)
      lastServerTried = server
      
      // Log para debug (apenas em console)
      console.warn(`❌ Servidor ${server} falhou:`, errorMessage)
      if (i < servers.length - 1) {
        console.log(`🔄 Tentando próximo servidor... (${i + 2}/${servers.length})`)
      }
      
      // Continuar para próximo servidor
      continue
    }
  }
  
  // Se chegou aqui, nenhum servidor funcionou
  // Limpar cache do servidor que estava funcionando
  if (currentWorkingServer) {
    currentWorkingServer = null
    localStorage.removeItem('apiWorkingServer')
  }
  
  // Mensagem de erro mais clara e útil
  let errorMsg = 'Não foi possível conectar aos servidores.'
  const serversList = servers.map(s => new URL(s).hostname).join(', ')
  
  if (corsError) {
    errorMsg = `Não foi possível conectar aos servidores (${serversList}).\n\nO servidor pode estar temporariamente offline ou há um problema de conexão.\n\nTente novamente em alguns instantes.`
  } else if (lastError) {
    errorMsg = `Não foi possível conectar aos servidores (${serversList}).\n\nÚltimo erro: ${lastError.message}\n\nTente novamente em alguns instantes.`
  }
  
  console.error('❌ Todos os servidores falharam:', {
    servidoresTentados: servers,
    ultimoServidor: lastServerTried,
    erro: lastError?.message
  })
  
  throw new Error(errorMsg)
}

// Carregar servidor que funcionou anteriormente
const savedServer = localStorage.getItem('apiWorkingServer')
if (savedServer && API_SERVERS.includes(savedServer)) {
  currentWorkingServer = savedServer
}

// Compatibilidade: se VITE_API_BASE_URL estiver definido, adicionar como fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined
if (API_BASE_URL && !API_SERVERS.includes(API_BASE_URL)) {
  API_SERVERS.push(API_BASE_URL)
  console.log('ℹ️  Servidor adicional adicionado via VITE_API_BASE_URL:', API_BASE_URL)
}

// Log final dos servidores configurados (apenas em desenvolvimento)
if (import.meta.env.DEV) {
  console.log('📡 Servidores API configurados:', API_SERVERS)
}

// Log final dos servidores configurados
console.log('📡 Servidores API configurados:', API_SERVERS)

// Roteamento simples baseado em hash
function getRoute(): string {
  const hash = window.location.hash.slice(1) || '/'
  return hash
}

function navigateTo(route: string) {
  window.location.hash = route
  window.dispatchEvent(new Event('hashchange'))
}

type Device = {
  id: number
  device_id: string
  owner_name: string | null
  cpf: string | null
  email: string | null
  address: string | null
  license_type: string
  status: string
  start_date: string
  end_date: string | null
  last_seen_at: string | null
  last_seen_ip: string | null
  last_hostname: string | null
  last_version: string | null
  created_by?: string | null
}

type LoginResponse = {
  token: string
  must_change_password: boolean
  role?: string
}

type User = {
  id: number
  username: string
  email: string | null
  role: string
  created_at: string
}

let authToken: string | null = null
let userRole: string = 'admin' // Padrão admin para compatibilidade

async function fetchHealth(): Promise<string> {
  try {
    const res = await fetchWithFallback('/health', { timeout: 5000 })
    const data = await res.json()
    const serverName = currentWorkingServer 
      ? new URL(currentWorkingServer).hostname 
      : 'desconhecido'
    return `API: ${data.status} (HTTP ${res.status}) - Servidor: ${serverName}`
  } catch (error: any) {
    return `Erro: ${error.message || 'Não foi possível conectar aos servidores'}`
  }
}

async function fetchDevices(): Promise<Device[]> {
  try {
    const res = await fetchWithFallback('/admin/devices', {
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    })
    if (!res.ok) return []
    const data = await res.json()
    return data.items ?? []
  } catch (error) {
    console.error('Erro ao buscar dispositivos:', error)
    return []
  }
}

async function fetchUsers(): Promise<User[]> {
  try {
    const res = await fetchWithFallback('/admin/users', {
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    })
    if (!res.ok) return []
    const data = await res.json()
    return data.items ?? []
  } catch (error) {
    console.error('Erro ao buscar usuários:', error)
    return []
  }
}

async function createUser(username: string, password: string, email: string, role: string = 'user'): Promise<void> {
  if (!authToken) throw new Error('Não autenticado')
  const res = await fetchWithFallback('/admin/users/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ username, password, email, role }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao criar usuário')
  }
}

async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetchWithFallback('/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Falha no login')
  }
  return res.json()
}

async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  if (!authToken) throw new Error('Não autenticado')
  const res = await fetchWithFallback('/admin/change-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao trocar senha')
  }
}

async function getUserProfile(): Promise<{ username: string; email: string | null; role: string; created_at: string }> {
  if (!authToken) throw new Error('Não autenticado')
  try {
    const res = await fetchWithFallback('/user/profile', {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
      timeout: 15000, // 15 segundos para perfil
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || 'Erro ao buscar perfil')
    }
    return res.json()
  } catch (error: any) {
    console.error('Erro ao buscar perfil:', error)
    throw new Error(`Erro ao buscar perfil: ${error.message || 'Erro desconhecido'}`)
  }
}

async function updateUserProfile(email: string): Promise<void> {
  if (!authToken) throw new Error('Não autenticado')
  const res = await fetchWithFallback('/user/profile', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ email }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao atualizar perfil')
  }
}

async function forgotPassword(email: string): Promise<void> {
  const res = await fetchWithFallback('/auth/forgot-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao solicitar recuperação de senha')
  }
}

async function resetPassword(token: string, newPassword: string): Promise<void> {
  const res = await fetchWithFallback('/auth/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token, new_password: newPassword }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao redefinir senha')
  }
}

async function deactivateLicense(deviceId: string): Promise<void> {
  if (!authToken) throw new Error('Não autenticado')
  const res = await fetchWithFallback(`/admin/devices/${encodeURIComponent(deviceId)}/deactivate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ action: 'block' }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao desativar licença')
  }
}

async function reactivateLicense(deviceId: string): Promise<void> {
  if (!authToken) throw new Error('Não autenticado')
  const res = await fetchWithFallback(`/admin/devices/${encodeURIComponent(deviceId)}/deactivate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ action: 'activate' }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Erro ao reativar licença')
  }
}

async function deleteLicense(deviceId: string): Promise<void> {
  if (!authToken) throw new Error('Não autenticado')
  
  try {
    const res = await fetchWithFallback(`/admin/devices/${encodeURIComponent(deviceId)}/delete`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      timeout: 15000, // 15 segundos para exclusão
    })
    
    if (!res.ok) {
      let errorMessage = 'Erro ao excluir licença'
      try {
        const text = await res.text()
        if (text) {
          try {
            const json = JSON.parse(text)
            errorMessage = json.error || json.message || text
          } catch {
            errorMessage = text
          }
        }
      } catch {
        errorMessage = `Erro HTTP ${res.status}: ${res.statusText}`
      }
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    // Melhorar mensagem de erro para CORS ou servidor offline
    if (error.message?.includes('CORS') || error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
      throw new Error('Não foi possível conectar aos servidores. Verifique sua conexão ou tente novamente mais tarde.')
    }
    throw error
  }
}

// Função para calcular estatísticas dos dispositivos
function calculateStats(devices: Device[]) {
  const stats = {
    total: devices.length,
    byType: {} as Record<string, number>,
    byStatus: {} as Record<string, number>,
    active: 0,
    expired: 0,
    expiring: 0,
  }
  
  devices.forEach((d) => {
    stats.byType[d.license_type] = (stats.byType[d.license_type] || 0) + 1
    stats.byStatus[d.status] = (stats.byStatus[d.status] || 0) + 1
    
    if (d.status === 'active') stats.active++
    
    if (d.end_date) {
      const end = new Date(d.end_date)
      const now = new Date()
      const diffDays = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
      if (diffDays < 0) stats.expired++
      else if (diffDays <= 7) stats.expiring++
    }
  })
  
  return stats
}

// Função para renderizar gráfico de pizza (usando SVG)
function renderPieChart(data: Record<string, number>, containerId: string, title: string) {
  const container = document.getElementById(containerId)
  if (!container) return
  
  const entries = Object.entries(data).filter(([_, v]) => v > 0)
  if (entries.length === 0) {
    container.innerHTML = `<p style="text-align: center; color: #6b7280;">Sem dados para exibir</p>`
    return
  }
  
  const total = entries.reduce((sum, [_, v]) => sum + v, 0)
  const colors = ['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899']
  
  let currentAngle = -90
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('viewBox', '0 0 200 200')
  svg.setAttribute('width', '200')
  svg.setAttribute('height', '200')
  svg.style.maxWidth = '100%'
  
  const centerX = 100
  const centerY = 100
  const radius = 80
  
  entries.forEach(([label, value], index) => {
    const percentage = (value / total) * 100
    const angle = (value / total) * 360
    
    const startAngle = currentAngle
    const endAngle = currentAngle + angle
    
    const x1 = centerX + radius * Math.cos((startAngle * Math.PI) / 180)
    const y1 = centerY + radius * Math.sin((startAngle * Math.PI) / 180)
    const x2 = centerX + radius * Math.cos((endAngle * Math.PI) / 180)
    const y2 = centerY + radius * Math.sin((endAngle * Math.PI) / 180)
    
    const largeArc = angle > 180 ? 1 : 0
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.setAttribute(
      'd',
      `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`
    )
    path.setAttribute('fill', colors[index % colors.length])
    path.setAttribute('stroke', '#fff')
    path.setAttribute('stroke-width', '2')
    path.style.cursor = 'pointer'
    path.setAttribute('title', `${label}: ${value} (${percentage.toFixed(1)}%)`)
    svg.appendChild(path)
    
    currentAngle += angle
  })
  
  const legend = entries
    .map(
      ([label, value], index) => `
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
      <div style="width: 16px; height: 16px; background: ${colors[index % colors.length]}; border-radius: 4px;"></div>
      <span style="font-size: 0.875rem;">${label}: <strong>${value}</strong></span>
    </div>
  `
    )
    .join('')
  
  container.innerHTML = `
    <div style="text-align: center; margin-bottom: 1rem;">
      <h3 style="margin: 0 0 1rem; font-size: 1.1rem; color: #1f2937;">${title}</h3>
      <div style="display: flex; justify-content: center;">${svg.outerHTML}</div>
    </div>
    <div style="margin-top: 1rem;">${legend}</div>
  `
}

// Landing Page Pública
function showLandingPage() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  app.innerHTML = `
    <div class="landing-page">
      <header class="landing-header">
        <div class="landing-container">
          <h1 class="landing-logo">Easy Play Rockola</h1>
          <nav class="landing-nav">
            <a href="#dashboard" class="landing-nav-link">Acessar Dashboard</a>
          </nav>
        </div>
      </header>
      
      <section class="landing-hero">
        <div class="landing-container">
          <h2 class="landing-hero-title">Sistema de Licenciamento Profissional</h2>
          <p class="landing-hero-subtitle">
            Gerencie suas licenças de software de forma simples, segura e eficiente.
          </p>
          <div class="landing-hero-buttons">
            <a href="#dashboard" class="landing-btn landing-btn-primary">Acessar Dashboard</a>
            <a href="#sobre" class="landing-btn landing-btn-secondary">Saiba Mais</a>
          </div>
        </div>
      </section>
      
      <section class="landing-features">
        <div class="landing-container">
          <h2 class="landing-section-title">Recursos Principais</h2>
          <div class="landing-features-grid">
            <div class="landing-feature-card">
              <div class="landing-feature-icon">🔒</div>
              <h3>Segurança</h3>
              <p>Proteção avançada contra pirataria e clonagem de licenças</p>
            </div>
            <div class="landing-feature-card">
              <div class="landing-feature-icon">📊</div>
              <h3>Dashboard Completo</h3>
              <p>Visualize estatísticas e gerencie todas as licenças em um só lugar</p>
            </div>
            <div class="landing-feature-card">
              <div class="landing-feature-icon">⚡</div>
              <h3>Rápido e Eficiente</h3>
              <p>Sistema otimizado para máxima performance e confiabilidade</p>
            </div>
            <div class="landing-feature-card">
              <div class="landing-feature-icon">📧</div>
              <h3>Notificações</h3>
              <p>Alertas automáticos por email sobre expiração de licenças</p>
            </div>
          </div>
        </div>
      </section>
      
      <section class="landing-cta">
        <div class="landing-container">
          <h2 class="landing-cta-title">Pronto para começar?</h2>
          <p class="landing-cta-subtitle">Acesse o dashboard e gerencie suas licenças agora mesmo</p>
          <a href="#dashboard" class="landing-btn landing-btn-primary landing-btn-large">Acessar Dashboard</a>
        </div>
      </section>
      
      <footer class="landing-footer">
        <div class="landing-container">
          <p>&copy; ${new Date().getFullYear()} Easy Play Rockola. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  `
  
  // Interceptar cliques nos links do dashboard
  document.querySelectorAll('a[href="#dashboard"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault()
      navigateTo('/dashboard')
    })
  })
}

// Login do Dashboard
function showLogin() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>Dashboard de Licenciamento</h1>
      </div>
      <div class="app-content">
        <p class="subtitle">Entre como administrador para gerenciar licenças.</p>
        <form id="login-form">
          <div class="form-group">
            <label>Usuário</label>
            <input name="username" required />
          </div>
          <div class="form-group">
            <label>Senha</label>
            <input name="password" type="password" required />
          </div>
          <button type="submit">Entrar</button>
          <div style="text-align: center; margin-top: 1rem;">
            <a href="#" id="forgot-password-link" style="color: #667eea; text-decoration: none; font-size: 0.875rem;">Esqueceu a senha?</a>
          </div>
        </form>
      </div>
    </main>
  `
  
  const forgotPasswordLink = document.getElementById('forgot-password-link')
  forgotPasswordLink?.addEventListener('click', (e) => {
    e.preventDefault()
    showForgotPassword()
  })
  
  const loginForm = document.querySelector<HTMLFormElement>('#login-form')
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const fd = new FormData(loginForm)
    const username = fd.get('username')?.toString() ?? ''
    const password = fd.get('password')?.toString() ?? ''
      try {
        const resp = await login(username, password)
        authToken = resp.token
        userRole = resp.role || 'admin'
        localStorage.setItem('adminToken', authToken)
        localStorage.setItem('userRole', userRole)
        if (resp.must_change_password) {
          showChangePassword(true)
        } else {
          await showDashboard()
        }
      } catch (err: any) {
        let errorMessage = err?.message ?? 'Falha no login'
        
        // Melhorar mensagem de erro de conexão
        if (errorMessage.includes('servidores falharam') || errorMessage.includes('conectar aos servidores')) {
          errorMessage = 'Não foi possível conectar aos servidores.\n\nOs servidores podem estar temporariamente offline.\n\nTente novamente em alguns instantes ou verifique sua conexão com a internet.'
        } else if (errorMessage.includes('CORS') || errorMessage.includes('offline')) {
          errorMessage = 'Erro de conexão com o servidor.\n\nO servidor pode estar temporariamente offline.\n\nTente novamente em alguns instantes.'
        }
        
        alert(errorMessage)
      }
  })
}

function showChangePassword(isFirstAccess: boolean = false) {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>${isFirstAccess ? 'Primeiro acesso' : 'Alterar Senha'}</h1>
      </div>
      <div class="app-content">
        <p class="subtitle">${isFirstAccess ? 'Defina uma nova senha para o usuário administrador.' : 'Altere sua senha de acesso ao sistema.'}</p>
        ${isFirstAccess ? `
        <div style="background: #fff3cd; border: 2px solid #ffc107; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;">
          <p style="margin: 0; color: #856404; font-size: 0.875rem;">
            <strong>Primeiro acesso:</strong> Digite sua senha atual (padrão: admin123) e defina uma nova senha segura.
          </p>
        </div>
        ` : ''}
        <form id="pwd-form">
          <div class="form-group">
            <label>Senha atual *</label>
            <input name="old_password" type="password" required placeholder="${isFirstAccess ? 'Digite a senha atual (padrão: admin123)' : 'Digite sua senha atual'}" />
          </div>
          <div class="form-group">
            <label>Nova senha *</label>
            <input name="new_password" type="password" required placeholder="Digite a nova senha" minlength="6" />
            <small style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem; display: block;">Mínimo de 6 caracteres</small>
          </div>
          <div class="form-group">
            <label>Confirmar nova senha *</label>
            <input name="confirm_password" type="password" required placeholder="Digite a nova senha novamente" minlength="6" />
          </div>
          <div style="display: flex; gap: 1rem;">
            ${!isFirstAccess ? `
            <button type="button" id="cancel-pwd-btn" style="flex: 1; background: #e5e7eb; color: #374151; padding: 0.875rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer;">Cancelar</button>
            ` : ''}
            <button type="submit" style="flex: 1;">${isFirstAccess ? 'Salvar nova senha' : 'Alterar Senha'}</button>
          </div>
        </form>
      </div>
    </main>
  `
  
  const pwdForm = document.querySelector<HTMLFormElement>('#pwd-form')
  pwdForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const fd = new FormData(pwdForm)
    const oldPassword = fd.get('old_password')?.toString() ?? ''
    const newPassword = fd.get('new_password')?.toString() ?? ''
    const confirmPassword = fd.get('confirm_password')?.toString() ?? ''
    
    if (!oldPassword) {
      alert('Senha atual é obrigatória!')
      return
    }
    
    if (newPassword.length < 6) {
      alert('A nova senha deve ter no mínimo 6 caracteres!')
      return
    }
    
    if (newPassword !== confirmPassword) {
      alert('As senhas não coincidem!')
      return
    }
    
    try {
      await changePassword(oldPassword, newPassword)
      alert('Senha alterada com sucesso!')
      await showDashboard()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao trocar senha')
    }
  })
  
  // Botão cancelar
  const cancelBtn = document.getElementById('cancel-pwd-btn')
  cancelBtn?.addEventListener('click', async () => {
    await showDashboard()
  })
}

async function showUserProfile() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  // Mostrar loading
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>Meu Perfil</h1>
      </div>
      <div class="app-content">
        <p style="text-align: center; color: #6b7280;">Carregando perfil...</p>
      </div>
    </main>
  `
  
  try {
    const profile = await getUserProfile()
    
    app.innerHTML = `
      <main class="app login-card">
        <div class="app-header">
          <h1>Meu Perfil</h1>
        </div>
        <div class="app-content">
          <form id="profile-form">
            <div class="form-group">
              <label>Usuário</label>
              <input type="text" value="${profile.username}" disabled style="background: #f3f4f6; cursor: not-allowed;" />
              <small style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem; display: block;">O nome de usuário não pode ser alterado</small>
            </div>
            <div class="form-group">
              <label>E-mail *</label>
              <input type="email" id="profile-email" value="${profile.email || ''}" placeholder="seu@email.com" />
            </div>
            <div class="form-group">
              <label>Função</label>
              <input type="text" value="${profile.role === 'admin' ? 'Administrador' : 'Usuário Comum'}" disabled style="background: #f3f4f6; cursor: not-allowed;" />
            </div>
            <div class="form-group">
              <label>Conta criada em</label>
              <input type="text" value="${new Date(profile.created_at).toLocaleDateString('pt-BR')}" disabled style="background: #f3f4f6; cursor: not-allowed;" />
            </div>
            <div style="display: flex; gap: 1rem;">
              <button type="button" id="cancel-profile-btn" style="flex: 1; background: #e5e7eb; color: #374151; padding: 0.875rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer;">Cancelar</button>
              <button type="submit" style="flex: 1;">Salvar Alterações</button>
            </div>
          </form>
        </div>
      </main>
    `
    
    const profileForm = document.querySelector<HTMLFormElement>('#profile-form')
    profileForm?.addEventListener('submit', async (e) => {
      e.preventDefault()
      const email = (document.getElementById('profile-email') as HTMLInputElement)?.value || ''
      try {
        await updateUserProfile(email)
        alert('Perfil atualizado com sucesso!')
        await showDashboard()
      } catch (err: any) {
        alert(err?.message ?? 'Erro ao atualizar perfil')
      }
    })
    
    const cancelBtn = document.getElementById('cancel-profile-btn')
    cancelBtn?.addEventListener('click', async () => {
      await showDashboard()
    })
  } catch (err: any) {
    alert(err?.message ?? 'Erro ao carregar perfil')
    await showDashboard()
  }
}

function showForgotPassword() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>Recuperar Senha</h1>
      </div>
      <div class="app-content">
        <p class="subtitle">Digite seu e-mail para receber instruções de recuperação de senha.</p>
        <form id="forgot-password-form">
          <div class="form-group">
            <label>E-mail *</label>
            <input type="email" id="forgot-email" required placeholder="seu@email.com" />
          </div>
          <div style="display: flex; gap: 1rem;">
            <button type="button" id="cancel-forgot-btn" style="flex: 1; background: #e5e7eb; color: #374151; padding: 0.875rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer;">Voltar</button>
            <button type="submit" style="flex: 1;">Enviar Instruções</button>
          </div>
        </form>
      </div>
    </main>
  `
  
  const forgotForm = document.querySelector<HTMLFormElement>('#forgot-password-form')
  forgotForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const email = (document.getElementById('forgot-email') as HTMLInputElement)?.value || ''
    try {
      await forgotPassword(email)
      alert('Se o e-mail existir, você receberá instruções de recuperação de senha.')
      showLogin()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao solicitar recuperação de senha')
    }
  })
  
  const cancelBtn = document.getElementById('cancel-forgot-btn')
  cancelBtn?.addEventListener('click', () => {
    showLogin()
  })
}

function showResetPassword(token: string) {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>Redefinir Senha</h1>
      </div>
      <div class="app-content">
        <p class="subtitle">Digite sua nova senha.</p>
        <form id="reset-password-form">
          <div class="form-group">
            <label>Nova senha *</label>
            <input type="password" id="reset-new-password" required placeholder="Digite a nova senha" minlength="6" />
            <small style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem; display: block;">Mínimo de 6 caracteres</small>
          </div>
          <div class="form-group">
            <label>Confirmar nova senha *</label>
            <input type="password" id="reset-confirm-password" required placeholder="Digite a nova senha novamente" minlength="6" />
          </div>
          <button type="submit" style="width: 100%;">Redefinir Senha</button>
        </form>
      </div>
    </main>
  `
  
  const resetForm = document.querySelector<HTMLFormElement>('#reset-password-form')
  resetForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const newPassword = (document.getElementById('reset-new-password') as HTMLInputElement)?.value || ''
    const confirmPassword = (document.getElementById('reset-confirm-password') as HTMLInputElement)?.value || ''
    
    if (newPassword.length < 6) {
      alert('A nova senha deve ter no mínimo 6 caracteres!')
      return
    }
    
    if (newPassword !== confirmPassword) {
      alert('As senhas não coincidem!')
      return
    }
    
    try {
      await resetPassword(token, newPassword)
      alert('Senha redefinida com sucesso! Você já pode fazer login.')
      showLogin()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao redefinir senha')
    }
  })
}

async function showDashboard() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  const [health, devices, users] = await Promise.all([
    fetchHealth(),
    fetchDevices(),
    fetchUsers(),
  ])
  
  const stats = calculateStats(devices)
  
  app.innerHTML = `
    <main class="app">
      <div class="app-header">
        <h1>Dashboard de Licenciamento</h1>
        <div style="display: flex; gap: 1rem; align-items: center;">
          <a href="#/" style="color: white; text-decoration: none; padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 8px;">Página Inicial</a>
          <button class="logout-btn" id="profile-btn" style="background: rgba(255, 255, 255, 0.15);">Meu Perfil</button>
          <button class="logout-btn" id="change-password-btn" style="background: rgba(255, 255, 255, 0.15);">Alterar Senha</button>
          <button class="logout-btn" id="logout-btn">Sair</button>
        </div>
      </div>
      <div class="app-content">
        <p class="subtitle">${health}</p>
        
        <!-- Estatísticas Rápidas -->
        <section>
          <h2>Estatísticas</h2>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px;">
              <div style="font-size: 0.875rem; opacity: 0.9;">Total de Licenças</div>
              <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">${stats.total}</div>
            </div>
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1.5rem; border-radius: 12px;">
              <div style="font-size: 0.875rem; opacity: 0.9;">Ativas</div>
              <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">${stats.active}</div>
            </div>
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 1.5rem; border-radius: 12px;">
              <div style="font-size: 0.875rem; opacity: 0.9;">Expirando (≤7 dias)</div>
              <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">${stats.expiring}</div>
            </div>
            <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 1.5rem; border-radius: 12px;">
              <div style="font-size: 0.875rem; opacity: 0.9;">Expiradas</div>
              <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">${stats.expired}</div>
            </div>
          </div>
          
          <!-- Gráficos -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
            <div style="background: white; border: 2px solid #e5e7eb; border-radius: 12px; padding: 1.5rem;">
              <div id="chart-by-type"></div>
            </div>
            <div style="background: white; border: 2px solid #e5e7eb; border-radius: 12px; padding: 1.5rem;">
              <div id="chart-by-status"></div>
            </div>
          </div>
        </section>
        
        <!-- Cadastro Rápido -->
        <section>
          <h2>${userRole === 'user' ? 'Criar Licença Gratuita (Ilimitada)' : 'Cadastro Rápido por Device ID'}</h2>
          <div class="quick-form-card">
            <p style="margin: 0 0 1rem; color: #6b7280; font-size: 0.9rem;">
              ${userRole === 'user' 
                ? 'Preencha os campos para criar uma licença gratuita válida por tempo ilimitado. Todos os campos são obrigatórios.' 
                : 'Preencha todos os campos para cadastrar uma nova licença. Todos os campos são obrigatórios.'}
            </p>
            <form id="quick-license-form" style="display: grid; gap: 1rem;">
              <div>
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Device ID *</label>
                <input 
                  type="text" 
                  id="quick-device-id" 
                  required 
                  placeholder="Cole o Device ID aqui (ex: abc123def456...)" 
                  style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 2px solid #e5e7eb; font-family: monospace;"
                />
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                  <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Nome *</label>
                  <input type="text" id="quick-owner-name" required placeholder="Nome completo do cliente" />
                </div>
                <div>
                  <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">CPF *</label>
                  <input type="text" id="quick-cpf" required placeholder="000.000.000-00" maxlength="14" />
                </div>
              </div>
              <div>
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">E-mail *</label>
                <input type="email" id="quick-email" required placeholder="email@exemplo.com" />
              </div>
              <div style="display: grid; grid-template-columns: 150px 1fr; gap: 1rem;">
                <div>
                  <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">CEP *</label>
                  <input 
                    type="text" 
                    id="quick-cep" 
                    required 
                    placeholder="00000-000" 
                    maxlength="9"
                    style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 2px solid #e5e7eb;"
                  />
                </div>
                <div>
                  <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Endereço *</label>
                  <input 
                    type="text" 
                    id="quick-address" 
                    required 
                    placeholder="Rua, número, bairro, cidade/UF (preenchido automaticamente pelo CEP)" 
                    readonly
                    style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 2px solid #e5e7eb; background-color: #f9fafb;"
                  />
                </div>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                  <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Número *</label>
                  <input type="text" id="quick-numero" required placeholder="Número do endereço" />
                </div>
                <div>
                  <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Complemento</label>
                  <input type="text" id="quick-complemento" placeholder="Apto, bloco, etc. (opcional)" />
                </div>
              </div>
              ${userRole === 'admin' ? `
              <div>
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Tipo de Licença *</label>
                <select id="quick-license-type" required style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 2px solid #e5e7eb;">
                  <option value="mensal">Mensal - R$ 19,90/mês</option>
                  <option value="trimestral">Trimestral - R$ 49,90/3 meses</option>
                  <option value="semestral">Semestral - R$ 94,90/6 meses</option>
                  <option value="anual" selected>Anual - R$ 180,00/ano</option>
                  <option value="trianual">Trienal - R$ 499,00/3 anos</option>
                  <option value="vitalicia">Vitalício - R$ 999,00 (único pagamento)</option>
                </select>
              </div>
              ` : `
              <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); padding: 1rem; border-radius: 12px; border: 2px solid #10b981;">
                <p style="margin: 0; color: #065f46; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
                  <span>✓</span> Licença Gratuita - Válida por tempo ilimitado
                </p>
              </div>
              `}
              <button type="submit" style="padding: 0.875rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                ${userRole === 'user' ? 'Criar Licença Gratuita' : 'Criar Licença'}
              </button>
            </form>
          </div>
        </section>
        
        ${userRole === 'admin' ? `
        <!-- Planos -->
        <section>
          <h2>Planos de Licença</h2>
          <div class="pricing-carousel-wrapper">
            <button class="carousel-btn carousel-btn-prev" aria-label="Plano anterior">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
            </button>
            <div class="pricing-carousel-container">
              <div class="pricing-carousel-track">
                <div class="pricing-card" data-type="mensal">
                  <div class="pricing-header">
                    <h3>Mensal</h3>
                    <div class="pricing-price-original">De: R$ 20,95</div>
                    <div class="pricing-price">R$ 19,90<span>/mês</span></div>
                    <div class="pricing-badge">5% OFF</div>
                  </div>
                  <ul class="pricing-features">
                    <li>Licença válida por 1 mês</li>
                    <li>Suporte completo</li>
                    <li>Atualizações incluídas</li>
                  </ul>
                  <button class="pricing-btn" onclick="selectPlan('mensal')">Selecionar</button>
                </div>
                
                <div class="pricing-card" data-type="trimestral">
                  <div class="pricing-header">
                    <h3>Trimestral</h3>
                    <div class="pricing-price-original">De: R$ 59,70</div>
                    <div class="pricing-price">R$ 49,90<span>/3 meses</span></div>
                    <div class="pricing-badge">16% OFF</div>
                  </div>
                  <ul class="pricing-features">
                    <li>Licença válida por 3 meses</li>
                    <li>Suporte completo</li>
                    <li>Atualizações incluídas</li>
                  </ul>
                  <button class="pricing-btn" onclick="selectPlan('trimestral')">Selecionar</button>
                </div>
                
                <div class="pricing-card" data-type="semestral">
                  <div class="pricing-header">
                    <h3>Semestral</h3>
                    <div class="pricing-price-original">De: R$ 119,40</div>
                    <div class="pricing-price">R$ 94,90<span>/6 meses</span></div>
                    <div class="pricing-badge">21% OFF</div>
                  </div>
                  <ul class="pricing-features">
                    <li>Licença válida por 6 meses</li>
                    <li>Suporte completo</li>
                    <li>Atualizações incluídas</li>
                  </ul>
                  <button class="pricing-btn" onclick="selectPlan('semestral')">Selecionar</button>
                </div>
                
                <div class="pricing-card featured" data-type="anual">
                  <div class="pricing-header">
                    <h3>Anual</h3>
                    <div class="pricing-price-original">De: R$ 238,80</div>
                    <div class="pricing-price">R$ 180,00<span>/ano</span></div>
                    <div class="pricing-badge">Mais Popular - 25% OFF</div>
                  </div>
                  <ul class="pricing-features">
                    <li>Licença válida por 1 ano</li>
                    <li>Suporte completo</li>
                    <li>Atualizações incluídas</li>
                  </ul>
                  <button class="pricing-btn" onclick="selectPlan('anual')">Selecionar</button>
                </div>
                
                <div class="pricing-card" data-type="trianual">
                  <div class="pricing-header">
                    <h3>Trienal</h3>
                    <div class="pricing-price-original">De: R$ 716,40</div>
                    <div class="pricing-price">R$ 499,00<span>/3 anos</span></div>
                    <div class="pricing-badge">Melhor Valor - 30% OFF</div>
                  </div>
                  <ul class="pricing-features">
                    <li>Licença válida por 3 anos</li>
                    <li>Suporte completo</li>
                    <li>Atualizações incluídas</li>
                  </ul>
                  <button class="pricing-btn" onclick="selectPlan('trianual')">Selecionar</button>
                </div>
                
                <div class="pricing-card" data-type="vitalicia" style="border-color: #f59e0b;">
                  <div class="pricing-header">
                    <h3>Vitalício</h3>
                    <div class="pricing-price-original">De: R$ 1.500,00</div>
                    <div class="pricing-price">R$ 999,00<span> (único)</span></div>
                    <div class="pricing-badge" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">33% OFF</div>
                  </div>
                  <ul class="pricing-features">
                    <li>Licença válida para sempre</li>
                    <li>Suporte vitalício</li>
                    <li>Todas as atualizações</li>
                    <li>Sem renovação</li>
                  </ul>
                  <button class="pricing-btn" onclick="selectPlan('vitalicia')">Selecionar</button>
                </div>
              </div>
            </div>
            <button class="carousel-btn carousel-btn-next" aria-label="Próximo plano">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </button>
            <div class="carousel-dots"></div>
          </div>
        </section>
        ` : ''}
        
        ${userRole === 'admin' ? `
        <!-- Gerenciamento de Usuários -->
        <section>
          <h2>Gerenciar Usuários/Revendedores</h2>
          <div class="quick-form-card" style="margin-bottom: 2rem;">
            <h3 style="margin: 0 0 1rem; font-size: 1.1rem;">Criar Novo Usuário</h3>
            <form id="create-user-form" class="responsive-form-grid">
              <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Usuário *</label>
                <input type="text" id="new-username" required placeholder="nome_usuario" />
              </div>
              <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Senha *</label>
                <input type="password" id="new-password" required placeholder="Senha segura" />
              </div>
              <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">E-mail</label>
                <input type="email" id="new-email" placeholder="email@exemplo.com" />
              </div>
              <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Função *</label>
                <select id="new-role" required style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 2px solid #e5e7eb;">
                  <option value="user">Usuário Comum</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
              <div class="form-group form-group-submit">
                <button type="submit" style="padding: 0.75rem 1.5rem; width: 100%;">Criar Usuário</button>
              </div>
            </form>
          </div>
          
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Usuário</th>
                  <th>E-mail</th>
                  <th>Função</th>
                  <th>Criado em</th>
                </tr>
              </thead>
              <tbody>
                ${users.length === 0 ? `
                  <tr>
                    <td colspan="5" style="text-align: center; padding: 2rem; color: #6b7280;">
                      Nenhum usuário cadastrado ainda.
                    </td>
                  </tr>
                ` : users.map((u) => `
                  <tr>
                    <td>${u.id}</td>
                    <td><strong>${u.username}</strong></td>
                    <td>${u.email || '-'}</td>
                    <td><span class="status-pill status-active">${u.role || 'user'}</span></td>
                    <td>${new Date(u.created_at).toLocaleDateString('pt-BR')}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </section>
        ` : ''}
        
        <!-- Lista de Licenças -->
        <section>
          <h2>Licenças registradas (${devices.length})</h2>
          ${devices.length === 0 ? `
            <div class="empty-state">
              <p>Nenhuma licença cadastrada ainda.</p>
            </div>
          ` : `
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Device ID</th>
                    <th>Nome</th>
                    <th>CPF</th>
                    <th>E-mail</th>
                    <th>Endereço</th>
                    <th>Tipo</th>
                    <th>Status</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Dias Restantes</th>
                    ${userRole === 'admin' ? '<th>Criado por</th>' : ''}
                    <th>Último Acesso</th>
                    <th>IP</th>
                    <th>Host</th>
                    <th>Versão</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  ${devices
                    .map(
                      (d) => `
                    <tr>
                      <td><code style="font-size: 0.8rem;">${d.device_id}</code></td>
                      <td><strong>${d.owner_name ?? '-'}</strong></td>
                      <td>${d.cpf ?? '-'}</td>
                      <td>${d.email ?? '-'}</td>
                      <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${d.address ?? '-'}</td>
                      <td>${d.license_type}</td>
                      <td>
                        <span class="status-pill status-${d.status}">
                          ${d.status}
                        </span>
                      </td>
                      <td>${d.start_date}</td>
                      <td>${d.end_date ?? '-'}</td>
                      <td>${
                        d.end_date
                          ? (() => {
                              const end = new Date(d.end_date)
                              const now = new Date()
                              const diffTime = end.getTime() - now.getTime()
                              const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
                              if (diffDays < 0) {
                                return '<span style="color: #dc2626; font-weight: 600;">Expirada</span>'
                              } else if (diffDays <= 3) {
                                return `<span style="color: #dc2626; font-weight: 600;">${diffDays} ${diffDays === 1 ? 'dia' : 'dias'}</span>`
                              } else if (diffDays <= 7) {
                                return `<span style="color: #f59e0b; font-weight: 600;">${diffDays} dias</span>`
                              } else {
                                return `<span style="color: #10b981;">${diffDays} dias</span>`
                              }
                            })()
                          : d.license_type === 'vitalicia' ? '<span style="color: #10b981; font-weight: 600;">Vitalício</span>' : '-'
                      }</td>
                      ${userRole === 'admin' ? `<td>${d.created_by ?? '-'}</td>` : ''}
                      <td>${d.last_seen_at ? new Date(d.last_seen_at).toLocaleString('pt-BR') : '-'}</td>
                      <td>${d.last_seen_ip ?? '-'}</td>
                      <td>${d.last_hostname ?? '-'}</td>
                      <td>${d.last_version ?? '-'}</td>
                      <td>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                          ${d.status === 'active' ? `
                            <button 
                              class="action-btn action-btn-warning" 
                              data-action="deactivate" 
                              data-device-id="${d.device_id}"
                              title="Desativar licença"
                              style="padding: 0.5rem 1rem; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.875rem; font-weight: 600; transition: all 0.2s;"
                              onmouseover="this.style.transform='scale(1.05)'"
                              onmouseout="this.style.transform='scale(1)'"
                            >
                              Desativar
                            </button>
                          ` : d.status === 'blocked' ? `
                            <button 
                              class="action-btn action-btn-success" 
                              data-action="activate" 
                              data-device-id="${d.device_id}"
                              title="Reativar licença"
                              style="padding: 0.5rem 1rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.875rem; font-weight: 600; transition: all 0.2s;"
                              onmouseover="this.style.transform='scale(1.05)'"
                              onmouseout="this.style.transform='scale(1)'"
                            >
                              Reativar
                            </button>
                          ` : ''}
                          ${userRole === 'admin' ? `
                            <button 
                              class="action-btn action-btn-danger" 
                              data-action="delete" 
                              data-device-id="${d.device_id}"
                              title="Excluir licença permanentemente"
                              style="padding: 0.5rem 1rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.875rem; font-weight: 600; transition: all 0.2s;"
                              onmouseover="this.style.transform='scale(1.05)'"
                              onmouseout="this.style.transform='scale(1)'"
                            >
                              Excluir
                            </button>
                          ` : ''}
                        </div>
                      </td>
                    </tr>
                  `,
                    )
                    .join('')}
                </tbody>
              </table>
            </div>
          `}
        </section>
      </div>
    </main>
  `
  
  // Renderizar gráficos
  renderPieChart(stats.byType, 'chart-by-type', 'Licenças por Tipo')
  renderPieChart(stats.byStatus, 'chart-by-status', 'Licenças por Status')
  
  // Event listeners para ações de licenças
  document.querySelectorAll('[data-action="deactivate"]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const deviceId = (e.target as HTMLElement).getAttribute('data-device-id')
      if (!deviceId) return
      
      if (!confirm(`Tem certeza que deseja DESATIVAR a licença ${deviceId}?`)) {
        return
      }
      
      try {
        await deactivateLicense(deviceId)
        alert('Licença desativada com sucesso!')
        await showDashboard()
      } catch (err: any) {
        alert(err?.message ?? 'Erro ao desativar licença')
      }
    })
  })
  
  document.querySelectorAll('[data-action="activate"]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const deviceId = (e.target as HTMLElement).getAttribute('data-device-id')
      if (!deviceId) return
      
      if (!confirm(`Tem certeza que deseja REATIVAR a licença ${deviceId}?`)) {
        return
      }
      
      try {
        await reactivateLicense(deviceId)
        alert('Licença reativada com sucesso!')
        await showDashboard()
      } catch (err: any) {
        alert(err?.message ?? 'Erro ao reativar licença')
      }
    })
  })
  
  document.querySelectorAll('[data-action="delete"]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const deviceId = (e.target as HTMLElement).getAttribute('data-device-id')
      if (!deviceId) return
      
      if (!confirm(`⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!\n\nTem certeza que deseja EXCLUIR PERMANENTEMENTE a licença ${deviceId}?`)) {
        return
      }
      
      // Confirmação dupla para exclusão
      if (!confirm(`Confirmação final: Excluir a licença ${deviceId}?\n\nEsta ação não pode ser desfeita!`)) {
        return
      }
      
      try {
        await deleteLicense(deviceId)
        alert('Licença excluída permanentemente!')
        await showDashboard()
      } catch (err: any) {
        // Melhorar mensagem de erro para o usuário
        let errorMsg = err?.message ?? 'Erro ao excluir licença'
        if (errorMsg.includes('CORS') || errorMsg.includes('servidor offline') || errorMsg.includes('conectar aos servidores')) {
          errorMsg = 'Não foi possível conectar aos servidores. Verifique sua conexão com a internet e tente novamente.\n\nSe o problema persistir, o servidor pode estar temporariamente offline.'
        }
        alert(errorMsg)
      }
    })
  })
  
  // Event listeners
  const logoutBtn = document.querySelector<HTMLButtonElement>('#logout-btn')
  logoutBtn?.addEventListener('click', () => {
    authToken = null
    userRole = 'admin'
    localStorage.removeItem('adminToken')
    localStorage.removeItem('userRole')
    navigateTo('/')
    showLandingPage()
  })
  
  // Botão alterar senha
  const changePasswordBtn = document.querySelector<HTMLButtonElement>('#change-password-btn')
  changePasswordBtn?.addEventListener('click', () => {
    showChangePassword(false)
  })
  
  // Botão perfil
  const profileBtn = document.querySelector<HTMLButtonElement>('#profile-btn')
  profileBtn?.addEventListener('click', () => {
    showUserProfile()
  })
  
  // Máscara de CPF
  const cpfInput = document.getElementById('quick-cpf') as HTMLInputElement
  cpfInput?.addEventListener('input', (e) => {
    let value = (e.target as HTMLInputElement).value.replace(/\D/g, '')
    if (value.length <= 11) {
      value = value.replace(/(\d{3})(\d)/, '$1.$2')
      value = value.replace(/(\d{3})(\d)/, '$1.$2')
      value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2')
      ;(e.target as HTMLInputElement).value = value
    }
  })
  
  // Máscara de CEP
  const cepInput = document.getElementById('quick-cep') as HTMLInputElement
  cepInput?.addEventListener('input', (e) => {
    let value = (e.target as HTMLInputElement).value.replace(/\D/g, '')
    if (value.length <= 8) {
      value = value.replace(/(\d{5})(\d)/, '$1-$2')
      ;(e.target as HTMLInputElement).value = value
    }
  })
  
  // Busca automática de endereço por CEP
  cepInput?.addEventListener('blur', async (e) => {
    const cep = (e.target as HTMLInputElement).value.replace(/\D/g, '')
    const addressInput = document.getElementById('quick-address') as HTMLInputElement
    const numeroInput = document.getElementById('quick-numero') as HTMLInputElement
    
    if (cep.length === 8 && addressInput) {
      try {
        addressInput.style.backgroundColor = '#fff3cd'
        addressInput.placeholder = 'Buscando endereço...'
        
        const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`)
        const data = await res.json()
        
        if (data.erro) {
          addressInput.style.backgroundColor = '#f9fafb'
          addressInput.placeholder = 'CEP não encontrado. Digite o endereço manualmente'
          addressInput.readOnly = false
          addressInput.value = ''
          return
        }
        
        const enderecoParts = []
        if (data.logradouro) enderecoParts.push(data.logradouro)
        if (data.bairro) enderecoParts.push(data.bairro)
        if (data.localidade && data.uf) enderecoParts.push(`${data.localidade}/${data.uf}`)
        if (cep) enderecoParts.push(`CEP ${cep.replace(/(\d{5})(\d{3})/, '$1-$2')}`)
        
        addressInput.value = enderecoParts.join(' - ')
        addressInput.style.backgroundColor = '#d1fae5'
        addressInput.readOnly = false
        
        if (numeroInput) {
          numeroInput.focus()
        }
        
        setTimeout(() => {
          addressInput.style.backgroundColor = '#f9fafb'
        }, 2000)
      } catch (error) {
        addressInput.style.backgroundColor = '#f9fafb'
        addressInput.placeholder = 'Erro ao buscar CEP. Digite o endereço manualmente'
        addressInput.readOnly = false
        addressInput.value = ''
      }
    } else if (cep.length > 0 && cep.length < 8) {
      addressInput.style.backgroundColor = '#f9fafb'
      addressInput.placeholder = 'CEP incompleto. Digite o endereço manualmente'
      addressInput.readOnly = false
      addressInput.value = ''
    }
  })
  
  // Formulário rápido de licença
  const quickForm = document.querySelector<HTMLFormElement>('#quick-license-form')
  quickForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const deviceId = (document.getElementById('quick-device-id') as HTMLInputElement)?.value.trim()
    const licenseTypeSelect = document.getElementById('quick-license-type') as HTMLSelectElement
    const licenseType = userRole === 'admin' ? licenseTypeSelect?.value : 'vitalicia'
    const ownerName = (document.getElementById('quick-owner-name') as HTMLInputElement)?.value.trim()
    const cpf = (document.getElementById('quick-cpf') as HTMLInputElement)?.value.trim()
    const email = (document.getElementById('quick-email') as HTMLInputElement)?.value.trim()
    const cep = (document.getElementById('quick-cep') as HTMLInputElement)?.value.trim()
    const addressBase = (document.getElementById('quick-address') as HTMLInputElement)?.value.trim()
    const numero = (document.getElementById('quick-numero') as HTMLInputElement)?.value.trim()
    const complemento = (document.getElementById('quick-complemento') as HTMLInputElement)?.value.trim()
    
    if (!deviceId || (userRole === 'admin' && !licenseType) || !ownerName || !cpf || !email || !cep || !addressBase || !numero) {
      alert('Todos os campos obrigatórios devem ser preenchidos!')
      return
    }
    
    const addressParts = [addressBase]
    if (numero) addressParts[0] = addressBase.replace(/^(.+?)(\s|$)/, `$1, ${numero}$2`)
    if (complemento) addressParts.push(complemento)
    const address = addressParts.join(' - ')
    
    try {
      let res
      if (userRole === 'user') {
        // Usuário comum usa endpoint de licença gratuita
        res = await fetchWithFallback('/user/devices/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
          },
          body: JSON.stringify({
            device_id: deviceId,
            owner_name: ownerName,
            cpf: cpf.replace(/\D/g, ''),
            email: email,
            address: address,
          }),
        })
      } else {
        // Admin usa endpoint normal
        res = await fetchWithFallback('/admin/devices/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
          },
          body: JSON.stringify({
            device_id: deviceId,
            license_type: licenseType,
            owner_name: ownerName,
            cpf: cpf.replace(/\D/g, ''),
            email: email,
            address: address,
          }),
        })
      }
      
      if (!res.ok) {
        const text = await res.text()
        alert(`Erro: ${text}`)
        return
      }
      
      alert(userRole === 'user' 
        ? 'Licença gratuita ilimitada criada com sucesso!' 
        : `Licença ${licenseType} criada com sucesso!`)
      location.reload()
    } catch (err: any) {
      alert(`Erro: ${err?.message || 'Erro ao criar licença'}`)
    }
  })
  
  // Formulário de criar usuário
  const createUserForm = document.querySelector<HTMLFormElement>('#create-user-form')
  createUserForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const username = (document.getElementById('new-username') as HTMLInputElement)?.value.trim()
    const password = (document.getElementById('new-password') as HTMLInputElement)?.value.trim()
    const email = (document.getElementById('new-email') as HTMLInputElement)?.value.trim()
    const role = (document.getElementById('new-role') as HTMLSelectElement)?.value || 'user'
    
    if (!username || !password) {
      alert('Usuário e senha são obrigatórios!')
      return
    }
    
    try {
      await createUser(username, password, email, role)
      alert('Usuário criado com sucesso!')
      location.reload()
    } catch (err: any) {
      alert(err?.message || 'Erro ao criar usuário')
    }
  })
  
  // Função para selecionar plano nos cards
  ;(window as any).selectPlan = (type: string) => {
    const select = document.getElementById('quick-license-type') as HTMLSelectElement
    if (select) {
      select.value = type
      document.getElementById('quick-device-id')?.focus()
    }
  }
  
  // Inicializar carrossel de planos
  if (userRole === 'admin') {
    initPricingCarousel()
  }
}

// Função para inicializar o carrossel de planos
function initPricingCarousel() {
  const track = document.querySelector<HTMLDivElement>('.pricing-carousel-track')
  const prevBtn = document.querySelector<HTMLButtonElement>('.carousel-btn-prev')
  const nextBtn = document.querySelector<HTMLButtonElement>('.carousel-btn-next')
  const dotsContainer = document.querySelector<HTMLDivElement>('.carousel-dots')
  
  if (!track || !prevBtn || !nextBtn) return
  
  const cards = track.querySelectorAll<HTMLDivElement>('.pricing-card')
  const totalCards = cards.length
  let currentIndex = 0
  
  // Calcular quantos cards mostrar por vez baseado na largura da tela
  function getCardsPerView(): number {
    const width = window.innerWidth
    if (width < 640) return 1      // Mobile
    if (width < 1024) return 2      // Tablet
    if (width < 1440) return 3      // Desktop pequeno
    return 4                         // Desktop grande
  }
  
  // Criar dots indicadores
  function createDots() {
    if (!dotsContainer) return
    dotsContainer.innerHTML = ''
    const cardsPerView = getCardsPerView()
    const totalDots = Math.ceil(totalCards / cardsPerView)
    
    for (let i = 0; i < totalDots; i++) {
      const dot = document.createElement('button')
      dot.className = 'carousel-dot'
      dot.setAttribute('aria-label', `Ir para slide ${i + 1}`)
      if (i === 0) dot.classList.add('active')
      dot.addEventListener('click', () => goToSlide(i))
      dotsContainer.appendChild(dot)
    }
  }
  
  // Atualizar posição do carrossel
  function updateCarousel() {
    if (!track || !prevBtn || !nextBtn) return
    
    const cardsPerView = getCardsPerView()
    const cardWidth = track.offsetWidth / cardsPerView
    const maxIndex = Math.max(0, Math.ceil(totalCards / cardsPerView) - 1)
    
    // Limitar índice
    currentIndex = Math.max(0, Math.min(currentIndex, maxIndex))
    
    // Calcular offset suave
    const offset = -currentIndex * cardWidth * cardsPerView
    track.style.transform = `translateX(${offset}px)`
    
    // Atualizar botões
    prevBtn.disabled = currentIndex === 0
    nextBtn.disabled = currentIndex >= maxIndex
    
    // Atualizar dots
    const dots = dotsContainer?.querySelectorAll('.carousel-dot')
    dots?.forEach((dot, index) => {
      dot.classList.toggle('active', index === currentIndex)
    })
  }
  
  // Ir para slide específico
  function goToSlide(index: number) {
    currentIndex = index
    updateCarousel()
  }
  
  // Próximo slide
  function nextSlide() {
    const cardsPerView = getCardsPerView()
    const maxIndex = Math.max(0, Math.ceil(totalCards / cardsPerView) - 1)
    if (currentIndex < maxIndex) {
      currentIndex++
      updateCarousel()
    }
  }
  
  // Slide anterior
  function prevSlide() {
    if (currentIndex > 0) {
      currentIndex--
      updateCarousel()
    }
  }
  
  // Event listeners
  prevBtn.addEventListener('click', prevSlide)
  nextBtn.addEventListener('click', nextSlide)
  
  // Touch/swipe support
  let touchStartX = 0
  let touchEndX = 0
  
  if (track) {
    track.addEventListener('touchstart', (e) => {
      touchStartX = e.touches[0].clientX
    }, { passive: true })
    
    track.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].clientX
      handleSwipe()
    }, { passive: true })
  }
  
  function handleSwipe() {
    const swipeThreshold = 50
    const diff = touchStartX - touchEndX
    
    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        nextSlide()
      } else {
        prevSlide()
      }
    }
  }
  
  // Inicializar
  createDots()
  updateCarousel()
  
  // Recalcular em resize
  let resizeTimeout: number
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout)
    resizeTimeout = window.setTimeout(() => {
      createDots()
      updateCarousel()
    }, 250)
  })
}

// Router principal
async function router() {
  const route = getRoute()
  authToken = localStorage.getItem('adminToken')
  userRole = localStorage.getItem('userRole') || 'admin'
  
  if (route === '/dashboard') {
    if (!authToken) {
      showLogin()
    } else {
      try {
        await showDashboard()
      } catch {
        authToken = null
        userRole = 'admin'
        localStorage.removeItem('adminToken')
        localStorage.removeItem('userRole')
        showLogin()
      }
    }
  } else if (route.startsWith('/reset-password')) {
    const params = new URLSearchParams(window.location.hash.split('?')[1])
    const token = params.get('token')
    if (token) {
      showResetPassword(token)
    } else {
      showLogin()
    }
  } else {
    showLandingPage()
  }
}

// Inicializar
async function bootstrap() {
  window.addEventListener('hashchange', router)
  await router()
}

bootstrap()
