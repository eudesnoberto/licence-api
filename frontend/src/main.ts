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
      'https://licence-api-6evg.onrender.com',                         // Backup 1 (Render)
      'https://thick-beverly-easyplayrockola-37418eab.koyeb.app',      // Backup 2 (Koyeb)
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

// Cache de dados
let devicesCache: { data: Device[]; timestamp: number } | null = null
const CACHE_DURATION = 30000 // 30 segundos

async function fetchDevices(useCache: boolean = true): Promise<Device[]> {
  // Verificar cache
  if (useCache && devicesCache) {
    const now = Date.now()
    if (now - devicesCache.timestamp < CACHE_DURATION) {
      if (import.meta.env.DEV) {
        console.log('📦 Usando cache de dispositivos')
      }
      return devicesCache.data
    }
  }
  
  try {
    if (import.meta.env.DEV) {
      console.log('🔍 Buscando dispositivos...')
    }
    const res = await fetchWithFallback('/admin/devices', {
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    })
    
    if (!res.ok) {
      const errorText = await res.text()
      if (import.meta.env.DEV) {
        console.error('❌ Erro na resposta:', { status: res.status, error: errorText })
      }
      return devicesCache?.data || []
    }
    
    const data = await res.json()
    
    // Verificar diferentes formatos de resposta
    let devices: Device[] = []
    if (Array.isArray(data)) {
      devices = data
    } else if (data.items && Array.isArray(data.items)) {
      devices = data.items
    } else if (data.devices && Array.isArray(data.devices)) {
      devices = data.devices
    }
    
    // Atualizar cache
    devicesCache = { data: devices, timestamp: Date.now() }
    
    if (import.meta.env.DEV) {
      console.log('✅ Dados recebidos:', devices.length, 'itens')
    }
    
    return devices
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('❌ Erro ao buscar dispositivos:', error)
    }
    return devicesCache?.data || []
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
    let errorMessage = 'Falha no login'
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
    let errorMessage = 'Erro ao solicitar recuperação de senha'
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
    
    // Mensagens específicas para erros comuns
    if (errorMessage.includes('SMTP') || errorMessage.includes('email não está habilitada')) {
      errorMessage = 'O envio de emails não está configurado no servidor. Entre em contato com o administrador.'
    } else if (errorMessage.includes('Erro ao enviar email')) {
      errorMessage = 'Não foi possível enviar o email. Verifique se o SMTP está configurado corretamente.'
    }
    
    throw new Error(errorMessage)
  }
}

async function getResetTokenInfo(token: string): Promise<{ expires_at: string; remaining_seconds: number }> {
  const res = await fetchWithFallback(`/auth/reset-password?token=${encodeURIComponent(token)}`, {
    method: 'GET',
  })
  if (!res.ok) {
    const text = await res.text()
    let errorMessage = text
    try {
      const json = JSON.parse(text)
      errorMessage = json.error || text
    } catch {
      // Se não for JSON, usar o texto direto
    }
    throw new Error(errorMessage || 'Erro ao verificar token')
  }
  return res.json()
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

// Função para obter uma mídia aleatória (imagem ou vídeo)
function getRandomMedia(): { type: 'image' | 'video', src: string } {
  const images = ['img0.jpg', 'mg1.jpg', 'mg2.jpg']
  const videos = ['video0_optimized.mp4', 'video1_optimized.mp4', 'video2_optimized.mp4']
  
  // Combinar todas as mídias em um array
  const allMedia: Array<{ type: 'image' | 'video', src: string }> = [
    ...images.map(img => ({ type: 'image' as const, src: img })),
    ...videos.map(vid => ({ type: 'video' as const, src: vid }))
  ]
  
  // Selecionar aleatoriamente
  const randomIndex = Math.floor(Math.random() * allMedia.length)
  return allMedia[randomIndex]
}

// Landing Page Pública - Tema Musical
function showLandingPage() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  // Obter mídia aleatória
  const randomMedia = getRandomMedia()
  
  app.innerHTML = `
    <div class="landing-page landing-music-theme">
      <header class="landing-header">
        <div class="landing-container">
          <h1 class="landing-logo">🎵 Easy Play Rockola</h1>
          <nav class="landing-nav">
            <a href="#dashboard" class="landing-nav-link">Login</a>
          </nav>
        </div>
      </header>
      
      
      <section class="landing-media-section">
        <div class="landing-container">
          <div class="landing-media-wrapper">
            <div class="landing-media-loading" id="media-loading">
              <div class="loading-spinner"></div>
              <p class="loading-text">Carregando mídia...</p>
            </div>
            ${randomMedia.type === 'image' 
              ? `<img src="/${randomMedia.src}" alt="Easy Play Rockola" class="landing-media" style="display: none;" />`
              : `<video src="/${randomMedia.src}" class="landing-media" autoplay muted loop playsinline style="display: none;"></video>`
            }
          </div>
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
  
  // Gerenciar loading da mídia - usar setTimeout para garantir que o DOM esteja pronto
  setTimeout(() => {
    const mediaElement = document.querySelector<HTMLImageElement | HTMLVideoElement>('.landing-media')
    const loadingElement = document.getElementById('media-loading')
    
    if (!mediaElement || !loadingElement) {
      console.warn('Elementos de mídia ou loading não encontrados')
      return
    }
    
    let loadingStartTime = Date.now()
    const minLoadingTime = 500 // Tempo mínimo de exibição do loading (500ms)
    
    const hideLoading = () => {
      const elapsed = Date.now() - loadingStartTime
      const remainingTime = Math.max(0, minLoadingTime - elapsed)
      
      setTimeout(() => {
        if (mediaElement) {
          mediaElement.style.display = 'block'
          mediaElement.style.opacity = '0'
          requestAnimationFrame(() => {
            if (mediaElement) {
              mediaElement.style.transition = 'opacity 0.5s ease-in'
              mediaElement.style.opacity = '1'
            }
          })
        }
        if (loadingElement) {
          loadingElement.style.transition = 'opacity 0.3s ease-out'
          loadingElement.style.opacity = '0'
          setTimeout(() => {
            if (loadingElement) {
              loadingElement.style.display = 'none'
            }
          }, 300)
        }
      }, remainingTime)
    }
    
    if (randomMedia.type === 'image') {
      const img = mediaElement as HTMLImageElement
      
      // Verificar se já está carregada
      if (img.complete && img.naturalWidth > 0) {
        hideLoading()
        return
      }
      
      // Adicionar listeners
      img.addEventListener('load', hideLoading, { once: true })
      img.addEventListener('error', () => {
        if (loadingElement) {
          loadingElement.innerHTML = `
            <div class="loading-spinner" style="border-top-color: #ef4444;"></div>
            <p class="loading-text" style="color: #ef4444;">Erro ao carregar mídia</p>
          `
        }
      }, { once: true })
    } else {
      const video = mediaElement as HTMLVideoElement
      
      // Verificar se já está carregado
      if (video.readyState >= 3) {
        hideLoading()
        return
      }
      
      // Adicionar listeners
      const handleLoad = () => {
        hideLoading()
        video.removeEventListener('loadeddata', handleLoad)
        video.removeEventListener('canplay', handleLoad)
        video.removeEventListener('canplaythrough', handleLoad)
      }
      
      video.addEventListener('loadeddata', handleLoad)
      video.addEventListener('canplay', handleLoad)
      video.addEventListener('canplaythrough', handleLoad)
      
      video.addEventListener('error', () => {
        if (loadingElement) {
          loadingElement.innerHTML = `
            <div class="loading-spinner" style="border-top-color: #ef4444;"></div>
            <p class="loading-text" style="color: #ef4444;">Erro ao carregar mídia</p>
          `
        }
      }, { once: true })
      
      // Forçar carregamento
      video.load()
    }
  }, 50)
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
            <input name="username" id="login-username" required placeholder="Digite seu usuário" autocomplete="username" />
          </div>
          <div class="form-group">
            <label>Senha</label>
            <input name="password" id="login-password" type="password" required placeholder="Digite sua senha" autocomplete="current-password" />
          </div>
          
          <!-- Loading do Login -->
          <div id="login-loading" style="display: none; text-align: center; padding: 1.5rem;">
            <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
            <p style="color: #667eea; font-weight: 500; margin: 0;">Autenticando...</p>
          </div>
          
          <!-- Mensagem de erro -->
          <div id="login-error" class="login-error-message" style="display: none;">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
              <div class="error-title">Falha na autenticação</div>
              <div class="error-text" id="login-error-text"></div>
            </div>
          </div>
          
          <button type="submit" id="login-submit-btn" style="width: 100%;">Entrar</button>
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
  const loadingDiv = document.getElementById('login-loading')
  const errorDiv = document.getElementById('login-error')
  const errorText = document.getElementById('login-error-text')
  const submitBtn = document.getElementById('login-submit-btn') as HTMLButtonElement
  const usernameInput = document.getElementById('login-username') as HTMLInputElement
  const passwordInput = document.getElementById('login-password') as HTMLInputElement
  
  // Função para esconder erro
  function hideError() {
    if (errorDiv) errorDiv.style.display = 'none'
  }
  
  // Esconder erro ao digitar
  usernameInput?.addEventListener('input', hideError)
  passwordInput?.addEventListener('input', hideError)
  
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    
    // Esconder erro anterior
    hideError()
    
    const fd = new FormData(loginForm)
    const username = fd.get('username')?.toString() ?? ''
    const password = fd.get('password')?.toString() ?? ''
    
    if (!username || !password) {
      if (errorDiv && errorText) {
        errorText.textContent = 'Por favor, preencha todos os campos.'
        errorDiv.style.display = 'flex'
      }
      return
    }
    
    // Mostrar loading
    if (loadingDiv) loadingDiv.style.display = 'block'
    if (submitBtn) {
      submitBtn.disabled = true
      submitBtn.textContent = 'Autenticando...'
    }
    if (usernameInput) usernameInput.disabled = true
    if (passwordInput) passwordInput.disabled = true
    
    try {
      const resp = await login(username, password)
      authToken = resp.token
      userRole = resp.role || 'admin'
      localStorage.setItem('adminToken', authToken)
      localStorage.setItem('userRole', userRole)
      
      // Ocultar loading
      if (loadingDiv) loadingDiv.style.display = 'none'
      
      if (resp.must_change_password) {
        showChangePassword(true)
      } else {
        await showDashboard()
      }
    } catch (err: any) {
      // Ocultar loading
      if (loadingDiv) loadingDiv.style.display = 'none'
      if (submitBtn) {
        submitBtn.disabled = false
        submitBtn.textContent = 'Entrar'
      }
      if (usernameInput) usernameInput.disabled = false
      if (passwordInput) passwordInput.disabled = false
      
      // Processar mensagem de erro
      let errorMessage = err?.message ?? 'Falha na autenticação'
      
      // Melhorar mensagens de erro
      if (errorMessage.includes('inválidos') || errorMessage.includes('inválido') || errorMessage.includes('incorret')) {
        errorMessage = 'Credenciais inválidas. Verifique seu usuário e senha e tente novamente.'
      } else if (errorMessage.includes('servidores falharam') || errorMessage.includes('conectar aos servidores')) {
        errorMessage = 'Não foi possível conectar aos servidores. Os servidores podem estar temporariamente offline. Verifique sua conexão com a internet e tente novamente.'
      } else if (errorMessage.includes('CORS') || errorMessage.includes('offline') || errorMessage.includes('Failed to fetch')) {
        errorMessage = 'Erro de conexão com o servidor. O servidor pode estar temporariamente indisponível. Tente novamente em alguns instantes.'
      } else if (errorMessage.includes('timeout') || errorMessage.includes('Timeout')) {
        errorMessage = 'Tempo de conexão esgotado. O servidor está demorando para responder. Tente novamente.'
      } else if (errorMessage.includes('Network') || errorMessage.includes('network')) {
        errorMessage = 'Erro de rede. Verifique sua conexão com a internet e tente novamente.'
      }
      
      // Mostrar erro de forma profissional
      if (errorDiv && errorText) {
        errorText.textContent = errorMessage
        errorDiv.style.display = 'flex'
        
        // Scroll suave para o erro
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
      
      // Também mostrar toast para melhor visibilidade
      showToast(errorMessage, 'error', 6000)
      
      // Focar no campo de usuário após erro
      setTimeout(() => {
        usernameInput?.focus()
        usernameInput?.select()
      }, 100)
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

// Função para exibir toast/notificação flutuante
function showToast(message: string, type: 'success' | 'error' | 'info' = 'info', duration: number = 5000) {
  // Remover toast existente se houver
  const existingToast = document.querySelector('.toast-notification')
  if (existingToast) {
    existingToast.remove()
  }
  
  const toast = document.createElement('div')
  toast.className = `toast-notification toast-${type}`
  toast.innerHTML = `
    <div class="toast-content">
      <div class="toast-icon">
        ${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}
      </div>
      <div class="toast-message">${message}</div>
      <button class="toast-close" aria-label="Fechar">&times;</button>
    </div>
  `
  
  document.body.appendChild(toast)
  
  // Animação de entrada
  requestAnimationFrame(() => {
    toast.style.opacity = '0'
    toast.style.transform = 'translateY(-20px)'
    requestAnimationFrame(() => {
      toast.style.transition = 'all 0.3s ease-out'
      toast.style.opacity = '1'
      toast.style.transform = 'translateY(0)'
    })
  })
  
  // Botão de fechar
  const closeBtn = toast.querySelector('.toast-close')
  const closeToast = () => {
    toast.style.transition = 'all 0.3s ease-in'
    toast.style.opacity = '0'
    toast.style.transform = 'translateY(-20px)'
    setTimeout(() => toast.remove(), 300)
  }
  
  closeBtn?.addEventListener('click', closeToast)
  
  // Auto-fechar após duração
  if (duration > 0) {
    setTimeout(closeToast, duration)
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
          <div id="forgot-loading" style="display: none; text-align: center; padding: 1.5rem;">
            <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
            <p style="color: #667eea; font-weight: 500;">Enviando solicitação...</p>
          </div>
          <div id="forgot-form-buttons" style="display: flex; gap: 1rem;">
            <button type="button" id="cancel-forgot-btn" style="flex: 1; background: #e5e7eb; color: #374151; padding: 0.875rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer;">Voltar</button>
            <button type="submit" id="submit-forgot-btn" style="flex: 1;">Enviar Instruções</button>
          </div>
        </form>
      </div>
    </main>
  `
  
  const forgotForm = document.querySelector<HTMLFormElement>('#forgot-password-form')
  const loadingDiv = document.getElementById('forgot-loading')
  const buttonsDiv = document.getElementById('forgot-form-buttons')
  const submitBtn = document.getElementById('submit-forgot-btn') as HTMLButtonElement
  const emailInput = document.getElementById('forgot-email') as HTMLInputElement
  
  forgotForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const email = emailInput?.value || ''
    
    if (!email) return
    
    // Mostrar loading
    if (loadingDiv) loadingDiv.style.display = 'block'
    if (buttonsDiv) buttonsDiv.style.display = 'none'
    if (submitBtn) submitBtn.disabled = true
    if (emailInput) emailInput.disabled = true
    
    try {
      await forgotPassword(email)
      
      // Ocultar loading
      if (loadingDiv) loadingDiv.style.display = 'none'
      if (buttonsDiv) buttonsDiv.style.display = 'flex'
      if (submitBtn) submitBtn.disabled = false
      if (emailInput) emailInput.disabled = false
      
      // Mostrar toast de sucesso
      showToast('Se o e-mail existir, você receberá instruções de recuperação de senha.', 'success', 6000)
      
      // Voltar para login após um delay
      setTimeout(() => {
        showLogin()
      }, 2000)
    } catch (err: any) {
      // Ocultar loading
      if (loadingDiv) loadingDiv.style.display = 'none'
      if (buttonsDiv) buttonsDiv.style.display = 'flex'
      if (submitBtn) submitBtn.disabled = false
      if (emailInput) emailInput.disabled = false
      
      // Mostrar toast de erro
      showToast(err?.message ?? 'Erro ao solicitar recuperação de senha', 'error', 6000)
    }
  })
  
  const cancelBtn = document.getElementById('cancel-forgot-btn')
  cancelBtn?.addEventListener('click', () => {
    showLogin()
  })
}

async function showResetPassword(token: string) {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  // Mostrar loading enquanto busca informações do token
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>Redefinir Senha</h1>
      </div>
      <div class="app-content">
        <div style="text-align: center; padding: 2rem;">
          <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
          <p style="color: #667eea; font-weight: 500;">Verificando token...</p>
        </div>
      </div>
    </main>
  `
  
  let expirationTime: number
  try {
    // Buscar informações do token do backend
    const tokenInfo = await getResetTokenInfo(token)
    
    // Calcular tempo de expiração baseado no tempo restante retornado pelo servidor
    expirationTime = Date.now() + (tokenInfo.remaining_seconds * 1000)
  } catch (err: any) {
    // Se houver erro ao buscar informações do token, mostrar erro e redirecionar
    app.innerHTML = `
      <main class="app login-card">
        <div class="app-header">
          <h1>Erro</h1>
        </div>
        <div class="app-content">
          <div class="login-error-message" style="display: flex;">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
              <div class="error-title">Token inválido ou expirado</div>
              <div class="error-text">${err?.message || 'O token de recuperação não é válido ou já expirou.'}</div>
            </div>
          </div>
          <button onclick="window.location.hash = '/'" style="width: 100%; margin-top: 1rem; padding: 0.875rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Voltar para Login</button>
        </div>
      </main>
    `
    return
  }
  
  app.innerHTML = `
    <main class="app login-card">
      <div class="app-header">
        <h1>Redefinir Senha</h1>
      </div>
      <div class="app-content">
        <p class="subtitle">Digite sua nova senha.</p>
        
        <!-- Contador regressivo -->
        <div class="token-timer-container" id="token-timer-container">
          <div class="token-timer-icon">⏱️</div>
          <div class="token-timer-text">
            <span class="token-timer-label">Token expira em:</span>
            <span class="token-timer-countdown" id="token-timer-countdown">0:30:00</span>
          </div>
        </div>
        
        <form id="reset-password-form">
          <div class="form-group">
            <label>Nova senha *</label>
            <input type="password" id="reset-new-password" required placeholder="Digite a nova senha" />
            
            <!-- Barra de força da senha -->
            <div class="password-strength-container" style="margin-top: 0.5rem;">
              <div class="password-strength-bar">
                <div class="password-strength-fill" id="password-strength-fill"></div>
              </div>
              <div class="password-strength-text" id="password-strength-text">Força da senha</div>
            </div>
            
            <!-- Validadores de senha -->
            <div class="password-validators" id="password-validators" style="margin-top: 0.75rem;">
              <div class="password-validator-item" data-validator="length">
                <span class="validator-icon">✗</span>
                <span class="validator-text">Mínimo de 6 caracteres</span>
              </div>
              <div class="password-validator-item" data-validator="number">
                <span class="validator-icon">✗</span>
                <span class="validator-text">Pelo menos um número</span>
              </div>
              <div class="password-validator-item" data-validator="lowercase">
                <span class="validator-icon">✗</span>
                <span class="validator-text">Pelo menos uma letra minúscula</span>
              </div>
              <div class="password-validator-item" data-validator="uppercase">
                <span class="validator-icon">✗</span>
                <span class="validator-text">Pelo menos uma letra maiúscula</span>
              </div>
              <div class="password-validator-item" data-validator="special">
                <span class="validator-icon">✗</span>
                <span class="validator-text">Pelo menos um caractere especial (!@#$%^&*)</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Confirmar nova senha *</label>
            <input type="password" id="reset-confirm-password" required placeholder="Digite a nova senha novamente" />
            <div class="password-match-indicator" id="password-match-indicator" style="margin-top: 0.5rem; font-size: 0.75rem; display: none;">
              <span class="match-icon">✗</span>
              <span class="match-text">As senhas não coincidem</span>
            </div>
          </div>
          <button type="submit" id="reset-submit-btn" style="width: 100%;" disabled>Redefinir Senha</button>
        </form>
        
        <!-- Loading durante redefinição -->
        <div id="reset-loading" class="reset-loading-overlay" style="display: none;">
          <div class="reset-loading-content">
            <div class="loading-spinner" style="margin: 0 auto 1.5rem;"></div>
            <p class="reset-loading-text">Redefinindo senha...</p>
            <p class="reset-loading-subtext">Aguarde enquanto processamos sua solicitação</p>
          </div>
        </div>
      </div>
    </main>
  `
  
  // Iniciar contador regressivo
  let countdownInterval: number | null = null
  function startCountdown() {
    const countdownElement = document.getElementById('token-timer-countdown')
    const timerContainer = document.getElementById('token-timer-container')
    
    function updateCountdown() {
      const now = Date.now()
      const remaining = expirationTime - now
      
      if (remaining <= 0) {
        if (countdownElement) {
          countdownElement.textContent = '0:00:00'
          countdownElement.style.color = '#dc2626'
        }
        if (timerContainer) {
          timerContainer.classList.add('token-expired')
        }
        if (countdownInterval) {
          clearInterval(countdownInterval)
        }
        
        // Desabilitar formulário quando expirar
        const submitBtn = document.getElementById('reset-submit-btn') as HTMLButtonElement
        if (submitBtn) {
          submitBtn.disabled = true
          submitBtn.textContent = 'Token Expirado - Solicite um novo link'
        }
        
        alert('O token de recuperação expirou. Por favor, solicite um novo link de recuperação de senha.')
        showLogin()
        return
      }
      
      const hours = Math.floor(remaining / (1000 * 60 * 60))
      const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((remaining % (1000 * 60)) / 1000)
      
      const formatted = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      
      if (countdownElement) {
        countdownElement.textContent = formatted
        
        // Mudar cor quando estiver próximo do fim
        if (remaining < 5 * 60 * 1000) { // Menos de 5 minutos
          countdownElement.style.color = '#dc2626'
          if (timerContainer) {
            timerContainer.classList.add('token-warning')
          }
        } else if (remaining < 10 * 60 * 1000) { // Menos de 10 minutos
          countdownElement.style.color = '#f59e0b'
        } else {
          countdownElement.style.color = '#059669'
        }
      }
    }
    
    updateCountdown() // Atualizar imediatamente
    countdownInterval = window.setInterval(updateCountdown, 1000) // Atualizar a cada segundo
  }
  
  startCountdown()
  
  // Função para validar senha
  function validatePassword(password: string) {
    const validators = {
      length: password.length >= 6,
      number: /\d/.test(password),
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password),
    }
    return validators
  }
  
  // Função para calcular força da senha
  function calculatePasswordStrength(password: string): { strength: number; label: string; color: string } {
    const validators = validatePassword(password)
    let strength = 0
    let label = 'Muito fraca'
    let color = '#ef4444'
    
    // Cada validador vale 20% (5 validadores = 100%)
    if (validators.length) strength += 20
    if (validators.number) strength += 20
    if (validators.lowercase) strength += 20
    if (validators.uppercase) strength += 20
    if (validators.special) strength += 20
    
    if (strength >= 100) {
      label = 'Muito forte'
      color = '#10b981'
    } else if (strength >= 80) {
      label = 'Forte'
      color = '#10b981'
    } else if (strength >= 60) {
      label = 'Média'
      color = '#f59e0b'
    } else if (strength >= 40) {
      label = 'Fraca'
      color = '#f97316'
    }
    
    return { strength, label, color }
  }
  
  // Função para atualizar validadores
  function updateValidators(password: string) {
    const validators = validatePassword(password)
    const validatorItems = document.querySelectorAll('.password-validator-item')
    
    validatorItems.forEach((item) => {
      const validatorType = item.getAttribute('data-validator')
      const icon = item.querySelector('.validator-icon')
      const isValid = validators[validatorType as keyof typeof validators]
      
      if (isValid) {
        item.classList.add('validator-valid')
        item.classList.remove('validator-invalid')
        if (icon) icon.textContent = '✓'
      } else {
        item.classList.add('validator-invalid')
        item.classList.remove('validator-valid')
        if (icon) icon.textContent = '✗'
      }
    })
  }
  
  // Função para atualizar barra de força
  function updateStrengthBar(password: string) {
    const { strength, label, color } = calculatePasswordStrength(password)
    const fill = document.getElementById('password-strength-fill')
    const text = document.getElementById('password-strength-text')
    
    if (fill) {
      fill.style.width = `${strength}%`
      fill.style.backgroundColor = color
    }
    
    if (text) {
      text.textContent = password.length > 0 ? label : 'Força da senha'
      text.style.color = password.length > 0 ? color : '#6b7280'
    }
  }
  
  // Função para verificar se senhas coincidem
  function checkPasswordMatch() {
    const newPassword = (document.getElementById('reset-new-password') as HTMLInputElement)?.value || ''
    const confirmPassword = (document.getElementById('reset-confirm-password') as HTMLInputElement)?.value || ''
    const indicator = document.getElementById('password-match-indicator')
    const matchIcon = indicator?.querySelector('.match-icon')
    const matchText = indicator?.querySelector('.match-text')
    const submitBtn = document.getElementById('reset-submit-btn') as HTMLButtonElement
    
    if (confirmPassword.length === 0) {
      if (indicator) indicator.style.display = 'none'
      return false
    }
    
    if (indicator) indicator.style.display = 'flex'
    
    if (newPassword === confirmPassword && newPassword.length > 0) {
      indicator?.classList.add('match-valid')
      indicator?.classList.remove('match-invalid')
      if (matchIcon) matchIcon.textContent = '✓'
      if (matchText) matchText.textContent = 'As senhas coincidem'
    } else {
      indicator?.classList.add('match-invalid')
      indicator?.classList.remove('match-valid')
      if (matchIcon) matchIcon.textContent = '✗'
      if (matchText) matchText.textContent = 'As senhas não coincidem'
    }
    
    // Habilitar botão apenas se senha for válida e coincidir
    const validators = validatePassword(newPassword)
    const allValid = validators.length && validators.number && validators.lowercase && validators.uppercase && validators.special
    const passwordsMatch = newPassword === confirmPassword && confirmPassword.length > 0
    
    // Verificar se token ainda não expirou
    const tokenValid = Date.now() < expirationTime
    
    if (submitBtn) {
      submitBtn.disabled = !(allValid && passwordsMatch && tokenValid)
    }
    
    return passwordsMatch
  }
  
  // Event listeners
  const newPasswordInput = document.getElementById('reset-new-password') as HTMLInputElement
  const confirmPasswordInput = document.getElementById('reset-confirm-password') as HTMLInputElement
  
  newPasswordInput?.addEventListener('input', (e) => {
    const password = (e.target as HTMLInputElement).value
    updateValidators(password)
    updateStrengthBar(password)
    checkPasswordMatch()
  })
  
  confirmPasswordInput?.addEventListener('input', () => {
    checkPasswordMatch()
  })
  
  const resetForm = document.querySelector<HTMLFormElement>('#reset-password-form')
  const loadingOverlay = document.getElementById('reset-loading')
  const submitBtn = document.getElementById('reset-submit-btn') as HTMLButtonElement
  
  resetForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const newPassword = newPasswordInput?.value || ''
    const confirmPassword = confirmPasswordInput?.value || ''
    
    // Verificar se token ainda é válido
    if (Date.now() >= expirationTime) {
      showToast('O token de recuperação expirou. Por favor, solicite um novo link de recuperação de senha.', 'error', 6000)
      setTimeout(() => showLogin(), 2000)
      return
    }
    
    const validators = validatePassword(newPassword)
    if (!validators.length || !validators.number || !validators.lowercase || !validators.uppercase || !validators.special) {
      showToast('A senha não atende aos requisitos mínimos. Verifique os critérios abaixo.', 'error', 5000)
      return
    }
    
    if (newPassword !== confirmPassword) {
      showToast('As senhas não coincidem. Verifique e tente novamente.', 'error', 4000)
      return
    }
    
    // Mostrar loading
    if (loadingOverlay) loadingOverlay.style.display = 'flex'
    if (submitBtn) {
      submitBtn.disabled = true
      submitBtn.textContent = 'Processando...'
    }
    if (newPasswordInput) newPasswordInput.disabled = true
    if (confirmPasswordInput) confirmPasswordInput.disabled = true
    
    try {
      // Parar contador
      if (countdownInterval) {
        clearInterval(countdownInterval)
      }
      
      await resetPassword(token, newPassword)
      
      // Ocultar loading
      if (loadingOverlay) loadingOverlay.style.display = 'none'
      
      // Mostrar mensagem de sucesso profissional
      showToast('Senha redefinida com sucesso! Redirecionando para o login...', 'success', 4000)
      
      // Redirecionar para login após um breve delay
      setTimeout(() => {
        showLogin()
      }, 2000)
    } catch (err: any) {
      // Ocultar loading
      if (loadingOverlay) loadingOverlay.style.display = 'none'
      if (submitBtn) {
        submitBtn.disabled = false
        submitBtn.textContent = 'Redefinir Senha'
      }
      if (newPasswordInput) newPasswordInput.disabled = false
      if (confirmPasswordInput) confirmPasswordInput.disabled = false
      
      const errorMsg = err?.message ?? 'Erro ao redefinir senha'
      
      // Se o token foi invalidado (usado), mostrar mensagem específica
      if (errorMsg.includes('inválido') || errorMsg.includes('expirado') || errorMsg.includes('Token')) {
        showToast('Este token já foi usado ou expirou. Por favor, solicite um novo link de recuperação de senha.', 'error', 6000)
        setTimeout(() => {
          showLogin()
        }, 3000)
      } else {
        showToast(errorMsg, 'error', 6000)
      }
    }
  })
}

async function showDashboard() {
  const app = document.querySelector<HTMLDivElement>('#app')
  if (!app) return
  
  // Mostrar loading
  app.innerHTML = `
    <main class="app">
      <div class="app-header">
        <h1>Dashboard de Licenciamento</h1>
      </div>
      <div class="app-content" style="text-align: center; padding: 4rem;">
        <div style="display: inline-block; padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
          <div style="font-size: 1.5rem; margin-bottom: 1rem;">⏳</div>
          <div style="font-size: 1.1rem; color: #667eea; font-weight: 600;">Carregando dashboard...</div>
          <div style="margin-top: 1rem; color: #6b7280; font-size: 0.9rem;">Aguarde enquanto buscamos os dados</div>
        </div>
      </div>
    </main>
  `
  
  // Carregar dados em paralelo
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
            ${devices.length > 50 ? `
            <div style="background: #fff3cd; border: 2px solid #ffc107; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
              <p style="margin: 0; color: #856404; font-size: 0.9rem;">
                <strong>⚠️ Muitas licenças (${devices.length}):</strong> A tabela pode demorar para carregar. Considere usar filtros ou paginação.
              </p>
            </div>
            ` : ''}
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
  
  // Renderizar gráficos com lazy loading (usar requestAnimationFrame)
  requestAnimationFrame(() => {
    renderPieChart(stats.byType, 'chart-by-type', 'Licenças por Tipo')
    requestAnimationFrame(() => {
      renderPieChart(stats.byStatus, 'chart-by-status', 'Licenças por Status')
    })
  })
  
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
        // Invalidar cache
        devicesCache = null
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
        // Invalidar cache
        devicesCache = null
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
        // Invalidar cache
        devicesCache = null
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
      
      // Invalidar cache
      devicesCache = null
      alert(userRole === 'user' 
        ? 'Licença gratuita ilimitada criada com sucesso!' 
        : `Licença ${licenseType} criada com sucesso!`)
      await showDashboard()
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
      await showDashboard()
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
  
  // Recalcular em resize com debounce otimizado
  let resizeTimeout: number
  let isResizing = false
  window.addEventListener('resize', () => {
    if (isResizing) return
    isResizing = true
    clearTimeout(resizeTimeout)
    resizeTimeout = window.setTimeout(() => {
      createDots()
      updateCarousel()
      isResizing = false
    }, 300)
  }, { passive: true })
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
      await showResetPassword(token)
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
