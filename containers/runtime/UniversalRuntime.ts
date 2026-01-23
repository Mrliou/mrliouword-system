/**
 * MrLiouWord Universal Container Runtime
 * 統一容器運行時 - 支援所有平台
 * Origin Signature: MrLiouWord
 */

import { FlpkgContainer, RuntimeInstance, Platform } from './types'
import { NodeAdapter } from './adapters/NodeAdapter'
import { NextAdapter } from './adapters/NextAdapter'
import { PosixAdapter } from './adapters/PosixAdapter'
import { WindowsAdapter } from './adapters/WindowsAdapter'

export class UniversalRuntime {
  private platform: Platform
  private adapters: Map<Platform, any>
  
  constructor() {
    this.platform = this.detectPlatform()
    this.adapters = new Map([
      ['node', new NodeAdapter()],
      ['next', new NextAdapter()],
      ['unix', new PosixAdapter()],
      ['linux', new PosixAdapter()],
      ['macos', new PosixAdapter()],
      ['windows', new WindowsAdapter()],
    ])
  }
  
  async spawn(container: FlpkgContainer): Promise<RuntimeInstance> {
    const adapter = this.adapters.get(this.platform)
    if (!adapter) {
      throw new Error(`Unsupported platform: ${this.platform}`)
    }
    
    console.log(`[UniversalRuntime] Spawning container on ${this.platform}`)
    const instance = await adapter.create(container)
    
    // Apply L0-L7 layer configuration
    await this.applyLayerConfig(instance, container.layer)
    
    return instance
  }
  
  async load(path: string): Promise<FlpkgContainer> {
    const loader = await import('./loaders/FlpkgLoader')
    return loader.load(path)
  }
  
  private detectPlatform(): Platform {
    if (typeof process !== 'undefined') {
      if (process.versions?.node) return 'node'
      const platform = process.platform
      if (platform === 'darwin') return 'macos'
      if (platform === 'win32') return 'windows'
      if (platform === 'linux') return 'linux'
    }
    return 'unix'
  }
  
  private async applyLayerConfig(instance: RuntimeInstance, layer: string) {
    // L0-L7 層級配置
    const layerManager = await import('./LayerManager')
    await layerManager.configure(instance, layer as any)
  }
}
