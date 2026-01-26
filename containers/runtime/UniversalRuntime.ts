/**
 * MrLiouWord Universal Container Runtime
 * 統一容器運行時 - 支援所有平台
 * Origin Signature: MrLiouWord
 */

import { LayerManager } from './LayerManager';
import { PlatformBridge } from './PlatformBridge';
import { NodeAdapter } from './adapters/NodeAdapter';
import { NextAdapter } from './adapters/NextAdapter';

export interface RuntimeConfig {
  platform?: 'unix' | 'linux' | 'macos' | 'windows' | 'node' | 'next';
  layer?: string;
  cpu?: number;
  ram?: string;
  gpu?: number;
}

export interface RuntimeInstance {
  id: string;
  status: 'starting' | 'running' | 'stopped' | 'failed';
  platform: string;
  layer: string;
  execute(): Promise<any>;
  stop(): Promise<void>;
}

export class UniversalRuntime {
  private layerManager: LayerManager;
  private platformBridge: PlatformBridge;
  private instances: Map<string, RuntimeInstance>;

  constructor(config: RuntimeConfig = {}) {
    this.layerManager = new LayerManager();
    this.platformBridge = new PlatformBridge(config.platform);
    this.instances = new Map();
  }

  async init(): Promise<void> {
    console.log('🚀 Initializing Universal Runtime...');
    await this.platformBridge.detectPlatform();
    await this.layerManager.initialize();
    console.log('✅ Universal Runtime initialized');
  }

  async spawn(config: RuntimeConfig): Promise<RuntimeInstance> {
    const instanceId = `runtime-${Date.now()}`;
    const platform = config.platform || await this.platformBridge.detectPlatform();
    const layer = config.layer || 'L3';

    const instance: RuntimeInstance = {
      id: instanceId,
      status: 'starting',
      platform,
      layer,
      execute: async () => {
        instance.status = 'running';
        return { success: true, instanceId };
      },
      stop: async () => {
        instance.status = 'stopped';
        this.instances.delete(instanceId);
      }
    };

    this.instances.set(instanceId, instance);
    console.log(`✅ Spawned runtime instance: ${instanceId}`);
    return instance;
  }

  async load(containerPath: string, layer?: string): Promise<void> {
    console.log(`📦 Loading container: ${containerPath}`);
    const targetLayer = layer || 'L3';
    await this.layerManager.loadToLayer(containerPath, targetLayer);
    console.log(`✅ Container loaded to ${targetLayer}`);
  }

  getInstances(): RuntimeInstance[] {
    return Array.from(this.instances.values());
  }
}
