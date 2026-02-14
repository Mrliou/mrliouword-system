import { UniversalRuntime } from '../runtime/UniversalRuntime'
import { FlpkgContainer } from '../runtime/types'

describe('UniversalRuntime', () => {
  it('should detect platform', () => {
    const runtime = new UniversalRuntime()
    expect(runtime).toBeDefined()
  })
  
  it('should create a basic container', async () => {
    const runtime = new UniversalRuntime()
    
    const container: FlpkgContainer = {
      id: 'test-container',
      version: 'flpkg/1.0',
      origin_signature: 'MrLiouWord',
      layer: 'L2',
      content: {
        particles: [],
        metadata: {}
      }
    }
    
    const instance = await runtime.spawn(container)
    
    expect(instance).toBeDefined()
    expect(instance.id).toContain('runtime-')
    expect(instance.status).toBe('starting')
    expect(instance.metadata.origin_signature).toBe('MrLiouWord')
  })
  
  it('should apply layer configuration', async () => {
    const runtime = new UniversalRuntime()
    
    const container: FlpkgContainer = {
      id: 'test-container-l0',
      version: 'flpkg/1.0',
      origin_signature: 'MrLiouWord',
      layer: 'L0',
      content: {
        metadata: {}
      }
    }
    
    const instance = await runtime.spawn(container)
    
    expect(instance.metadata.origin_signature).toBe('MrLiouWord')
  })
})
