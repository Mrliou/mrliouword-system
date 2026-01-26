---
title: "前粒子整合流程圖與實現指南"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: ["pre-particle", "particle-system", "integration", "flow-diagram", "implementation-guide", "particle-pipeline"]
---

# 前粒子整合流程圖與實現指南

<!-- origin_signature: MrLiouWord -->

## 目錄

1. [概述](#概述)
2. [前粒子系統架構](#前粒子系統架構)
3. [粒子創建管線](#粒子創建管線)
4. [流程圖](#流程圖)
5. [前粒子狀態機](#前粒子狀態機)
6. [整合實現步驟](#整合實現步驟)
7. [實現範例](#實現範例)
8. [性能考量與優化](#性能考量與優化)
9. [故障排除與最佳實踐](#故障排除與最佳實踐)

---

## 概述

前粒子（Pre-Particle）系統是MrLiouWord架構中的核心概念，負責在粒子完全實例化之前的準備、配置和初始化階段。本文檔提供完整的前粒子整合流程圖和逐步實現指南。

### 前粒子的定義

前粒子是指粒子在完全激活和進入運行態之前的預備狀態，包含：

- **元數據準備**: 粒子的基本屬性和配置
- **資源分配**: 記憶體、GPU緩衝區等資源的預分配
- **依賴解析**: 確定粒子間的依賴關係
- **初始化隊列**: 管理粒子的初始化順序
- **驗證檢查**: 確保粒子配置的正確性

### 核心特性

- 🔄 **異步初始化**: 支持非阻塞的粒子創建流程
- 🎯 **依賴管理**: 自動解析和處理粒子間依賴
- 🚀 **批次處理**: 高效的批量粒子創建
- 🛡️ **錯誤恢復**: 完善的錯誤處理和回滾機制
- 📊 **狀態追蹤**: 實時監控粒子初始化狀態

---

## 前粒子系統架構

### 架構層次圖

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│              Particle Creation Request API                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Pre-Particle Manager Layer                   │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Request     │  │  Dependency  │  │   Validation    │ │
│  │   Queue       │  │   Resolver   │  │   Engine        │ │
│  └───────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Resource Allocation Layer                      │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │    Memory     │  │   GPU Buffer │  │    Network      │ │
│  │   Allocator   │  │   Allocator  │  │   Resources     │ │
│  └───────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Particle Instantiation Layer                  │
│              Final Particle Object Creation                 │
└─────────────────────────────────────────────────────────────┘
```

### 系統組件

```typescript
// pre-particle-types.ts
export enum PreParticleState {
  PENDING = 'pending',           // 等待處理
  VALIDATING = 'validating',     // 驗證中
  RESOLVING_DEPS = 'resolving',  // 解析依賴
  ALLOCATING = 'allocating',     // 分配資源
  INITIALIZING = 'initializing', // 初始化中
  READY = 'ready',               // 就緒
  FAILED = 'failed',             // 失敗
  CANCELLED = 'cancelled'        // 已取消
}

export interface PreParticleConfig {
  id: string;
  type: ParticleType;
  properties: Record<string, any>;
  dependencies: string[];
  resources: ResourceRequirements;
  priority: number;
  timeout: number;
  retryPolicy: RetryPolicy;
}

export interface ResourceRequirements {
  memory: number;          // 字節
  gpuMemory?: number;      // 字節
  computeUnits?: number;   // GPU計算單元
  networkBandwidth?: number; // KB/s
}

export interface RetryPolicy {
  maxRetries: number;
  backoffMultiplier: number;
  initialDelay: number;
  maxDelay: number;
}

export interface PreParticle {
  config: PreParticleConfig;
  state: PreParticleState;
  allocatedResources: AllocatedResources;
  dependencies: PreParticle[];
  createdAt: number;
  updatedAt: number;
  errors: Error[];
}

export interface AllocatedResources {
  memoryHandle: MemoryHandle;
  gpuBufferHandle?: GPUBuffer;
  computeContext?: ComputeContext;
}
```

---

## 粒子創建管線

### 管線階段詳解

```typescript
// pre-particle-pipeline.ts
export class PreParticlePipeline {
  private stages: PipelineStage[] = [];
  private eventEmitter: EventEmitter;
  
  constructor() {
    this.initializeStages();
    this.eventEmitter = new EventEmitter();
  }
  
  private initializeStages(): void {
    this.stages = [
      new ValidationStage(),
      new DependencyResolutionStage(),
      new ResourceAllocationStage(),
      new InitializationStage(),
      new ReadyStage()
    ];
  }
  
  async process(config: PreParticleConfig): Promise<PreParticle> {
    let preParticle: PreParticle = {
      config,
      state: PreParticleState.PENDING,
      allocatedResources: {} as AllocatedResources,
      dependencies: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      errors: []
    };
    
    try {
      for (const stage of this.stages) {
        this.eventEmitter.emit('stage:start', {
          stage: stage.name,
          particle: preParticle.config.id
        });
        
        preParticle = await stage.execute(preParticle);
        preParticle.updatedAt = Date.now();
        
        this.eventEmitter.emit('stage:complete', {
          stage: stage.name,
          particle: preParticle.config.id,
          state: preParticle.state
        });
        
        // 如果階段失敗，停止處理
        if (preParticle.state === PreParticleState.FAILED) {
          throw new Error(`Stage ${stage.name} failed`);
        }
      }
      
      return preParticle;
      
    } catch (error) {
      preParticle.state = PreParticleState.FAILED;
      preParticle.errors.push(error as Error);
      
      // 清理已分配的資源
      await this.rollback(preParticle);
      
      throw error;
    }
  }
  
  private async rollback(preParticle: PreParticle): Promise<void> {
    // 反向執行清理操作
    for (let i = this.stages.length - 1; i >= 0; i--) {
      try {
        await this.stages[i].cleanup(preParticle);
      } catch (cleanupError) {
        console.error('Cleanup error:', cleanupError);
      }
    }
  }
  
  on(event: string, handler: Function): void {
    this.eventEmitter.on(event, handler);
  }
}

// 管線階段基類
export abstract class PipelineStage {
  abstract name: string;
  
  abstract execute(preParticle: PreParticle): Promise<PreParticle>;
  
  async cleanup(preParticle: PreParticle): Promise<void> {
    // 默認清理實現
  }
}
```

### 驗證階段

```typescript
// validation-stage.ts
export class ValidationStage extends PipelineStage {
  name = 'validation';
  
  async execute(preParticle: PreParticle): Promise<PreParticle> {
    preParticle.state = PreParticleState.VALIDATING;
    
    const config = preParticle.config;
    
    // 1. 驗證必需字段
    if (!config.id || !config.type) {
      throw new Error('Missing required fields: id or type');
    }
    
    // 2. 驗證ID唯一性
    if (await this.isIdDuplicate(config.id)) {
      throw new Error(`Particle ID ${config.id} already exists`);
    }
    
    // 3. 驗證資源需求
    if (!this.validateResourceRequirements(config.resources)) {
      throw new Error('Invalid resource requirements');
    }
    
    // 4. 驗證屬性
    if (!this.validateProperties(config.properties, config.type)) {
      throw new Error('Invalid particle properties');
    }
    
    // 5. 驗證依賴存在性
    for (const depId of config.dependencies) {
      if (!await this.dependencyExists(depId)) {
        throw new Error(`Dependency ${depId} does not exist`);
      }
    }
    
    // 6. 檢查循環依賴
    if (await this.hasCircularDependency(config)) {
      throw new Error('Circular dependency detected');
    }
    
    return preParticle;
  }
  
  private async isIdDuplicate(id: string): Promise<boolean> {
    // 檢查ID是否已存在
    return false; // 實現細節
  }
  
  private validateResourceRequirements(resources: ResourceRequirements): boolean {
    if (resources.memory <= 0) return false;
    if (resources.gpuMemory && resources.gpuMemory <= 0) return false;
    if (resources.computeUnits && resources.computeUnits <= 0) return false;
    return true;
  }
  
  private validateProperties(
    properties: Record<string, any>,
    type: ParticleType
  ): boolean {
    // 根據粒子類型驗證屬性
    const schema = this.getSchemaForType(type);
    return this.validateAgainstSchema(properties, schema);
  }
  
  private getSchemaForType(type: ParticleType): any {
    // 返回類型對應的schema
    return {}; // 實現細節
  }
  
  private validateAgainstSchema(data: any, schema: any): boolean {
    // JSON Schema驗證
    return true; // 實現細節
  }
  
  private async dependencyExists(depId: string): Promise<boolean> {
    // 檢查依賴是否存在
    return true; // 實現細節
  }
  
  private async hasCircularDependency(config: PreParticleConfig): Promise<boolean> {
    // 使用DFS檢測循環依賴
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    
    return this.detectCycle(config.id, visited, recursionStack);
  }
  
  private async detectCycle(
    id: string,
    visited: Set<string>,
    recursionStack: Set<string>
  ): Promise<boolean> {
    if (recursionStack.has(id)) return true;
    if (visited.has(id)) return false;
    
    visited.add(id);
    recursionStack.add(id);
    
    const deps = await this.getDependencies(id);
    for (const dep of deps) {
      if (await this.detectCycle(dep, visited, recursionStack)) {
        return true;
      }
    }
    
    recursionStack.delete(id);
    return false;
  }
  
  private async getDependencies(id: string): Promise<string[]> {
    // 獲取粒子的依賴列表
    return []; // 實現細節
  }
}
```

### 依賴解析階段

```typescript
// dependency-resolution-stage.ts
export class DependencyResolutionStage extends PipelineStage {
  name = 'dependency-resolution';
  private dependencyGraph: Map<string, PreParticle> = new Map();
  
  async execute(preParticle: PreParticle): Promise<PreParticle> {
    preParticle.state = PreParticleState.RESOLVING_DEPS;
    
    // 解析所有依賴
    const dependencies: PreParticle[] = [];
    
    for (const depId of preParticle.config.dependencies) {
      const dep = await this.resolveDependency(depId);
      
      // 確保依賴已就緒
      if (dep.state !== PreParticleState.READY) {
        // 等待依賴就緒
        await this.waitForDependency(dep);
      }
      
      dependencies.push(dep);
    }
    
    preParticle.dependencies = dependencies;
    
    // 計算拓撲排序
    const sortedDeps = this.topologicalSort(dependencies);
    preParticle.dependencies = sortedDeps;
    
    return preParticle;
  }
  
  private async resolveDependency(depId: string): Promise<PreParticle> {
    // 從緩存或存儲中獲取依賴
    if (this.dependencyGraph.has(depId)) {
      return this.dependencyGraph.get(depId)!;
    }
    
    // 加載依賴
    const dep = await this.loadDependency(depId);
    this.dependencyGraph.set(depId, dep);
    
    return dep;
  }
  
  private async loadDependency(depId: string): Promise<PreParticle> {
    // 從存儲加載依賴
    return {} as PreParticle; // 實現細節
  }
  
  private async waitForDependency(dep: PreParticle, timeout: number = 30000): Promise<void> {
    const startTime = Date.now();
    
    while (dep.state !== PreParticleState.READY) {
      if (Date.now() - startTime > timeout) {
        throw new Error(`Dependency ${dep.config.id} timeout`);
      }
      
      if (dep.state === PreParticleState.FAILED) {
        throw new Error(`Dependency ${dep.config.id} failed`);
      }
      
      await this.sleep(100);
    }
  }
  
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  private topologicalSort(dependencies: PreParticle[]): PreParticle[] {
    const sorted: PreParticle[] = [];
    const visited = new Set<string>();
    
    const visit = (particle: PreParticle) => {
      if (visited.has(particle.config.id)) return;
      visited.add(particle.config.id);
      
      for (const dep of particle.dependencies) {
        visit(dep);
      }
      
      sorted.push(particle);
    };
    
    for (const dep of dependencies) {
      visit(dep);
    }
    
    return sorted;
  }
}
```

### 資源分配階段

```typescript
// resource-allocation-stage.ts
export class ResourceAllocationStage extends PipelineStage {
  name = 'resource-allocation';
  private memoryAllocator: MemoryAllocator;
  private gpuAllocator?: GPUBufferAllocator;
  
  constructor() {
    super();
    this.memoryAllocator = new MemoryAllocator();
    if (typeof GPU !== 'undefined') {
      this.gpuAllocator = new GPUBufferAllocator();
    }
  }
  
  async execute(preParticle: PreParticle): Promise<PreParticle> {
    preParticle.state = PreParticleState.ALLOCATING;
    
    const requirements = preParticle.config.resources;
    
    // 1. 分配CPU記憶體
    const memoryHandle = await this.memoryAllocator.allocate(requirements.memory);
    if (!memoryHandle) {
      throw new Error('Failed to allocate memory');
    }
    
    preParticle.allocatedResources.memoryHandle = memoryHandle;
    
    // 2. 分配GPU記憶體（如果需要）
    if (requirements.gpuMemory && this.gpuAllocator) {
      const gpuBuffer = await this.gpuAllocator.allocate(requirements.gpuMemory);
      if (!gpuBuffer) {
        // 回滾CPU記憶體分配
        await this.memoryAllocator.deallocate(memoryHandle);
        throw new Error('Failed to allocate GPU memory');
      }
      preParticle.allocatedResources.gpuBufferHandle = gpuBuffer;
    }
    
    // 3. 分配計算資源（如果需要）
    if (requirements.computeUnits) {
      const computeContext = await this.allocateComputeResources(requirements.computeUnits);
      preParticle.allocatedResources.computeContext = computeContext;
    }
    
    return preParticle;
  }
  
  async cleanup(preParticle: PreParticle): Promise<void> {
    const resources = preParticle.allocatedResources;
    
    // 釋放所有已分配的資源
    if (resources.memoryHandle) {
      await this.memoryAllocator.deallocate(resources.memoryHandle);
    }
    
    if (resources.gpuBufferHandle && this.gpuAllocator) {
      await this.gpuAllocator.deallocate(resources.gpuBufferHandle);
    }
    
    if (resources.computeContext) {
      await this.releaseComputeResources(resources.computeContext);
    }
  }
  
  private async allocateComputeResources(units: number): Promise<ComputeContext> {
    // 分配計算資源
    return {} as ComputeContext; // 實現細節
  }
  
  private async releaseComputeResources(context: ComputeContext): Promise<void> {
    // 釋放計算資源
  }
}

// 記憶體分配器
export class MemoryAllocator {
  private pool: Map<string, MemoryBlock> = new Map();
  private totalAllocated: number = 0;
  private maxMemory: number = 1024 * 1024 * 1024; // 1GB
  
  async allocate(size: number): Promise<MemoryHandle | null> {
    if (this.totalAllocated + size > this.maxMemory) {
      // 嘗試垃圾回收
      await this.garbageCollect();
      
      if (this.totalAllocated + size > this.maxMemory) {
        return null;
      }
    }
    
    const handle: MemoryHandle = {
      id: this.generateId(),
      size,
      address: this.allocateBlock(size)
    };
    
    this.pool.set(handle.id, {
      handle,
      allocated: Date.now()
    });
    
    this.totalAllocated += size;
    
    return handle;
  }
  
  async deallocate(handle: MemoryHandle): Promise<void> {
    if (this.pool.has(handle.id)) {
      this.freeBlock(handle.address, handle.size);
      this.pool.delete(handle.id);
      this.totalAllocated -= handle.size;
    }
  }
  
  private async garbageCollect(): Promise<void> {
    // 實現垃圾回收邏輯
  }
  
  private generateId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private allocateBlock(size: number): number {
    // 實際記憶體分配
    return 0; // 實現細節
  }
  
  private freeBlock(address: number, size: number): void {
    // 實際記憶體釋放
  }
}

interface MemoryHandle {
  id: string;
  size: number;
  address: number;
}

interface MemoryBlock {
  handle: MemoryHandle;
  allocated: number;
}

interface ComputeContext {
  id: string;
  units: number;
}
```

---

## 流程圖

### 完整創建流程

```
開始
  │
  ↓
┌──────────────────┐
│  接收創建請求     │
│  PreParticleConfig│
└──────────────────┘
  │
  ↓
┌──────────────────┐
│   驗證階段        │
│ • 檢查必需字段    │
│ • 驗證唯一性      │
│ • 檢查循環依賴    │
└──────────────────┘
  │
  ├─[失敗]→ 錯誤處理 → 結束
  │
  ↓ [成功]
┌──────────────────┐
│  依賴解析階段     │
│ • 加載依賴        │
│ • 等待依賴就緒    │
│ • 拓撲排序        │
└──────────────────┘
  │
  ├─[失敗]→ 清理資源 → 結束
  │
  ↓ [成功]
┌──────────────────┐
│  資源分配階段     │
│ • CPU記憶體       │
│ • GPU記憶體       │
│ • 計算資源        │
└──────────────────┘
  │
  ├─[失敗]→ 回滾分配 → 結束
  │
  ↓ [成功]
┌──────────────────┐
│  初始化階段       │
│ • 設置屬性        │
│ • 建立連接        │
│ • 註冊事件        │
└──────────────────┘
  │
  ├─[失敗]→ 完全回滾 → 結束
  │
  ↓ [成功]
┌──────────────────┐
│   就緒階段        │
│ • 標記為READY     │
│ • 通知監聽器      │
│ • 返回PreParticle │
└──────────────────┘
  │
  ↓
結束（成功）
```

### 並發處理流程

```
┌─────────────────────────────────────────────────────┐
│              Pre-Particle Request Queue             │
│  [Req1] [Req2] [Req3] [Req4] [Req5] ...            │
└─────────────────────────────────────────────────────┘
        │        │        │        │        │
        ↓        ↓        ↓        ↓        ↓
┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│ Worker 1 ││ Worker 2 ││ Worker 3 ││ Worker 4 │
│          ││          ││          ││          │
│ Pipeline ││ Pipeline ││ Pipeline ││ Pipeline │
└──────────┘└──────────┘└──────────┘└──────────┘
        │        │        │        │
        ↓        ↓        ↓        ↓
┌─────────────────────────────────────────────────────┐
│           Resource Coordination Layer               │
│  • Memory Pool Management                           │
│  • GPU Resource Scheduling                          │
│  • Dependency Graph Sync                            │
└─────────────────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────────────────┐
│              Completed Particles Pool               │
│  Ready particles awaiting activation                │
└─────────────────────────────────────────────────────┘
```

---

## 前粒子狀態機

### 狀態轉換圖

```
                    ┌──────────────┐
                    │   PENDING    │
                    └──────────────┘
                           │
                           ↓
                    ┌──────────────┐
              ┌────→│  VALIDATING  │────┐
              │     └──────────────┘    │
              │            │             │
              │            ↓             │
              │     ┌──────────────┐    │
              │     │ RESOLVING_   │    │
              │     │   DEPS       │    │
              │     └──────────────┘    │
              │            │             │
              │            ↓             │
              │     ┌──────────────┐    │
              │     │ ALLOCATING   │    │
              │     └──────────────┘    │
              │            │             │
        [Retry]            ↓             │
              │     ┌──────────────┐    │
              │     │INITIALIZING  │    │
              │     └──────────────┘    │
              │            │             │
              │            ↓             │
              │     ┌──────────────┐    │
              └─────│    READY     │    │
                    └──────────────┘    │
                           │             │
                           │             │
                           │        [Error]
                           │             │
                           │             ↓
                           │      ┌──────────────┐
                           │      │    FAILED    │
                           │      └──────────────┘
                           │
                    [Cancel]
                           │
                           ↓
                    ┌──────────────┐
                    │  CANCELLED   │
                    └──────────────┘
```

### 狀態管理器

```typescript
// pre-particle-state-machine.ts
export class PreParticleStateMachine {
  private currentState: PreParticleState;
  private preParticle: PreParticle;
  private transitions: Map<PreParticleState, PreParticleState[]>;
  private listeners: Map<PreParticleState, Function[]> = new Map();
  
  constructor(preParticle: PreParticle) {
    this.preParticle = preParticle;
    this.currentState = preParticle.state;
    this.initializeTransitions();
  }
  
  private initializeTransitions(): void {
    this.transitions = new Map([
      [PreParticleState.PENDING, [
        PreParticleState.VALIDATING,
        PreParticleState.CANCELLED
      ]],
      [PreParticleState.VALIDATING, [
        PreParticleState.RESOLVING_DEPS,
        PreParticleState.FAILED,
        PreParticleState.CANCELLED
      ]],
      [PreParticleState.RESOLVING_DEPS, [
        PreParticleState.ALLOCATING,
        PreParticleState.FAILED,
        PreParticleState.CANCELLED
      ]],
      [PreParticleState.ALLOCATING, [
        PreParticleState.INITIALIZING,
        PreParticleState.FAILED,
        PreParticleState.CANCELLED
      ]],
      [PreParticleState.INITIALIZING, [
        PreParticleState.READY,
        PreParticleState.FAILED,
        PreParticleState.VALIDATING, // Retry
        PreParticleState.CANCELLED
      ]],
      [PreParticleState.READY, []],
      [PreParticleState.FAILED, [
        PreParticleState.VALIDATING // Retry
      ]],
      [PreParticleState.CANCELLED, []]
    ]);
  }
  
  transition(newState: PreParticleState): boolean {
    const allowedTransitions = this.transitions.get(this.currentState) || [];
    
    if (!allowedTransitions.includes(newState)) {
      console.error(
        `Invalid transition from ${this.currentState} to ${newState}`
      );
      return false;
    }
    
    const oldState = this.currentState;
    this.currentState = newState;
    this.preParticle.state = newState;
    this.preParticle.updatedAt = Date.now();
    
    // 觸發狀態變更監聽器
    this.notifyListeners(oldState, newState);
    
    return true;
  }
  
  onStateChange(state: PreParticleState, callback: Function): void {
    if (!this.listeners.has(state)) {
      this.listeners.set(state, []);
    }
    this.listeners.get(state)!.push(callback);
  }
  
  private notifyListeners(oldState: PreParticleState, newState: PreParticleState): void {
    const callbacks = this.listeners.get(newState) || [];
    callbacks.forEach(callback => {
      try {
        callback(this.preParticle, oldState, newState);
      } catch (error) {
        console.error('Listener error:', error);
      }
    });
  }
  
  canTransitionTo(state: PreParticleState): boolean {
    const allowedTransitions = this.transitions.get(this.currentState) || [];
    return allowedTransitions.includes(state);
  }
  
  getCurrentState(): PreParticleState {
    return this.currentState;
  }
}
```

---

## 整合實現步驟

### 步驟 1: 初始化前粒子管理器

```typescript
// step1-initialize-manager.ts
import { PreParticlePipeline } from './pre-particle-pipeline';
import { PreParticleManager } from './pre-particle-manager';

// 創建前粒子管理器
const manager = new PreParticleManager({
  maxConcurrentProcessing: 10,
  defaultTimeout: 30000,
  enableRetry: true,
  retryPolicy: {
    maxRetries: 3,
    backoffMultiplier: 2,
    initialDelay: 1000,
    maxDelay: 10000
  }
});

// 初始化管理器
await manager.initialize();

console.log('Pre-Particle Manager initialized');
```

### 步驟 2: 定義粒子配置

```typescript
// step2-define-config.ts
const particleConfig: PreParticleConfig = {
  id: 'neural-particle-001',
  type: ParticleType.NEURAL,
  properties: {
    layers: [128, 64, 32],
    activationFunction: 'relu',
    learningRate: 0.001,
    momentum: 0.9
  },
  dependencies: [
    'data-loader-001',
    'optimizer-001'
  ],
  resources: {
    memory: 1024 * 1024 * 100, // 100MB
    gpuMemory: 1024 * 1024 * 500, // 500MB
    computeUnits: 4
  },
  priority: 5,
  timeout: 60000,
  retryPolicy: {
    maxRetries: 3,
    backoffMultiplier: 2,
    initialDelay: 1000,
    maxDelay: 10000
  }
};
```

### 步驟 3: 提交粒子創建請求

```typescript
// step3-submit-request.ts
// 提交單個粒子
const preParticle = await manager.createParticle(particleConfig);

console.log('Pre-Particle created:', preParticle.config.id);
console.log('State:', preParticle.state);

// 批次提交多個粒子
const configs: PreParticleConfig[] = [
  particleConfig1,
  particleConfig2,
  particleConfig3
];

const preParticles = await manager.createParticlesBatch(configs);

console.log(`Created ${preParticles.length} pre-particles`);
```

### 步驟 4: 監控粒子狀態

```typescript
// step4-monitor-state.ts
// 監聽狀態變化
manager.on('particle:state-change', (event) => {
  console.log(`Particle ${event.particleId} state changed:`);
  console.log(`  From: ${event.oldState}`);
  console.log(`  To: ${event.newState}`);
});

// 監聽特定狀態
manager.on('particle:ready', (particle) => {
  console.log(`Particle ${particle.config.id} is ready!`);
  // 可以開始使用該粒子
});

manager.on('particle:failed', (particle) => {
  console.error(`Particle ${particle.config.id} failed:`);
  console.error(particle.errors);
});

// 查詢粒子狀態
const state = await manager.getParticleState('neural-particle-001');
console.log('Current state:', state);

// 等待粒子就緒
await manager.waitForReady('neural-particle-001', 30000);
console.log('Particle is now ready');
```

### 步驟 5: 激活粒子

```typescript
// step5-activate-particle.ts
// 當前粒子就緒後，可以激活它
const activatedParticle = await manager.activateParticle('neural-particle-001');

console.log('Particle activated:', activatedParticle.id);

// 使用激活的粒子
const result = await activatedParticle.process(inputData);
console.log('Processing result:', result);
```

---

## 實現範例

### 完整實現範例

```typescript
// complete-example.ts
import {
  PreParticleManager,
  PreParticleConfig,
  PreParticleState,
  ParticleType
} from './pre-particle-system';

async function completeWorkflow() {
  // 1. 初始化管理器
  const manager = new PreParticleManager({
    maxConcurrentProcessing: 10,
    defaultTimeout: 30000,
    enableRetry: true
  });
  
  await manager.initialize();
  console.log('✓ Manager initialized');
  
  // 2. 定義粒子配置
  const configs: PreParticleConfig[] = [
    {
      id: 'data-loader',
      type: ParticleType.DATA,
      properties: {
        source: 'database',
        batchSize: 32
      },
      dependencies: [],
      resources: {
        memory: 1024 * 1024 * 50
      },
      priority: 10,
      timeout: 60000,
      retryPolicy: {
        maxRetries: 3,
        backoffMultiplier: 2,
        initialDelay: 1000,
        maxDelay: 10000
      }
    },
    {
      id: 'neural-network',
      type: ParticleType.NEURAL,
      properties: {
        architecture: 'transformer',
        layers: [512, 256, 128]
      },
      dependencies: ['data-loader'],
      resources: {
        memory: 1024 * 1024 * 200,
        gpuMemory: 1024 * 1024 * 1000,
        computeUnits: 8
      },
      priority: 5,
      timeout: 120000,
      retryPolicy: {
        maxRetries: 2,
        backoffMultiplier: 2,
        initialDelay: 2000,
        maxDelay: 10000
      }
    },
    {
      id: 'output-processor',
      type: ParticleType.PROCESSOR,
      properties: {
        format: 'json',
        compression: true
      },
      dependencies: ['neural-network'],
      resources: {
        memory: 1024 * 1024 * 30
      },
      priority: 3,
      timeout: 30000,
      retryPolicy: {
        maxRetries: 3,
        backoffMultiplier: 1.5,
        initialDelay: 500,
        maxDelay: 5000
      }
    }
  ];
  
  // 3. 設置監聽器
  manager.on('particle:state-change', (event) => {
    console.log(`[${event.particleId}] ${event.oldState} → ${event.newState}`);
  });
  
  manager.on('particle:ready', (particle) => {
    console.log(`✓ [${particle.config.id}] Ready!`);
  });
  
  manager.on('particle:failed', (particle) => {
    console.error(`✗ [${particle.config.id}] Failed:`, particle.errors);
  });
  
  // 4. 批次創建粒子
  console.log('\nCreating particles...');
  const preParticles = await manager.createParticlesBatch(configs);
  console.log(`Created ${preParticles.length} pre-particles`);
  
  // 5. 等待所有粒子就緒
  console.log('\nWaiting for particles to be ready...');
  await Promise.all(
    preParticles.map(p => manager.waitForReady(p.config.id, 180000))
  );
  console.log('All particles ready!');
  
  // 6. 激活粒子並使用
  console.log('\nActivating particles...');
  const particles = await Promise.all(
    preParticles.map(p => manager.activateParticle(p.config.id))
  );
  
  // 7. 執行工作流
  console.log('\nExecuting workflow...');
  const dataLoader = particles.find(p => p.id === 'data-loader')!;
  const neuralNet = particles.find(p => p.id === 'neural-network')!;
  const outputProc = particles.find(p => p.id === 'output-processor')!;
  
  // 加載數據
  const data = await dataLoader.load();
  console.log('✓ Data loaded');
  
  // 神經網絡處理
  const prediction = await neuralNet.predict(data);
  console.log('✓ Prediction complete');
  
  // 輸出處理
  const result = await outputProc.process(prediction);
  console.log('✓ Output processed');
  
  console.log('\n Final result:', result);
  
  // 8. 清理
  await manager.shutdown();
  console.log('\n✓ Workflow complete');
}

// 執行完整工作流
completeWorkflow().catch(console.error);
```

---

## 性能考量與優化

### 並發控制

```typescript
// concurrency-control.ts
export class ConcurrencyController {
  private maxConcurrent: number;
  private activeCount: number = 0;
  private queue: Array<() => Promise<void>> = [];
  
  constructor(maxConcurrent: number = 10) {
    this.maxConcurrent = maxConcurrent;
  }
  
  async execute<T>(task: () => Promise<T>): Promise<T> {
    while (this.activeCount >= this.maxConcurrent) {
      await this.waitForSlot();
    }
    
    this.activeCount++;
    
    try {
      return await task();
    } finally {
      this.activeCount--;
      this.processQueue();
    }
  }
  
  private waitForSlot(): Promise<void> {
    return new Promise((resolve) => {
      this.queue.push(async () => resolve());
    });
  }
  
  private processQueue(): void {
    if (this.queue.length > 0 && this.activeCount < this.maxConcurrent) {
      const task = this.queue.shift();
      if (task) task();
    }
  }
}
```

### 資源池優化

```typescript
// resource-pool-optimization.ts
export class ResourcePool<T> {
  private pool: T[] = [];
  private inUse: Set<T> = new Set();
  private factory: () => Promise<T>;
  private maxSize: number;
  
  constructor(factory: () => Promise<T>, maxSize: number = 100) {
    this.factory = factory;
    this.maxSize = maxSize;
  }
  
  async acquire(): Promise<T> {
    // 從池中獲取空閒資源
    if (this.pool.length > 0) {
      const resource = this.pool.pop()!;
      this.inUse.add(resource);
      return resource;
    }
    
    // 創建新資源（如果未達上限）
    if (this.inUse.size < this.maxSize) {
      const resource = await this.factory();
      this.inUse.add(resource);
      return resource;
    }
    
    // 等待資源釋放
    return this.waitForResource();
  }
  
  release(resource: T): void {
    if (this.inUse.has(resource)) {
      this.inUse.delete(resource);
      this.pool.push(resource);
    }
  }
  
  private async waitForResource(): Promise<T> {
    // 輪詢等待資源釋放
    while (this.pool.length === 0) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return this.acquire();
  }
  
  clear(): void {
    this.pool = [];
    this.inUse.clear();
  }
}
```

---

## 故障排除與最佳實踐

### 常見問題與解決方案

#### 問題1: 循環依賴

```typescript
// 錯誤示例
const configA: PreParticleConfig = {
  id: 'particle-a',
  dependencies: ['particle-b'], // 依賴B
  // ...
};

const configB: PreParticleConfig = {
  id: 'particle-b',
  dependencies: ['particle-a'], // 依賴A（循環！）
  // ...
};

// 解決方案：重構依賴關係
const configShared: PreParticleConfig = {
  id: 'particle-shared',
  dependencies: [], // 無依賴
  // ...
};

const configA: PreParticleConfig = {
  id: 'particle-a',
  dependencies: ['particle-shared'], // 依賴共享粒子
  // ...
};

const configB: PreParticleConfig = {
  id: 'particle-b',
  dependencies: ['particle-shared'], // 依賴共享粒子
  // ...
};
```

#### 問題2: 資源耗盡

```typescript
// 監控資源使用
manager.on('resource:low-memory', () => {
  console.warn('Low memory detected, triggering cleanup');
  // 觸發垃圾回收
  manager.garbageCollect();
});

// 設置資源限制
const limitedConfig: PreParticleConfig = {
  // ...
  resources: {
    memory: Math.min(requestedMemory, availableMemory * 0.8),
    gpuMemory: Math.min(requestedGpu, availableGpu * 0.7)
  }
};
```

### 最佳實踐

1. **合理設置超時時間**
```typescript
// 根據粒子複雜度設置超時
const timeout = estimateInitTime(config) * 2;
```

2. **使用優先級調度**
```typescript
// 關鍵粒子優先處理
const criticalConfig: PreParticleConfig = {
  // ...
  priority: 10 // 最高優先級
};
```

3. **實現重試機制**
```typescript
// 指數退避重試
const retryPolicy: RetryPolicy = {
  maxRetries: 3,
  backoffMultiplier: 2,
  initialDelay: 1000,
  maxDelay: 10000
};
```

4. **監控和日誌**
```typescript
// 詳細日誌
manager.on('*', (event) => {
  logger.info({
    timestamp: Date.now(),
    event: event.type,
    particle: event.particleId,
    details: event.data
  });
});
```

---

**怎麼過去，就怎麼回來**

*Last Updated: 2026-01-26T12:00:00Z*
