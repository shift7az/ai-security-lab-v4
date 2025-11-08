/**
 * WebSocket Hook for Real-Time Updates
 * Manages Socket.IO connection and real-time event handling
 */

import { useEffect, useState, useCallback, useRef, createContext, useContext, ReactNode } from 'react'
import { io, Socket } from 'socket.io-client'
import type {
  WebSocketMessage,
  ThreatDetectedEvent,
  NewAlertEvent,
  SystemUpdateEvent,
  CameraStatusEvent,
  AlertUpdateEvent,
  ThreatAnalysis,
  Alert,
} from '@/types'

// ============================================================================
// Configuration
// ============================================================================

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000'
const RECONNECT_ATTEMPTS = 5
const RECONNECT_DELAY = 3000 // 3 seconds

// ============================================================================
// Hook State Interface
// ============================================================================

interface UseWebSocketReturn {
  // Connection state
  socket: Socket | null
  isConnected: boolean
  connectionError: string | null
  
  // Real-time data
  latestThreat: ThreatDetectedEvent | null
  latestAlert: NewAlertEvent | null
  threats: Record<string, ThreatAnalysis>
  alerts: Alert[]
  
  // Connection controls
  connect: () => void
  disconnect: () => void
  reconnect: () => void
  
  // Event subscription
  subscribe: (event: string, handler: (data: any) => void) => () => void
  
  // Manual emit
  emit: (event: string, data: any) => void
}

// ============================================================================
// WebSocket Hook
// ============================================================================

export function useWebSocket(): UseWebSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  
  // Real-time data state
  const [latestThreat, setLatestThreat] = useState<ThreatDetectedEvent | null>(null)
  const [latestAlert, setLatestAlert] = useState<NewAlertEvent | null>(null)
  const [threats, setThreats] = useState<Record<string, ThreatAnalysis>>({})
  const [alerts, setAlerts] = useState<Alert[]>([])
  
  // Connection management
  const reconnectAttempts = useRef(0)
  const reconnectTimeout = useRef<NodeJS.Timeout>()
  
  // ========================================================================
  // Connection Management
  // ========================================================================
  
  const connect = useCallback(() => {
    try {
      console.log('Connecting to WebSocket server:', WS_URL)
      
      const newSocket = io(WS_URL, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: RECONNECT_ATTEMPTS,
        reconnectionDelay: RECONNECT_DELAY,
        timeout: 10000,
      })
      
      // Connection event handlers
      newSocket.on('connect', () => {
        console.log('✅ WebSocket connected')
        setIsConnected(true)
        setConnectionError(null)
        reconnectAttempts.current = 0
      })
      
      newSocket.on('disconnect', (reason) => {
        console.log('❌ WebSocket disconnected:', reason)
        setIsConnected(false)
        
        // Auto-reconnect on certain disconnect reasons
        if (reason === 'io server disconnect') {
          // Server initiated disconnect, try to reconnect
          if (reconnectAttempts.current < RECONNECT_ATTEMPTS) {
            reconnectAttempts.current++
            reconnectTimeout.current = setTimeout(() => {
              console.log(`Reconnection attempt ${reconnectAttempts.current}/${RECONNECT_ATTEMPTS}`)
              newSocket.connect()
            }, RECONNECT_DELAY)
          }
        }
      })
      
      newSocket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error)
        setConnectionError(error.message)
        setIsConnected(false)
      })
      
      newSocket.on('error', (error) => {
        console.error('WebSocket error:', error)
        setConnectionError(error.message || 'WebSocket error occurred')
      })
      
      // Real-time event handlers
      newSocket.on('threat_detected', (data: ThreatDetectedEvent) => {
        console.log('🔴 Threat detected:', data)
        setLatestThreat(data)
        
        // Update threats map
        setThreats(prev => ({
          ...prev,
          [data.camera_id]: data.threat_analysis
        }))
        
        // Play alert sound if needed
        if (data.requires_immediate_action) {
          playAlertSound()
        }
      })
      
      newSocket.on('new_alert', (data: NewAlertEvent) => {
        console.log('🚨 New alert:', data)
        setLatestAlert(data)
        
        // Add to alerts list
        setAlerts(prev => [data.alert, ...prev].slice(0, 50)) // Keep last 50 alerts
        
        // Play sound if enabled
        if (data.play_sound) {
          playAlertSound()
        }
        
        // Show desktop notification if enabled
        if (Notification.permission === 'granted') {
          new Notification(`Security Alert: ${data.alert.threat_level.toUpperCase()}`, {
            body: data.alert.message,
            icon: '/alert-icon.png',
            tag: data.alert.id,
          })
        }
      })
      
      newSocket.on('system_update', (data: SystemUpdateEvent) => {
        console.log('ℹ️ System update:', data)
        // Could dispatch this to a global state management system
      })
      
      newSocket.on('camera_status', (data: CameraStatusEvent) => {
        console.log('📹 Camera status update:', data)
        // Could update camera status in global state
      })
      
      newSocket.on('alert_update', (data: AlertUpdateEvent) => {
        console.log('✏️ Alert updated:', data)
        // Update alert in list
        setAlerts(prev => prev.map(alert => 
          alert.id === data.alert_id 
            ? { ...alert, status: data.status }
            : alert
        ))
      })
      
      setSocket(newSocket)
      
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error)
      setConnectionError(error instanceof Error ? error.message : 'Failed to connect')
    }
  }, [])
  
  const disconnect = useCallback(() => {
    if (socket) {
      console.log('Disconnecting WebSocket...')
      socket.disconnect()
      setSocket(null)
      setIsConnected(false)
    }
    
    // Clear reconnect timeout
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current)
    }
  }, [socket])
  
  const reconnect = useCallback(() => {
    disconnect()
    setTimeout(() => connect(), 1000)
  }, [disconnect, connect])
  
  // ========================================================================
  // Event Subscription
  // ========================================================================
  
  const subscribe = useCallback((event: string, handler: (data: any) => void) => {
    if (!socket) {
      console.warn('Cannot subscribe: socket not connected')
      return () => {}
    }
    
    socket.on(event, handler)
    
    // Return unsubscribe function
    return () => {
      socket.off(event, handler)
    }
  }, [socket])
  
  // ========================================================================
  // Manual Emit
  // ========================================================================
  
  const emit = useCallback((event: string, data: any) => {
    if (!socket || !isConnected) {
      console.warn('Cannot emit: socket not connected')
      return
    }
    
    socket.emit(event, data)
  }, [socket, isConnected])
  
  // ========================================================================
  // Lifecycle
  // ========================================================================
  
  useEffect(() => {
    // Auto-connect on mount
    connect()
    
    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, []) // Empty deps - only run on mount/unmount
  
  // Request notification permission on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      if (Notification.permission === 'default') {
        Notification.requestPermission()
      }
    }
  }, [])
  
  return {
    socket,
    isConnected,
    connectionError,
    latestThreat,
    latestAlert,
    threats,
    alerts,
    connect,
    disconnect,
    reconnect,
    subscribe,
    emit,
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Play alert sound
 */
function playAlertSound() {
  if (typeof window === 'undefined') return
  
  try {
    // Check if sound is enabled in settings
    const soundEnabled = localStorage.getItem('alert_sound_enabled') !== 'false'
    
    if (soundEnabled) {
      const audio = new Audio('/sounds/alert.mp3')
      audio.volume = 0.5
      audio.play().catch(err => {
        console.warn('Could not play alert sound:', err)
      })
    }
  } catch (error) {
    console.error('Error playing alert sound:', error)
  }
}

/**
 * Hook for specific event subscription
 */
export function useWebSocketEvent<T = any>(
  event: string,
  handler: (data: T) => void,
  deps: any[] = []
) {
  const { subscribe } = useWebSocket()
  
  useEffect(() => {
    const unsubscribe = subscribe(event, handler)
    return unsubscribe
  }, [event, ...deps])
}

// ============================================================================
// Context Provider (Optional - for global WebSocket state)
// ============================================================================

interface WebSocketContextValue {
  ws: UseWebSocketReturn
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null)

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const ws = useWebSocket()
  
  return (
    <WebSocketContext.Provider value={{ ws }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocketContext() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider')
  }
  return context.ws
}
