/**
 * L0-L7 Layer Management System
 * 層級管理系統
 * Origin Signature: MrLiouWord
 */

export class LayerManager {
  private layers = {
    L0: { name: 'ROOT', desc: 'Origin: MrLiouWord' },
    L1: { name: 'SEED', desc: 'Initial state' },
    L2: { name: 'PARTICLE', desc: '17 fx particles' },
    L3: { name: 'LAW', desc: 'Business logic' },
    L4: { name: 'WORLD', desc: 'External connections' },
    L5: { name: 'MIRROR', desc: 'Backup/redundancy' },
    L6: { name: 'REFLECT', desc: 'UI/API projection' },
    L7: { name: 'LOOP', desc: 'Verification' }
  };

  private loadedContainers: Map<string, Set<string>> = new Map();

  async initialize(): Promise<void> {
    for (const layer of Object.keys(this.layers)) {
      this.loadedContainers.set(layer, new Set());
    }
  }

  async loadToLayer(containerPath: string, layer: string): Promise<void> {
    if (!this.layers[layer as keyof typeof this.layers]) {
      throw new Error(`Invalid layer: ${layer}`);
    }
    
    const containers = this.loadedContainers.get(layer);
    if (containers) {
      containers.add(containerPath);
    }
  }

  getLayerInfo(layer: string) {
    return this.layers[layer as keyof typeof this.layers];
  }

  getLoadedContainers(layer: string): string[] {
    return Array.from(this.loadedContainers.get(layer) || []);
  }
}
