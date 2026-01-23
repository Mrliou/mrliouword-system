/**
 * Next.js Platform Adapter
 */

import { FlpkgContainer, RuntimeInstance } from '../types'

export class NextAdapter {
  async create(container: FlpkgContainer): Promise<RuntimeInstance> {
    console.log(`[NextAdapter] Creating instance for container ${container.id}`)
    
    const instance: RuntimeInstance = {
      id: `runtime-${container.id}-${Date.now()}`,
      container,
      platform: 'next',
      status: 'starting',
      metadata: {
        origin_signature: container.origin_signature,
        created_at: new Date().toISOString(),
        framework: 'Next.js',
      },
      async execute() {
        console.log(`[NextAdapter] Executing container ${container.id}`)
        this.status = 'running'
      },
      async stop() {
        console.log(`[NextAdapter] Stopping container ${container.id}`)
        this.status = 'stopped'
      }
    }
    
    return instance
  }
}
