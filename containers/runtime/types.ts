export type Platform = 'node' | 'next' | 'unix' | 'linux' | 'macos' | 'windows'

export interface FlpkgContainer {
  id: string
  version: string
  origin_signature: string
  layer: 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7'
  content: {
    particles?: any[]
    references?: any[]
    metadata?: Record<string, any>
  }
  encrypted?: boolean
}

export interface RuntimeInstance {
  id: string
  container: FlpkgContainer
  platform: Platform
  status: 'starting' | 'running' | 'stopped' | 'failed'
  metadata: {
    origin_signature: string
    created_at: string
    [key: string]: any
  }
  particles?: any[]
  execute(): Promise<void>
  stop(): Promise<void>
}
