/**
 * MetaEnv Controller - 元代碼沙盒控制器
 * 實現 P.MetaEnv.openapi.yaml 規格
 */

import { UniversalRuntime } from '../runtime/UniversalRuntime'
import { GuardV1 } from './GuardV1'
import { ChannelMapper } from './ChannelMapper'

export interface SpawnRequest {
  env_id?: string
  role?: 'core' | 'node'
  shape: {
    cpu: number
    gpu?: number
    ram: string
  }
  policy?: string
}

export interface SpawnResponse {
  ok: boolean
  env_id: string
  status: string
}

export class MetaEnvController {
  private runtime: UniversalRuntime
  private guard: GuardV1
  private channelMapper: ChannelMapper
  private environments: Map<string, any>
  
  constructor() {
    this.runtime = new UniversalRuntime()
    this.guard = new GuardV1()
    this.channelMapper = new ChannelMapper()
    this.environments = new Map()
  }
  
  async spawn(req: SpawnRequest): Promise<SpawnResponse> {
    const env_id = req.env_id || `env-${Date.now()}`
    
    console.log(`[MetaEnv] Spawning environment: ${env_id}`)
    console.log(`[MetaEnv] Shape: ${req.shape.cpu} CPU, ${req.shape.ram} RAM`)
    
    // Apply default policy
    if (req.policy) {
      await this.guard.applyPolicy(env_id, req.policy)
    }
    
    this.environments.set(env_id, {
      id: env_id,
      status: 'starting',
      shape: req.shape,
      created_at: new Date().toISOString()
    })
    
    return {
      ok: true,
      env_id,
      status: 'starting'
    }
  }
  
  async applyPolicy(env_id: string, policy: string): Promise<void> {
    await this.guard.applyPolicy(env_id, policy)
  }
  
  async createSnapshot(env_id: string, encrypted = true): Promise<string> {
    const snapshot_id = `snapshot-${env_id}-${Date.now()}`
    console.log(`[MetaEnv] Creating snapshot: ${snapshot_id} (encrypted: ${encrypted})`)
    
    // Create encrypted snapshot (implementation)
    
    return snapshot_id
  }
  
  async channelMap(app: string, from: string, to: string, mode = 'dry-run'): Promise<any> {
    return this.channelMapper.map(app, from, to, mode)
  }
  
  async lockdown(env_id: string, reason: string): Promise<void> {
    console.log(`[MetaEnv] LOCKDOWN: ${env_id} - ${reason}`)
    await this.guard.lockdown(env_id, reason)
  }
}
