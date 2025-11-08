/**
 * Type definitions for AI Security Lab Dashboard
 * Provides type safety for all domain models and API responses
 */

// ============================================================================
// Core Domain Models
// ============================================================================

export type ThreatLevel = 'none' | 'low' | 'medium' | 'high' | 'critical'
export type AlertStatus = 'active' | 'acknowledged' | 'resolved'
export type AlertPriority = 'low' | 'medium' | 'high' | 'critical'
export type CameraStatus = 'online' | 'offline' | 'error' | 'maintenance'
export type SystemHealthStatus = 'healthy' | 'degraded' | 'unhealthy'

// ============================================================================
// Camera Models
// ============================================================================

export interface Camera {
  id: string
  name: string
  location: string
  status: CameraStatus
  stream_url: string
  snapshot_url?: string
  last_detection?: Detection
  threat_count_24h: number
  uptime_percentage: number
  metadata?: {
    resolution?: string
    fps?: number
    codec?: string
  }
}

export interface CameraWithStats extends Camera {
  total_detections: number
  threats_detected: number
  average_threat_score: number
  last_active: string
}

// ============================================================================
// Detection Models
// ============================================================================

export interface Detection {
  id: string
  camera_id: string
  detection_type: string
  confidence: number
  bbox: [number, number, number, number] // [x, y, width, height]
  timestamp: string
  frame_data?: string // Base64 encoded image
  metadata?: Record<string, any>
}

// ============================================================================
// Threat Analysis Models
// ============================================================================

export interface ThreatFactor {
  name: string
  score: number
  description: string
  weight?: number
}

export interface ThreatAnalysis {
  detection_id: string
  threat_score: number
  threat_level: ThreatLevel
  primary_threat: string
  requires_response: boolean
  response_priority: AlertPriority
  factors: ThreatFactor[]
  timestamp: string
  camera_id: string
  recommendations?: string[]
}

export interface IntelligenceResult {
  detection_id: string
  camera_id: string
  timestamp: string
  threat_analysis: ThreatAnalysis | null
  processing_time_ms: number
  ai_models_used: string[]
  insights: Record<string, any>
}

// ============================================================================
// Alert Models
// ============================================================================

export interface Alert {
  id: string
  camera_id: string
  camera_name?: string
  threat_level: ThreatLevel
  priority: AlertPriority
  message: string
  description?: string
  timestamp: string
  status: AlertStatus
  acknowledged_by?: string
  acknowledged_at?: string
  resolved_by?: string
  resolved_at?: string
  resolution_notes?: string
  detection_id?: string
  threat_score?: number
  actions_taken?: string[]
}

export interface AlertAction {
  alert_id: string
  action: 'acknowledge' | 'resolve'
  user_id: string
  notes?: string
  timestamp?: string
}

// ============================================================================
// Dashboard Models
// ============================================================================

export interface DashboardOverview {
  total_threats: number
  critical_alerts: number
  active_cameras: number
  total_cameras: number
  system_health: number
  health_status: SystemHealthStatus
  threat_trend: TrendData
  alert_trend: TrendData
  processing_stats: ProcessingStats
  timestamp: string
}

export interface TrendData {
  current: number
  previous: number
  change_percentage: number
  direction: 'up' | 'down' | 'stable'
}

export interface ProcessingStats {
  total_processed: number
  threats_detected: number
  alerts_generated: number
  avg_processing_time: number
  last_activity: string | null
}

// ============================================================================
// System Health Models
// ============================================================================

export interface SystemHealth {
  status: SystemHealthStatus
  timestamp: string
  components: ComponentHealth
  statistics: ProcessingStats
  configuration: SystemConfiguration
}

export interface ComponentHealth {
  ai_orchestrator: boolean
  threat_detector: boolean
  database: boolean
  cache: boolean
  frigate: boolean
}

export interface SystemConfiguration {
  threat_detector_enabled: boolean
  max_concurrent_analyses: number
  workers_active: number
}

export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  gpu_usage?: number
  disk_usage: number
  network_throughput: {
    incoming: number
    outgoing: number
  }
  queue_sizes: {
    detection_queue: number
    result_queue: number
  }
}

// ============================================================================
// Timeline & History Models
// ============================================================================

export interface TimelineEvent {
  id: string
  type: 'threat' | 'alert' | 'system' | 'camera'
  timestamp: string
  camera_id?: string
  camera_name?: string
  threat_level?: ThreatLevel
  title: string
  description: string
  metadata?: Record<string, any>
  related_detection_id?: string
}

export interface ThreatHistory {
  detection_id: string
  camera_id: string
  threat_score: number
  threat_level: ThreatLevel
  timestamp: string
  primary_threat: string
  factors_count: number
}

// ============================================================================
// Chart & Visualization Models
// ============================================================================

export interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
  category?: string
}

export interface ThreatTrendData extends ChartDataPoint {
  threat_score: number
  threat_level: ThreatLevel
  camera_id: string
}

export interface CameraHeatmapData {
  camera_id: string
  camera_name: string
  location: string
  threat_density: number
  total_threats: number
  average_threat_score: number
  coordinates?: {
    x: number
    y: number
  }
}

// ============================================================================
// API Response Models
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ErrorResponse {
  error: string
  message: string
  details?: Record<string, any>
  timestamp: string
}

// ============================================================================
// WebSocket Event Models
// ============================================================================

export interface WebSocketMessage<T = any> {
  type: 'threat_detected' | 'new_alert' | 'system_update' | 'camera_status' | 'alert_update'
  data: T
  timestamp: string
}

export interface ThreatDetectedEvent {
  camera_id: string
  detection_id: string
  threat_analysis: ThreatAnalysis
  requires_immediate_action: boolean
}

export interface NewAlertEvent {
  alert: Alert
  play_sound: boolean
  auto_acknowledge: boolean
}

export interface SystemUpdateEvent {
  component: keyof ComponentHealth
  status: boolean
  message?: string
}

export interface CameraStatusEvent {
  camera_id: string
  status: CameraStatus
  message?: string
}

export interface AlertUpdateEvent {
  alert_id: string
  status: AlertStatus
  updated_by: string
}

// ============================================================================
// Filter & Query Models
// ============================================================================

export interface CameraFilter {
  status?: CameraStatus[]
  location?: string[]
  has_threats?: boolean
}

export interface ThreatFilter {
  camera_id?: string
  threat_level?: ThreatLevel[]
  date_from?: string
  date_to?: string
  min_score?: number
  max_score?: number
}

export interface AlertFilter {
  status?: AlertStatus[]
  priority?: AlertPriority[]
  camera_id?: string
  date_from?: string
  date_to?: string
}

export interface TimeRangeQuery {
  hours?: number
  from?: string
  to?: string
}

// ============================================================================
// UI State Models
// ============================================================================

export interface DashboardState {
  selectedCamera: string | null
  activeFilters: {
    cameras: CameraFilter
    threats: ThreatFilter
    alerts: AlertFilter
  }
  viewMode: 'grid' | 'list' | 'map'
  timeRange: TimeRangeQuery
  autoRefresh: boolean
  refreshInterval: number // milliseconds
}

export interface NotificationSettings {
  sound_enabled: boolean
  desktop_notifications: boolean
  alert_threshold: ThreatLevel
  mute_cameras: string[]
}

// ============================================================================
// Utility Types
// ============================================================================

export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>

// ============================================================================
// Type Guards
// ============================================================================

export function isThreatLevel(value: string): value is ThreatLevel {
  return ['none', 'low', 'medium', 'high', 'critical'].includes(value)
}

export function isAlertStatus(value: string): value is AlertStatus {
  return ['active', 'acknowledged', 'resolved'].includes(value)
}

export function isCameraStatus(value: string): value is CameraStatus {
  return ['online', 'offline', 'error', 'maintenance'].includes(value)
}

export function isValidThreatAnalysis(obj: any): obj is ThreatAnalysis {
  return (
    obj &&
    typeof obj.detection_id === 'string' &&
    typeof obj.threat_score === 'number' &&
    isThreatLevel(obj.threat_level) &&
    Array.isArray(obj.factors)
  )
}
