---
title: "終端系統立體種子整合"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: ["terminal", "seed-architecture", "3d-integration", "cli", "system-core", "terminal-interface"]
---

# 終端系統立體種子整合

<!-- origin_signature: MrLiouWord -->

## 目錄

1. [概述](#概述)
2. [立體種子架構](#立體種子架構)
3. [終端介面整合](#終端介面整合)
4. [命令系統設計](#命令系統設計)
5. [3D種子可視化](#3d種子可視化)
6. [種子生命週期管理](#種子生命週期管理)
7. [終端命令參考](#終端命令參考)
8. [實現範例](#實現範例)
9. [進階特性](#進階特性)

---

## 概述

終端系統立體種子整合是MrLiouWord系統的核心創新，將傳統的2D終端介面擴展為3D立體空間，使得命令行操作能夠在三維空間中操縱和管理種子實體。這種架構將命令行的簡潔性與三維空間的直觀性完美結合。

### 核心概念

**立體種子（3D Seed）** 是系統中的基本實體單元，具有以下特性：

- **三維位置**: 在3D空間中的精確座標 (x, y, z)
- **多層結構**: 包含核心層、邏輯層、展示層
- **動態演化**: 隨時間和交互而變化
- **網絡連接**: 種子之間形成複雜的關聯網絡
- **終端可控**: 通過命令行完全控制種子行為

### 系統特性

- 🎯 **3D空間操作**: 在終端中操縱三維種子
- 💻 **命令行驅動**: 強大的CLI命令系統
- 🌐 **網絡拓撲**: 種子間的動態連接關係
- 🔄 **實時同步**: 終端命令與3D空間實時同步
- 📊 **可視化輸出**: ASCII藝術和彩色終端輸出

---

## 立體種子架構

### 種子結構定義

```typescript
// seed-structure.ts
export interface Seed3D {
  // 基本屬性
  id: string;
  type: SeedType;
  name: string;
  
  // 空間屬性
  position: Vector3D;
  rotation: Quaternion;
  scale: Vector3D;
  
  // 層次結構
  layers: SeedLayers;
  
  // 連接關係
  connections: SeedConnection[];
  
  // 狀態
  state: SeedState;
  health: number;
  energy: number;
  
  // 行為
  behaviors: SeedBehavior[];
  
  // 元數據
  metadata: SeedMetadata;
  
  // 生命週期
  lifecycle: SeedLifecycle;
}

export interface Vector3D {
  x: number;
  y: number;
  z: number;
}

export interface Quaternion {
  x: number;
  y: number;
  z: number;
  w: number;
}

export interface SeedLayers {
  core: CoreLayer;      // 核心層：基本邏輯和狀態
  logic: LogicLayer;    // 邏輯層：業務邏輯
  display: DisplayLayer; // 展示層：視覺表現
}

export interface CoreLayer {
  kernel: SeedKernel;
  memory: MemoryBlock;
  processor: ProcessorUnit;
}

export interface LogicLayer {
  rules: Rule[];
  triggers: Trigger[];
  actions: Action[];
}

export interface DisplayLayer {
  appearance: Appearance;
  animation: Animation;
  effects: Effect[];
}

export interface SeedConnection {
  targetId: string;
  type: ConnectionType;
  strength: number;
  bidirectional: boolean;
  data: any;
}

export enum SeedType {
  ROOT = 'root',           // 根種子
  BRANCH = 'branch',       // 分支種子
  LEAF = 'leaf',           // 葉子種子
  FRUIT = 'fruit',         // 果實種子
  FLOWER = 'flower',       // 花朵種子
  NEURAL = 'neural',       // 神經種子
  PARTICLE = 'particle'    // 粒子種子
}

export enum SeedState {
  DORMANT = 'dormant',     // 休眠
  GERMINATING = 'germinating', // 發芽
  GROWING = 'growing',     // 生長
  MATURE = 'mature',       // 成熟
  FLOWERING = 'flowering', // 開花
  FRUITING = 'fruiting',   // 結果
  DECAYING = 'decaying',   // 衰退
  DEAD = 'dead'            // 死亡
}

export enum ConnectionType {
  PARENT_CHILD = 'parent-child',
  SIBLING = 'sibling',
  NEURAL = 'neural',
  DATA_FLOW = 'data-flow',
  ENERGY = 'energy',
  SIGNAL = 'signal'
}
```

### 種子架構圖

```
                 ┌────────────────────────┐
                 │     Seed 3D Entity     │
                 └────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│  Core Layer   │  │ Logic Layer  │  │Display Layer │
│               │  │              │  │              │
│ • Kernel      │  │ • Rules      │  │ • Appearance │
│ • Memory      │  │ • Triggers   │  │ • Animation  │
│ • Processor   │  │ • Actions    │  │ • Effects    │
└───────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ↓
                 ┌────────────────────────┐
                 │   Seed Connections     │
                 │   Network Topology     │
                 └────────────────────────┘
```

### 種子層次實現

```typescript
// seed-layers.ts
export class SeedLayerManager {
  private seed: Seed3D;
  
  constructor(seed: Seed3D) {
    this.seed = seed;
  }
  
  // 核心層操作
  updateCoreLayer(updates: Partial<CoreLayer>): void {
    this.seed.layers.core = {
      ...this.seed.layers.core,
      ...updates
    };
    this.propagateChanges('core');
  }
  
  // 邏輯層操作
  addRule(rule: Rule): void {
    this.seed.layers.logic.rules.push(rule);
    this.compileRules();
  }
  
  addTrigger(trigger: Trigger): void {
    this.seed.layers.logic.triggers.push(trigger);
    this.registerTrigger(trigger);
  }
  
  // 展示層操作
  updateAppearance(appearance: Partial<Appearance>): void {
    this.seed.layers.display.appearance = {
      ...this.seed.layers.display.appearance,
      ...appearance
    };
    this.refreshDisplay();
  }
  
  addEffect(effect: Effect): void {
    this.seed.layers.display.effects.push(effect);
    this.applyEffect(effect);
  }
  
  // 層間通信
  private propagateChanges(layer: string): void {
    switch (layer) {
      case 'core':
        this.updateLogicFromCore();
        this.updateDisplayFromCore();
        break;
      case 'logic':
        this.updateDisplayFromLogic();
        break;
      case 'display':
        // 展示層通常不影響其他層
        break;
    }
  }
  
  private updateLogicFromCore(): void {
    // 根據核心層狀態更新邏輯層
  }
  
  private updateDisplayFromCore(): void {
    // 根據核心層狀態更新展示層
  }
  
  private updateDisplayFromLogic(): void {
    // 根據邏輯層狀態更新展示層
  }
  
  private compileRules(): void {
    // 編譯規則為可執行代碼
  }
  
  private registerTrigger(trigger: Trigger): void {
    // 註冊觸發器
  }
  
  private refreshDisplay(): void {
    // 刷新顯示
  }
  
  private applyEffect(effect: Effect): void {
    // 應用視覺效果
  }
}
```

---

## 終端介面整合

### 終端系統架構

```typescript
// terminal-system.ts
export class TerminalSeedSystem {
  private seeds: Map<string, Seed3D> = new Map();
  private commandProcessor: CommandProcessor;
  private renderer: TerminalRenderer;
  private space3D: Space3D;
  
  constructor() {
    this.commandProcessor = new CommandProcessor(this);
    this.renderer = new TerminalRenderer();
    this.space3D = new Space3D();
    this.initializeCommands();
  }
  
  private initializeCommands(): void {
    // 註冊所有命令
    this.commandProcessor.registerCommand(new CreateSeedCommand(this));
    this.commandProcessor.registerCommand(new MoveSeedCommand(this));
    this.commandProcessor.registerCommand(new ConnectSeedCommand(this));
    this.commandProcessor.registerCommand(new ListSeedsCommand(this));
    this.commandProcessor.registerCommand(new InspectSeedCommand(this));
    this.commandProcessor.registerCommand(new EvolveSeedCommand(this));
    this.commandProcessor.registerCommand(new VisualizeSeedCommand(this));
  }
  
  async executeCommand(input: string): Promise<CommandResult> {
    const result = await this.commandProcessor.process(input);
    
    // 渲染結果
    this.renderer.render(result);
    
    return result;
  }
  
  // 種子管理
  createSeed(config: SeedConfig): Seed3D {
    const seed = this.buildSeed(config);
    this.seeds.set(seed.id, seed);
    this.space3D.addSeed(seed);
    return seed;
  }
  
  getSeed(id: string): Seed3D | undefined {
    return this.seeds.get(id);
  }
  
  listSeeds(filter?: SeedFilter): Seed3D[] {
    let seeds = Array.from(this.seeds.values());
    
    if (filter) {
      seeds = this.applyFilter(seeds, filter);
    }
    
    return seeds;
  }
  
  deleteSeed(id: string): boolean {
    const seed = this.seeds.get(id);
    if (!seed) return false;
    
    this.space3D.removeSeed(seed);
    this.seeds.delete(id);
    return true;
  }
  
  // 空間操作
  moveSeed(id: string, position: Vector3D): void {
    const seed = this.seeds.get(id);
    if (seed) {
      seed.position = position;
      this.space3D.updateSeedPosition(seed);
    }
  }
  
  connectSeeds(sourceId: string, targetId: string, type: ConnectionType): void {
    const source = this.seeds.get(sourceId);
    const target = this.seeds.get(targetId);
    
    if (source && target) {
      const connection: SeedConnection = {
        targetId,
        type,
        strength: 1.0,
        bidirectional: false,
        data: {}
      };
      source.connections.push(connection);
    }
  }
  
  private buildSeed(config: SeedConfig): Seed3D {
    return {
      id: config.id || this.generateId(),
      type: config.type,
      name: config.name,
      position: config.position || { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0, w: 1 },
      scale: { x: 1, y: 1, z: 1 },
      layers: this.initializeLayers(config),
      connections: [],
      state: SeedState.GERMINATING,
      health: 100,
      energy: 100,
      behaviors: [],
      metadata: config.metadata || {},
      lifecycle: this.createLifecycle()
    };
  }
  
  private initializeLayers(config: SeedConfig): SeedLayers {
    return {
      core: this.createCoreLayer(config),
      logic: this.createLogicLayer(config),
      display: this.createDisplayLayer(config)
    };
  }
  
  private createCoreLayer(config: SeedConfig): CoreLayer {
    return {
      kernel: { version: '1.0.0', mode: 'active' },
      memory: { size: 1024 * 1024, used: 0 },
      processor: { cores: 1, frequency: 1.0 }
    };
  }
  
  private createLogicLayer(config: SeedConfig): LogicLayer {
    return {
      rules: config.rules || [],
      triggers: config.triggers || [],
      actions: config.actions || []
    };
  }
  
  private createDisplayLayer(config: SeedConfig): DisplayLayer {
    return {
      appearance: config.appearance || { color: 'green', shape: 'sphere' },
      animation: { type: 'idle', speed: 1.0 },
      effects: []
    };
  }
  
  private createLifecycle(): SeedLifecycle {
    return {
      createdAt: Date.now(),
      updatedAt: Date.now(),
      age: 0,
      stage: 0
    };
  }
  
  private generateId(): string {
    return `seed_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private applyFilter(seeds: Seed3D[], filter: SeedFilter): Seed3D[] {
    return seeds.filter(seed => {
      if (filter.type && seed.type !== filter.type) return false;
      if (filter.state && seed.state !== filter.state) return false;
      if (filter.minHealth && seed.health < filter.minHealth) return false;
      return true;
    });
  }
}
```

### 命令處理器

```typescript
// command-processor.ts
export class CommandProcessor {
  private commands: Map<string, Command> = new Map();
  private system: TerminalSeedSystem;
  
  constructor(system: TerminalSeedSystem) {
    this.system = system;
  }
  
  registerCommand(command: Command): void {
    this.commands.set(command.name, command);
    
    // 註冊別名
    if (command.aliases) {
      command.aliases.forEach(alias => {
        this.commands.set(alias, command);
      });
    }
  }
  
  async process(input: string): Promise<CommandResult> {
    // 解析輸入
    const parsed = this.parseInput(input);
    
    if (!parsed) {
      return {
        success: false,
        error: 'Invalid command syntax',
        output: ''
      };
    }
    
    // 查找命令
    const command = this.commands.get(parsed.command);
    
    if (!command) {
      return {
        success: false,
        error: `Unknown command: ${parsed.command}`,
        output: this.suggestCommands(parsed.command)
      };
    }
    
    // 驗證參數
    const validation = command.validate(parsed.args, parsed.flags);
    if (!validation.valid) {
      return {
        success: false,
        error: validation.error,
        output: command.usage()
      };
    }
    
    // 執行命令
    try {
      return await command.execute(parsed.args, parsed.flags);
    } catch (error) {
      return {
        success: false,
        error: `Command execution failed: ${error.message}`,
        output: ''
      };
    }
  }
  
  private parseInput(input: string): ParsedCommand | null {
    const trimmed = input.trim();
    if (!trimmed) return null;
    
    // 簡單的命令解析
    const parts = trimmed.split(/\s+/);
    const command = parts[0];
    const args: string[] = [];
    const flags: Record<string, any> = {};
    
    for (let i = 1; i < parts.length; i++) {
      const part = parts[i];
      
      if (part.startsWith('--')) {
        // 長選項: --flag=value 或 --flag
        const [key, value] = part.substring(2).split('=');
        flags[key] = value || true;
      } else if (part.startsWith('-')) {
        // 短選項: -f value 或 -f
        const key = part.substring(1);
        const nextPart = parts[i + 1];
        
        if (nextPart && !nextPart.startsWith('-')) {
          flags[key] = nextPart;
          i++;
        } else {
          flags[key] = true;
        }
      } else {
        // 參數
        args.push(part);
      }
    }
    
    return { command, args, flags };
  }
  
  private suggestCommands(input: string): string {
    const commandNames = Array.from(this.commands.keys());
    const suggestions = commandNames
      .filter(name => this.levenshteinDistance(input, name) <= 2)
      .slice(0, 3);
    
    if (suggestions.length > 0) {
      return `Did you mean: ${suggestions.join(', ')}?`;
    }
    
    return 'Type "help" to see available commands.';
  }
  
  private levenshteinDistance(a: string, b: string): number {
    const matrix: number[][] = [];
    
    for (let i = 0; i <= b.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= b.length; i++) {
      for (let j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    return matrix[b.length][a.length];
  }
}

export interface ParsedCommand {
  command: string;
  args: string[];
  flags: Record<string, any>;
}

export interface CommandResult {
  success: boolean;
  error?: string;
  output: string;
  data?: any;
}
```

---

## 命令系統設計

### 命令基類

```typescript
// command-base.ts
export abstract class Command {
  abstract name: string;
  abstract description: string;
  aliases?: string[];
  
  abstract execute(args: string[], flags: Record<string, any>): Promise<CommandResult>;
  
  validate(args: string[], flags: Record<string, any>): ValidationResult {
    return { valid: true };
  }
  
  usage(): string {
    return `Usage: ${this.name} [options]`;
  }
}

export interface ValidationResult {
  valid: boolean;
  error?: string;
}
```

### 創建種子命令

```typescript
// create-seed-command.ts
export class CreateSeedCommand extends Command {
  name = 'create';
  description = 'Create a new 3D seed';
  aliases = ['new', 'spawn'];
  
  private system: TerminalSeedSystem;
  
  constructor(system: TerminalSeedSystem) {
    super();
    this.system = system;
  }
  
  validate(args: string[], flags: Record<string, any>): ValidationResult {
    if (!flags.type && args.length === 0) {
      return {
        valid: false,
        error: 'Seed type is required'
      };
    }
    
    return { valid: true };
  }
  
  async execute(args: string[], flags: Record<string, any>): Promise<CommandResult> {
    const config: SeedConfig = {
      type: flags.type || args[0] as SeedType,
      name: flags.name || args[1] || 'Unnamed Seed',
      position: this.parsePosition(flags),
      appearance: {
        color: flags.color || 'green',
        shape: flags.shape || 'sphere'
      }
    };
    
    const seed = this.system.createSeed(config);
    
    const output = this.formatOutput(seed);
    
    return {
      success: true,
      output,
      data: seed
    };
  }
  
  usage(): string {
    return `
Usage: create [type] [name] [options]

Create a new 3D seed in the terminal system.

Arguments:
  type          Seed type (root|branch|leaf|fruit|flower|neural|particle)
  name          Seed name (optional)

Options:
  --type, -t    Seed type (alternative to positional argument)
  --name, -n    Seed name
  --x           X position (default: 0)
  --y           Y position (default: 0)
  --z           Z position (default: 0)
  --color, -c   Seed color (default: green)
  --shape, -s   Seed shape (default: sphere)

Examples:
  create root "Main Seed"
  create branch --x=10 --y=5 --z=0 --color=blue
  create neural MyNeuron --shape=cube
    `;
  }
  
  private parsePosition(flags: Record<string, any>): Vector3D {
    return {
      x: parseFloat(flags.x || '0'),
      y: parseFloat(flags.y || '0'),
      z: parseFloat(flags.z || '0')
    };
  }
  
  private formatOutput(seed: Seed3D): string {
    return `
✓ Seed created successfully!

  ID:       ${seed.id}
  Type:     ${seed.type}
  Name:     ${seed.name}
  Position: (${seed.position.x}, ${seed.position.y}, ${seed.position.z})
  State:    ${seed.state}
  Health:   ${seed.health}%
  Energy:   ${seed.energy}%
    `.trim();
  }
}
```

### 移動種子命令

```typescript
// move-seed-command.ts
export class MoveSeedCommand extends Command {
  name = 'move';
  description = 'Move a seed to a new position';
  aliases = ['mv', 'relocate'];
  
  private system: TerminalSeedSystem;
  
  constructor(system: TerminalSeedSystem) {
    super();
    this.system = system;
  }
  
  validate(args: string[], flags: Record<string, any>): ValidationResult {
    if (args.length < 1) {
      return {
        valid: false,
        error: 'Seed ID is required'
      };
    }
    
    if (!flags.x && !flags.y && !flags.z && args.length < 4) {
      return {
        valid: false,
        error: 'Target position is required'
      };
    }
    
    return { valid: true };
  }
  
  async execute(args: string[], flags: Record<string, any>): Promise<CommandResult> {
    const seedId = args[0];
    const seed = this.system.getSeed(seedId);
    
    if (!seed) {
      return {
        success: false,
        error: `Seed not found: ${seedId}`,
        output: ''
      };
    }
    
    const position: Vector3D = {
      x: parseFloat(flags.x || args[1] || seed.position.x),
      y: parseFloat(flags.y || args[2] || seed.position.y),
      z: parseFloat(flags.z || args[3] || seed.position.z)
    };
    
    const oldPosition = { ...seed.position };
    this.system.moveSeed(seedId, position);
    
    const output = `
✓ Seed moved successfully!

  ID:           ${seedId}
  From:         (${oldPosition.x}, ${oldPosition.y}, ${oldPosition.z})
  To:           (${position.x}, ${position.y}, ${position.z})
  Distance:     ${this.calculateDistance(oldPosition, position).toFixed(2)}
    `.trim();
    
    return {
      success: true,
      output,
      data: { oldPosition, newPosition: position }
    };
  }
  
  usage(): string {
    return `
Usage: move <seed-id> [x] [y] [z] [options]

Move a seed to a new position in 3D space.

Arguments:
  seed-id       ID of the seed to move
  x             Target X coordinate
  y             Target Y coordinate
  z             Target Z coordinate

Options:
  --x           Target X coordinate (alternative)
  --y           Target Y coordinate (alternative)
  --z           Target Z coordinate (alternative)
  --relative    Move relative to current position

Examples:
  move seed_123 10 5 0
  move seed_123 --x=10 --y=5 --z=0
  move seed_123 --x=5 --relative
    `;
  }
  
  private calculateDistance(a: Vector3D, b: Vector3D): number {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dz = b.z - a.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
}
```

### 列出種子命令

```typescript
// list-seeds-command.ts
export class ListSeedsCommand extends Command {
  name = 'list';
  description = 'List all seeds in the system';
  aliases = ['ls'];
  
  private system: TerminalSeedSystem;
  
  constructor(system: TerminalSeedSystem) {
    super();
    this.system = system;
  }
  
  async execute(args: string[], flags: Record<string, any>): Promise<CommandResult> {
    const filter: SeedFilter = {
      type: flags.type as SeedType,
      state: flags.state as SeedState,
      minHealth: flags['min-health'] ? parseFloat(flags['min-health']) : undefined
    };
    
    const seeds = this.system.listSeeds(filter);
    
    const output = this.formatList(seeds, flags);
    
    return {
      success: true,
      output,
      data: seeds
    };
  }
  
  usage(): string {
    return `
Usage: list [options]

List all seeds in the system with optional filtering.

Options:
  --type, -t        Filter by seed type
  --state, -s       Filter by seed state
  --min-health      Filter by minimum health
  --format, -f      Output format (table|json|tree)
  --sort            Sort by (id|type|health|energy)

Examples:
  list
  list --type=neural
  list --state=mature --min-health=80
  list --format=json
  list --sort=health
    `;
  }
  
  private formatList(seeds: Seed3D[], flags: Record<string, any>): string {
    if (seeds.length === 0) {
      return 'No seeds found.';
    }
    
    const format = flags.format || 'table';
    
    switch (format) {
      case 'json':
        return JSON.stringify(seeds, null, 2);
      case 'tree':
        return this.formatTree(seeds);
      case 'table':
      default:
        return this.formatTable(seeds);
    }
  }
  
  private formatTable(seeds: Seed3D[]): string {
    const headers = ['ID', 'Type', 'Name', 'Position', 'State', 'Health', 'Energy'];
    const rows = seeds.map(seed => [
      seed.id.substring(0, 12) + '...',
      seed.type,
      seed.name.substring(0, 20),
      `(${seed.position.x.toFixed(1)}, ${seed.position.y.toFixed(1)}, ${seed.position.z.toFixed(1)})`,
      seed.state,
      `${seed.health}%`,
      `${seed.energy}%`
    ]);
    
    return this.createTable(headers, rows);
  }
  
  private formatTree(seeds: Seed3D[]): string {
    // 構建樹狀結構
    const roots = seeds.filter(s => s.type === SeedType.ROOT);
    let output = '';
    
    for (const root of roots) {
      output += this.formatTreeNode(root, seeds, 0);
    }
    
    return output;
  }
  
  private formatTreeNode(seed: Seed3D, allSeeds: Seed3D[], depth: number): string {
    const indent = '  '.repeat(depth);
    const icon = this.getSeedIcon(seed.type);
    let output = `${indent}${icon} ${seed.name} [${seed.id.substring(0, 8)}] (${seed.state})\n`;
    
    // 找到子節點
    const children = allSeeds.filter(s => 
      s.connections.some(c => c.targetId === seed.id && c.type === ConnectionType.PARENT_CHILD)
    );
    
    for (const child of children) {
      output += this.formatTreeNode(child, allSeeds, depth + 1);
    }
    
    return output;
  }
  
  private getSeedIcon(type: SeedType): string {
    const icons = {
      [SeedType.ROOT]: '🌱',
      [SeedType.BRANCH]: '🌿',
      [SeedType.LEAF]: '🍃',
      [SeedType.FRUIT]: '🍎',
      [SeedType.FLOWER]: '🌸',
      [SeedType.NEURAL]: '🧠',
      [SeedType.PARTICLE]: '⚛️'
    };
    return icons[type] || '•';
  }
  
  private createTable(headers: string[], rows: string[][]): string {
    // 計算列寬
    const colWidths = headers.map((header, i) => {
      const maxRowWidth = Math.max(...rows.map(row => row[i].length));
      return Math.max(header.length, maxRowWidth);
    });
    
    // 創建表格
    const separator = '─';
    const divider = '┼';
    
    let table = '';
    
    // 標題行
    table += '┌' + colWidths.map(w => separator.repeat(w + 2)).join(divider) + '┐\n';
    table += '│ ' + headers.map((h, i) => h.padEnd(colWidths[i])).join(' │ ') + ' │\n';
    table += '├' + colWidths.map(w => separator.repeat(w + 2)).join(divider) + '┤\n';
    
    // 數據行
    for (const row of rows) {
      table += '│ ' + row.map((cell, i) => cell.padEnd(colWidths[i])).join(' │ ') + ' │\n';
    }
    
    table += '└' + colWidths.map(w => separator.repeat(w + 2)).join(divider) + '┘\n';
    
    return table;
  }
}
```

---

## 3D種子可視化

### ASCII藝術渲染器

```typescript
// ascii-renderer.ts
export class ASCIIRenderer {
  private width: number;
  private height: number;
  private depth: number;
  
  constructor(width: number = 80, height: number = 40, depth: number = 20) {
    this.width = width;
    this.height = height;
    this.depth = depth;
  }
  
  render3DSpace(seeds: Seed3D[]): string {
    // 創建3D緩衝區
    const buffer = this.createBuffer();
    
    // 渲染每個種子
    for (const seed of seeds) {
      this.renderSeed(buffer, seed);
    }
    
    // 渲染連接
    for (const seed of seeds) {
      this.renderConnections(buffer, seed, seeds);
    }
    
    // 轉換為字符串
    return this.bufferToString(buffer);
  }
  
  private createBuffer(): string[][][] {
    const buffer: string[][][] = [];
    for (let z = 0; z < this.depth; z++) {
      buffer[z] = [];
      for (let y = 0; y < this.height; y++) {
        buffer[z][y] = [];
        for (let x = 0; x < this.width; x++) {
          buffer[z][y][x] = ' ';
        }
      }
    }
    return buffer;
  }
  
  private renderSeed(buffer: string[][][], seed: Seed3D): void {
    // 將世界座標轉換為屏幕座標
    const screenPos = this.worldToScreen(seed.position);
    
    if (this.isInBounds(screenPos)) {
      const char = this.getSeedChar(seed);
      buffer[screenPos.z][screenPos.y][screenPos.x] = char;
      
      // 渲染種子周圍的光暈
      this.renderAura(buffer, screenPos, seed);
    }
  }
  
  private renderConnections(buffer: string[][][], seed: Seed3D, allSeeds: Seed3D[]): void {
    for (const connection of seed.connections) {
      const target = allSeeds.find(s => s.id === connection.targetId);
      if (target) {
        this.drawLine(buffer, seed.position, target.position, connection.type);
      }
    }
  }
  
  private drawLine(
    buffer: string[][][],
    from: Vector3D,
    to: Vector3D,
    type: ConnectionType
  ): void {
    const fromScreen = this.worldToScreen(from);
    const toScreen = this.worldToScreen(to);
    
    // 簡單的3D線條繪製
    const steps = 20;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const x = Math.round(fromScreen.x + (toScreen.x - fromScreen.x) * t);
      const y = Math.round(fromScreen.y + (toScreen.y - fromScreen.y) * t);
      const z = Math.round(fromScreen.z + (toScreen.z - fromScreen.z) * t);
      
      if (this.isInBounds({ x, y, z })) {
        buffer[z][y][x] = this.getConnectionChar(type);
      }
    }
  }
  
  private renderAura(buffer: string[][][], pos: Vector3D, seed: Seed3D): void {
    const auraSize = 2;
    const auraChar = this.getAuraChar(seed.state);
    
    for (let dz = -1; dz <= 1; dz++) {
      for (let dy = -auraSize; dy <= auraSize; dy++) {
        for (let dx = -auraSize; dx <= auraSize; dx++) {
          const newPos = {
            x: pos.x + dx,
            y: pos.y + dy,
            z: pos.z + dz
          };
          
          if (this.isInBounds(newPos) && buffer[newPos.z][newPos.y][newPos.x] === ' ') {
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (dist <= auraSize) {
              buffer[newPos.z][newPos.y][newPos.x] = auraChar;
            }
          }
        }
      }
    }
  }
  
  private worldToScreen(pos: Vector3D): Vector3D {
    return {
      x: Math.round((pos.x + 50) / 100 * this.width),
      y: Math.round((pos.y + 50) / 100 * this.height),
      z: Math.round((pos.z + 50) / 100 * this.depth)
    };
  }
  
  private isInBounds(pos: Vector3D): boolean {
    return pos.x >= 0 && pos.x < this.width &&
           pos.y >= 0 && pos.y < this.height &&
           pos.z >= 0 && pos.z < this.depth;
  }
  
  private getSeedChar(seed: Seed3D): string {
    const chars: Record<SeedType, string> = {
      [SeedType.ROOT]: '●',
      [SeedType.BRANCH]: '◆',
      [SeedType.LEAF]: '○',
      [SeedType.FRUIT]: '◉',
      [SeedType.FLOWER]: '✿',
      [SeedType.NEURAL]: '◎',
      [SeedType.PARTICLE]: '•'
    };
    return chars[seed.type] || '■';
  }
  
  private getConnectionChar(type: ConnectionType): string {
    const chars: Record<ConnectionType, string> = {
      [ConnectionType.PARENT_CHILD]: '│',
      [ConnectionType.SIBLING]: '─',
      [ConnectionType.NEURAL]: '═',
      [ConnectionType.DATA_FLOW]: '→',
      [ConnectionType.ENERGY]: '⟿',
      [ConnectionType.SIGNAL]: '~'
    };
    return chars[type] || '·';
  }
  
  private getAuraChar(state: SeedState): string {
    const chars: Record<SeedState, string> = {
      [SeedState.DORMANT]: '.',
      [SeedState.GERMINATING]: ':',
      [SeedState.GROWING]: '░',
      [SeedState.MATURE]: '▒',
      [SeedState.FLOWERING]: '▓',
      [SeedState.FRUITING]: '█',
      [SeedState.DECAYING]: '▓',
      [SeedState.DEAD]: ' '
    };
    return chars[state] || ' ';
  }
  
  private bufferToString(buffer: string[][][]): string {
    let output = '';
    
    // 渲染每一層深度
    for (let z = 0; z < this.depth; z++) {
      output += `\n──── Layer ${z} (Depth: ${z * 5}) ────\n`;
      
      for (let y = 0; y < this.height; y++) {
        output += buffer[z][y].join('') + '\n';
      }
    }
    
    return output;
  }
}
```

### 可視化命令

```typescript
// visualize-command.ts
export class VisualizeSeedCommand extends Command {
  name = 'visualize';
  description = 'Visualize seeds in 3D ASCII art';
  aliases = ['viz', 'show', 'render'];
  
  private system: TerminalSeedSystem;
  private renderer: ASCIIRenderer;
  
  constructor(system: TerminalSeedSystem) {
    super();
    this.system = system;
    this.renderer = new ASCIIRenderer();
  }
  
  async execute(args: string[], flags: Record<string, any>): Promise<CommandResult> {
    const filter: SeedFilter = {
      type: flags.type as SeedType
    };
    
    const seeds = this.system.listSeeds(filter);
    
    const output = this.renderer.render3DSpace(seeds);
    
    return {
      success: true,
      output,
      data: { seedCount: seeds.length }
    };
  }
  
  usage(): string {
    return `
Usage: visualize [options]

Render a 3D ASCII visualization of the seed space.

Options:
  --type, -t    Filter by seed type
  --layer, -l   Show specific depth layer
  --animated    Enable animation (experimental)

Examples:
  visualize
  visualize --type=neural
  visualize --layer=5
    `;
  }
}
```

---

## 種子生命週期管理

### 生命週期引擎

```typescript
// lifecycle-engine.ts
export class SeedLifecycleEngine {
  private seeds: Map<string, Seed3D>;
  private updateInterval: number = 1000; // 1秒
  private running: boolean = false;
  
  constructor(seeds: Map<string, Seed3D>) {
    this.seeds = seeds;
  }
  
  start(): void {
    if (this.running) return;
    
    this.running = true;
    this.runLoop();
  }
  
  stop(): void {
    this.running = false;
  }
  
  private async runLoop(): Promise<void> {
    while (this.running) {
      await this.tick();
      await this.sleep(this.updateInterval);
    }
  }
  
  private async tick(): Promise<void> {
    const now = Date.now();
    
    for (const seed of this.seeds.values()) {
      this.updateSeed(seed, now);
    }
  }
  
  private updateSeed(seed: Seed3D, now: number): void {
    // 更新年齡
    seed.lifecycle.age = now - seed.lifecycle.createdAt;
    
    // 狀態轉換
    this.updateState(seed);
    
    // 更新健康和能量
    this.updateVitals(seed);
    
    // 執行行為
    this.executeBehaviors(seed);
    
    seed.lifecycle.updatedAt = now;
  }
  
  private updateState(seed: Seed3D): void {
    const age = seed.lifecycle.age;
    
    switch (seed.state) {
      case SeedState.DORMANT:
        if (age > 1000) {
          seed.state = SeedState.GERMINATING;
        }
        break;
        
      case SeedState.GERMINATING:
        if (age > 5000 && seed.health > 50) {
          seed.state = SeedState.GROWING;
        }
        break;
        
      case SeedState.GROWING:
        if (age > 20000 && seed.health > 80) {
          seed.state = SeedState.MATURE;
        }
        break;
        
      case SeedState.MATURE:
        if (seed.type === SeedType.FLOWER && age > 30000) {
          seed.state = SeedState.FLOWERING;
        } else if (seed.type === SeedType.FRUIT && age > 30000) {
          seed.state = SeedState.FRUITING;
        }
        break;
        
      case SeedState.FLOWERING:
      case SeedState.FRUITING:
        if (age > 60000 || seed.health < 30) {
          seed.state = SeedState.DECAYING;
        }
        break;
        
      case SeedState.DECAYING:
        if (seed.health <= 0) {
          seed.state = SeedState.DEAD;
        }
        break;
    }
  }
  
  private updateVitals(seed: Seed3D): void {
    // 能量自然消耗
    seed.energy -= 0.1;
    
    // 健康隨狀態變化
    switch (seed.state) {
      case SeedState.GROWING:
        seed.health += 0.5;
        break;
      case SeedState.MATURE:
        seed.health += 0.1;
        break;
      case SeedState.DECAYING:
        seed.health -= 1.0;
        break;
      case SeedState.DEAD:
        seed.health = 0;
        seed.energy = 0;
        break;
    }
    
    // 限制範圍
    seed.health = Math.max(0, Math.min(100, seed.health));
    seed.energy = Math.max(0, Math.min(100, seed.energy));
  }
  
  private executeBehaviors(seed: Seed3D): void {
    for (const behavior of seed.behaviors) {
      try {
        behavior.execute(seed);
      } catch (error) {
        console.error(`Behavior error for seed ${seed.id}:`, error);
      }
    }
  }
  
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

---

## 終端命令參考

### 完整命令列表

```
種子管理命令:
  create, new, spawn       創建新種子
  delete, rm, remove       刪除種子
  list, ls                 列出所有種子
  inspect, info, describe  檢查種子詳情
  
空間操作命令:
  move, mv, relocate       移動種子位置
  rotate                   旋轉種子
  scale                    縮放種子
  
連接命令:
  connect, link            連接兩個種子
  disconnect, unlink       斷開連接
  connections, links       列出連接
  
狀態命令:
  evolve, grow             演化種子狀態
  feed, energize           補充能量
  heal                     恢復健康
  
可視化命令:
  visualize, viz, show     3D可視化
  render                   渲染ASCII藝術
  graph                    顯示連接圖
  
系統命令:
  help, -h, --help         顯示幫助
  version, -v              顯示版本
  clear, cls               清屏
  history                  命令歷史
  export                   導出種子數據
  import                   導入種子數據
```

### 命令使用範例

```bash
# 創建種子
$ create root "Main Seed" --x=0 --y=0 --z=0 --color=green
✓ Seed created: seed_1234567890

# 創建神經種子
$ create neural "AI Core" --x=10 --y=10 --z=5 --shape=cube

# 列出所有種子
$ list
┌──────────────┬────────┬─────────────┬────────────────┬────────┬────────┬────────┐
│ ID           │ Type   │ Name        │ Position       │ State  │ Health │ Energy │
├──────────────┼────────┼─────────────┼────────────────┼────────┼────────┼────────┤
│ seed_123...  │ root   │ Main Seed   │ (0.0, 0.0, 0.0)│ mature │ 95%    │ 87%    │
│ seed_456...  │ neural │ AI Core     │ (10, 10, 5)    │ growing│ 78%    │ 92%    │
└──────────────┴────────┴─────────────┴────────────────┴────────┴────────┴────────┘

# 移動種子
$ move seed_123 20 15 10
✓ Seed moved from (0, 0, 0) to (20, 15, 10)

# 連接種子
$ connect seed_123 seed_456 --type=neural --strength=0.8
✓ Seeds connected successfully

# 檢查種子
$ inspect seed_123
Seed Details:
─────────────
  ID:          seed_1234567890
  Type:        root
  Name:        Main Seed
  Position:    (20.0, 15.0, 10.0)
  Rotation:    (0.0, 0.0, 0.0, 1.0)
  Scale:       (1.0, 1.0, 1.0)
  
  State:       mature
  Health:      95%
  Energy:      87%
  Age:         1h 23m 45s
  
  Connections: 1
    → seed_456 (neural, strength: 0.8)
  
  Layers:
    Core:      Active, Memory: 45%, CPU: 23%
    Logic:     3 rules, 2 triggers, 5 actions
    Display:   green sphere, idle animation

# 可視化空間
$ visualize --type=neural

──── Layer 0 (Depth: 0) ────
                                                                                
                                    ░░░░░                                       
                                  ░░◎◎◎░░                                     
                                    ░░░░░                                       
                                                                                

# 演化種子
$ evolve seed_123
✓ Seed evolved to next stage: flowering

# 導出數據
$ export --format=json --output=seeds.json
✓ Exported 2 seeds to seeds.json
```

---

## 實現範例

### 完整工作流範例

```typescript
// complete-workflow-example.ts
import { TerminalSeedSystem } from './terminal-system';
import { SeedLifecycleEngine } from './lifecycle-engine';

async function demonstrateTerminalSeedSystem() {
  // 1. 初始化系統
  console.log('=== Initializing Terminal Seed System ===\n');
  const system = new TerminalSeedSystem();
  
  // 2. 創建根種子
  console.log('Creating root seed...');
  await system.executeCommand('create root "Genesis" --x=0 --y=0 --z=0 --color=gold');
  
  // 3. 創建分支種子
  console.log('\nCreating branch seeds...');
  await system.executeCommand('create branch "Left Branch" --x=-10 --y=5 --z=0');
  await system.executeCommand('create branch "Right Branch" --x=10 --y=5 --z=0');
  
  // 4. 創建神經種子
  console.log('\nCreating neural seeds...');
  await system.executeCommand('create neural "AI Processor" --x=0 --y=10 --z=5');
  
  // 5. 建立連接
  console.log('\nEstablishing connections...');
  const seeds = system.listSeeds();
  if (seeds.length >= 4) {
    await system.executeCommand(`connect ${seeds[0].id} ${seeds[1].id} --type=parent-child`);
    await system.executeCommand(`connect ${seeds[0].id} ${seeds[2].id} --type=parent-child`);
    await system.executeCommand(`connect ${seeds[3].id} ${seeds[0].id} --type=neural`);
  }
  
  // 6. 列出所有種子
  console.log('\n=== Seed Inventory ===');
  await system.executeCommand('list');
  
  // 7. 樹狀視圖
  console.log('\n=== Seed Tree ===');
  await system.executeCommand('list --format=tree');
  
  // 8. 3D可視化
  console.log('\n=== 3D Visualization ===');
  await system.executeCommand('visualize');
  
  // 9. 檢查特定種子
  if (seeds.length > 0) {
    console.log('\n=== Seed Details ===');
    await system.executeCommand(`inspect ${seeds[0].id}`);
  }
  
  // 10. 啟動生命週期引擎
  console.log('\n=== Starting Lifecycle Engine ===');
  const lifecycleEngine = new SeedLifecycleEngine(system['seeds']);
  lifecycleEngine.start();
  
  // 11. 模擬一段時間
  console.log('Simulating 10 seconds of growth...');
  await new Promise(resolve => setTimeout(resolve, 10000));
  
  // 12. 查看演化後的狀態
  console.log('\n=== After Evolution ===');
  await system.executeCommand('list');
  
  // 13. 移動種子
  console.log('\n=== Moving Seeds ===');
  if (seeds.length > 0) {
    await system.executeCommand(`move ${seeds[0].id} 5 5 5`);
  }
  
  // 14. 最終可視化
  console.log('\n=== Final Visualization ===');
  await system.executeCommand('visualize');
  
  // 15. 導出數據
  console.log('\n=== Exporting Data ===');
  await system.executeCommand('export --format=json --output=terminal-seeds.json');
  
  // 16. 停止生命週期引擎
  lifecycleEngine.stop();
  
  console.log('\n=== Demonstration Complete ===');
}

// 執行演示
demonstrateTerminalSeedSystem().catch(console.error);
```

---

## 進階特性

### 種子腳本語言

```typescript
// seed-script-language.ts
export class SeedScriptInterpreter {
  private system: TerminalSeedSystem;
  
  constructor(system: TerminalSeedSystem) {
    this.system = system;
  }
  
  async executeScript(script: string): Promise<void> {
    const lines = script.split('\n').filter(line => {
      const trimmed = line.trim();
      return trimmed && !trimmed.startsWith('#');
    });
    
    for (const line of lines) {
      await this.system.executeCommand(line);
    }
  }
}

// 腳本範例
const sampleScript = `
# 種子花園腳本

# 創建根系統
create root "Garden Root" --x=0 --y=0 --z=0

# 創建主幹
create branch "Main Trunk" --x=0 --y=5 --z=0
connect seed_root seed_trunk --type=parent-child

# 創建分支網絡
create branch "Branch 1" --x=-5 --y=10 --z=0
create branch "Branch 2" --x=5 --y=10 --z=0
create branch "Branch 3" --x=0 --y=10 --z=5
connect seed_trunk seed_branch1 --type=parent-child
connect seed_trunk seed_branch2 --type=parent-child
connect seed_trunk seed_branch3 --type=parent-child

# 創建葉子
create leaf "Leaf 1" --x=-7 --y=12 --z=0
create leaf "Leaf 2" --x=7 --y=12 --z=0
connect seed_branch1 seed_leaf1 --type=parent-child
connect seed_branch2 seed_leaf2 --type=parent-child

# 可視化結果
visualize
list --format=tree
`;
```

### 批次操作

```typescript
// batch-operations.ts
export class SeedBatchOperator {
  private system: TerminalSeedSystem;
  
  constructor(system: TerminalSeedSystem) {
    this.system = system;
  }
  
  async createGrid(
    type: SeedType,
    rows: number,
    cols: number,
    spacing: number
  ): Promise<Seed3D[]> {
    const seeds: Seed3D[] = [];
    
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const seed = this.system.createSeed({
          type,
          name: `Grid_${x}_${y}`,
          position: {
            x: x * spacing,
            y: y * spacing,
            z: 0
          }
        });
        seeds.push(seed);
      }
    }
    
    return seeds;
  }
  
  async connectNeighbors(seeds: Seed3D[], maxDistance: number): Promise<void> {
    for (let i = 0; i < seeds.length; i++) {
      for (let j = i + 1; j < seeds.length; j++) {
        const dist = this.distance(seeds[i].position, seeds[j].position);
        
        if (dist <= maxDistance) {
          this.system.connectSeeds(
            seeds[i].id,
            seeds[j].id,
            ConnectionType.SIBLING
          );
        }
      }
    }
  }
  
  private distance(a: Vector3D, b: Vector3D): number {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dz = b.z - a.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
}
```

---

**怎麼過去，就怎麼回來**

*Last Updated: 2026-01-26T12:00:00Z*
