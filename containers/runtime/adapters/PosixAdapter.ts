/**
 * POSIX Platform Adapter (Unix/Linux/macOS)
 */

import { FlpkgContainer, RuntimeInstance } from '../types'

export class PosixAdapter {
  async create(container: FlpkgContainer): Promise<RuntimeInstance> {
    console.log(`[PosixAdapter] Creating instance for container ${container.id}`)
    
    const instance: RuntimeInstance = {
      id: `runtime-${container.id}-${Date.now()}`,
      container,
      platform: 'unix',
      status: 'starting',
      metadata: {
        origin_signature: container.origin_signature,
        created_at: new Date().toISOString(),
        platform: process.platform,
        arch: process.arch,
      },
      async execute() {
        console.log(`[PosixAdapter] Executing container ${container.id}`)
        this.status = 'running'
      },
      async stop() {
        console.log(`[PosixAdapter] Stopping container ${container.id}`)
        this.status = 'stopped'
      }
    }
    
    return instance
  }
}
