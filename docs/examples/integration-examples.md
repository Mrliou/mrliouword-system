---
title: "整合示例"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: [examples, integration, tutorial, code-samples]
---

# 整合示例

<!-- origin_signature: MrLiouWord -->

## 目錄

- [完整系統整合](#完整系統整合)
- [Cloudflare Workers 整合](#cloudflare-workers-整合)
- [本地開發整合](#本地開發整合)
- [WebGPU 整合示例](#webgpu-整合示例)
- [地理記憶整合](#地理記憶整合)
- [多人協作整合](#多人協作整合)

## 完整系統整合

### 示例 1：完整的 MrLiouWord 系統

這個示例展示如何整合所有核心組件：

```python
# origin_signature: MrLiouWord

from flowagent import FlowAgent
from memory_vault import MemoryVault
from particle_globe import ParticleGlobe
from fpp_compiler import FppCompiler
from persona_manager import PersonaManager

class MrLiouWordSystem:
    """
    完整的 MrLiouWord 系統整合
    
    整合所有核心組件，提供統一的 API
    """
    
    def __init__(self, config: dict = None):
        """
        初始化系統
        
        Args:
            config: 配置字典
        """
        self.signature = "MrLiouWord"
        self.config = config or self._default_config()
        
        # 初始化所有組件
        self.agent = FlowAgent(origin_signature=self.signature)
        self.memory = MemoryVault(origin_signature=self.signature)
        self.globe = ParticleGlobe()
        self.compiler = FppCompiler()
        self.persona = PersonaManager()
        
        print(f"✓ MrLiouWord System initialized (signature: {self.signature})")
    
    def _default_config(self) -> dict:
        """默認配置"""
        return {
            "origin_signature": "MrLiouWord",
            "mode": "integrated",
            "layers": {
                "l0_enabled": True,
                "l1_enabled": True,
                "l2_enabled": True,
                "l3_enabled": True,
                "l4_enabled": True,
                "l5_enabled": True,
                "l6_enabled": True,
                "l7_enabled": True
            },
            "features": {
                "memory_enabled": True,
                "globe_enabled": True,
                "compiler_enabled": True,
                "persona_enabled": True
            }
        }
    
    def process_message(
        self,
        message: str,
        user_id: str = None,
        location: dict = None,
        persona: str = "DEFAULT"
    ) -> dict:
        """
        處理消息的完整流程
        
        這個方法展示了如何整合所有組件處理一條消息：
        1. 創建粒子 (L1)
        2. 編譯處理 (L2-L3)
        3. 人格處理 (L5)
        4. 存儲記憶 (L7)
        5. 地理綁定（可選）
        
        Args:
            message: 用戶消息
            user_id: 用戶 ID
            location: 地理位置 {lat, lng}
            persona: 使用的人格
            
        Returns:
            處理結果
        """
        print(f"\n{'='*60}")
        print(f"Processing message: {message[:50]}...")
        print(f"{'='*60}")
        
        # Step 1: 創建粒子 (L1)
        print("\n[L1] Creating particle...")
        particle = self.agent.create_particle({
            "content": message,
            "user_id": user_id,
            "timestamp": time.time(),
            "signature": self.signature
        })
        print(f"  ✓ Particle created: {particle['id']}")
        
        # Step 2: 編譯處理 (L2-L3)
        if self.config["features"]["compiler_enabled"]:
            print("\n[L2-L3] Compiling particle...")
            compiled = self.compiler.compile(particle)
            print(f"  ✓ Compiled to layer: {compiled['layer']}")
        else:
            compiled = particle
        
        # Step 3: 人格處理 (L5)
        print(f"\n[L5] Processing with persona: {persona}...")
        response = self.agent.process_with_persona(compiled, persona=persona)
        print(f"  ✓ Response generated")
        
        # Step 4: 存儲記憶 (L7)
        if self.config["features"]["memory_enabled"]:
            print("\n[L7] Storing memory...")
            memory_id = self.memory.store(
                layer=7,
                particle_id=response["id"],
                data={
                    "user_message": message,
                    "bot_response": response["content"],
                    "persona": persona,
                    "timestamp": time.time(),
                    "signature": self.signature
                }
            )
            print(f"  ✓ Memory stored: {memory_id}")
        
        # Step 5: 地理綁定（可選）
        if location and self.config["features"]["globe_enabled"]:
            print("\n[Globe] Binding to location...")
            self.globe.bind_particle(
                particle_id=response["id"],
                latitude=location["lat"],
                longitude=location["lng"],
                data={"message": message}
            )
            print(f"  ✓ Bound to ({location['lat']}, {location['lng']})")
        
        print(f"\n{'='*60}")
        print("✓ Processing complete!")
        print(f"{'='*60}\n")
        
        return {
            "particle_id": particle["id"],
            "response": response["content"],
            "persona": persona,
            "memory_id": memory_id if self.config["features"]["memory_enabled"] else None,
            "location": location,
            "signature": self.signature
        }
    
    def query_memories(
        self,
        query: str,
        threshold: float = 0.8,
        limit: int = 10
    ) -> list:
        """語意查詢記憶"""
        return self.memory.query_semantic(
            query=query,
            threshold=threshold
        )[:limit]
    
    def export_journey(
        self,
        start_date: str,
        end_date: str,
        filename: str
    ):
        """導出地理旅程"""
        memories = self.memory.query_by_timerange(
            start=start_date,
            end=end_date,
            layer=7
        )
        
        self.globe.export_to_kml(memories, filename)
        print(f"✓ Journey exported to {filename}")

# 使用示例
if __name__ == "__main__":
    import time
    
    # 初始化系統
    system = MrLiouWordSystem()
    
    # 處理帶位置的消息
    result1 = system.process_message(
        message="今天在台北101見到了老朋友",
        user_id="user_001",
        location={"lat": 25.0340, "lng": 121.5645},
        persona="ANALYST_BG"
    )
    
    print(f"Response: {result1['response']}")
    
    # 處理普通消息
    result2 = system.process_message(
        message="記得我們上次的對話嗎？",
        user_id="user_001",
        persona="ANALYST_BG"
    )
    
    print(f"Response: {result2['response']}")
    
    # 查詢記憶
    memories = system.query_memories("台北", threshold=0.8)
    print(f"\nFound {len(memories)} memories about 台北")
    
    # 導出旅程
    system.export_journey("2026-01-01", "2026-01-31", "january_journey.kml")
```

## Cloudflare Workers 整合

### 示例 2：部署到 Cloudflare Workers

```typescript
// origin_signature: MrLiouWord

/**
 * Cloudflare Workers 整合示例
 * 
 * 在 Cloudflare Workers 上運行 MrLiouWord 系統
 */

interface Env {
  // KV 命名空間
  PARTICLE_AUTH_VAULT: KVNamespace;
  
  // R2 存儲
  MRLIOUBOOK: R2Bucket;
  
  // 環境變量
  ENCRYPTION_KEY: string;
}

// 全局簽名
const ORIGIN_SIGNATURE = "MrLiouWord";

/**
 * 粒子處理 Worker
 */
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    
    // CORS 頭
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "X-Origin-Signature": ORIGIN_SIGNATURE
    };
    
    // 處理 OPTIONS 請求
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    
    const url = new URL(request.url);
    
    // 路由處理
    switch (url.pathname) {
      case "/api/particle/create":
        return handleCreateParticle(request, env, corsHeaders);
      
      case "/api/particle/query":
        return handleQueryParticle(request, env, corsHeaders);
      
      case "/api/memory/store":
        return handleStoreMemory(request, env, corsHeaders);
      
      case "/api/memory/retrieve":
        return handleRetrieveMemory(request, env, corsHeaders);
      
      default:
        return new Response("Not Found", { 
          status: 404,
          headers: corsHeaders
        });
    }
  }
};

/**
 * 創建粒子
 */
async function handleCreateParticle(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  
  const data = await request.json() as {
    content: string;
    user_id?: string;
  };
  
  // 創建粒子
  const particle = {
    id: `P_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    content: data.content,
    user_id: data.user_id,
    timestamp: Date.now(),
    layer: 1,
    origin_signature: ORIGIN_SIGNATURE
  };
  
  // 存儲到 KV
  await env.PARTICLE_AUTH_VAULT.put(
    particle.id,
    JSON.stringify(particle),
    {
      expirationTtl: 86400 * 30  // 30 天
    }
  );
  
  return new Response(
    JSON.stringify({
      status: "success",
      particle,
      origin_signature: ORIGIN_SIGNATURE
    }),
    {
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json"
      }
    }
  );
}

/**
 * 查詢粒子
 */
async function handleQueryParticle(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  
  const url = new URL(request.url);
  const particleId = url.searchParams.get("id");
  
  if (!particleId) {
    return new Response(
      JSON.stringify({ error: "Missing particle ID" }),
      {
        status: 400,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  
  // 從 KV 檢索
  const particleData = await env.PARTICLE_AUTH_VAULT.get(particleId);
  
  if (!particleData) {
    return new Response(
      JSON.stringify({ error: "Particle not found" }),
      {
        status: 404,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  
  const particle = JSON.parse(particleData);
  
  return new Response(
    JSON.stringify({
      status: "success",
      particle,
      origin_signature: ORIGIN_SIGNATURE
    }),
    {
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json"
      }
    }
  );
}

/**
 * 存儲記憶到 R2
 */
async function handleStoreMemory(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  
  const data = await request.json() as {
    particle_id: string;
    content: any;
  };
  
  const memoryKey = `L7/memory_${data.particle_id}.json`;
  const memoryData = {
    ...data,
    stored_at: new Date().toISOString(),
    origin_signature: ORIGIN_SIGNATURE
  };
  
  // 存儲到 R2
  await env.MRLIOUBOOK.put(
    memoryKey,
    JSON.stringify(memoryData),
    {
      httpMetadata: {
        contentType: "application/json"
      }
    }
  );
  
  return new Response(
    JSON.stringify({
      status: "success",
      memory_key: memoryKey,
      origin_signature: ORIGIN_SIGNATURE
    }),
    {
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json"
      }
    }
  );
}

/**
 * 從 R2 檢索記憶
 */
async function handleRetrieveMemory(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  
  const url = new URL(request.url);
  const particleId = url.searchParams.get("particle_id");
  
  if (!particleId) {
    return new Response(
      JSON.stringify({ error: "Missing particle_id" }),
      {
        status: 400,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  
  const memoryKey = `L7/memory_${particleId}.json`;
  
  // 從 R2 檢索
  const object = await env.MRLIOUBOOK.get(memoryKey);
  
  if (!object) {
    return new Response(
      JSON.stringify({ error: "Memory not found" }),
      {
        status: 404,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  
  const memoryData = await object.json();
  
  return new Response(
    JSON.stringify({
      status: "success",
      memory: memoryData,
      origin_signature: ORIGIN_SIGNATURE
    }),
    {
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json"
      }
    }
  );
}
```

### 部署配置

```toml
# origin_signature: MrLiouWord
# wrangler.toml

name = "mrliouword-particle-system"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[vars]
ORIGIN_SIGNATURE = "MrLiouWord"

[[kv_namespaces]]
binding = "PARTICLE_AUTH_VAULT"
id = "your-kv-namespace-id"

[[r2_buckets]]
binding = "MRLIOUBOOK"
bucket_name = "mrlioubook"

[build]
command = "npm run build"
```

## 本地開發整合

### 示例 3：本地開發環境設置

```bash
#!/bin/bash
# origin_signature: MrLiouWord
# setup_dev.sh - 設置本地開發環境

set -e

echo "Setting up MrLiouWord development environment..."

# 1. 創建項目目錄結構
mkdir -p mrliouword-dev/{src,tests,docs,data/{L1_Seed,L7_Memory}}
cd mrliouword-dev

# 2. 初始化 Python 虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 創建 requirements.txt
cat > requirements.txt << EOF
# origin_signature: MrLiouWord
flowagent>=1.0.0
memory-vault>=1.0.0
particle-globe>=1.0.0
fpp-compiler>=1.0.0
cryptography>=41.0.0
msgpack>=1.0.0
simhash>=2.1.0
EOF

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 創建配置文件
cat > config.json << EOF
{
  "origin_signature": "MrLiouWord",
  "mode": "development",
  "debug": true,
  "storage": {
    "type": "local",
    "path": "./data"
  },
  "layers": {
    "l1_path": "./data/L1_Seed",
    "l7_path": "./data/L7_Memory"
  }
}
EOF

# 6. 創建測試文件
cat > tests/test_integration.py << 'PYTHON'
# origin_signature: MrLiouWord

import unittest
from flowagent import FlowAgent
from memory_vault import MemoryVault

class TestIntegration(unittest.TestCase):
    """整合測試"""
    
    def setUp(self):
        self.agent = FlowAgent(origin_signature="MrLiouWord")
        self.memory = MemoryVault(origin_signature="MrLiouWord")
    
    def test_full_cycle(self):
        """測試完整循環"""
        # 創建粒子
        particle = self.agent.create_particle("test content")
        self.assertEqual(particle["signature"], "MrLiouWord")
        
        # 存儲到記憶
        self.memory.store(1, particle["id"], particle)
        
        # 檢索
        retrieved = self.memory.retrieve(1, particle["id"])
        self.assertEqual(retrieved["content"], "test content")

if __name__ == "__main__":
    unittest.main()
PYTHON

echo "✓ Development environment setup complete!"
echo "  Activate with: source venv/bin/activate"
echo "  Run tests with: python -m pytest tests/"
```

## WebGPU 整合示例

### 示例 4：WebGPU 粒子處理

```typescript
// origin_signature: MrLiouWord

/**
 * WebGPU 粒子處理整合
 */

interface Particle {
  id: string;
  content: number[];  // 向量化內容
  layer: number;
  timestamp: number;
  origin_signature: string;
}

class WebGPUParticleProcessor {
  private device: GPUDevice | null = null;
  private readonly ORIGIN_SIGNATURE = "MrLiouWord";
  
  /**
   * 初始化 WebGPU
   */
  async initialize(): Promise<void> {
    if (!navigator.gpu) {
      throw new Error("WebGPU not supported");
    }
    
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) {
      throw new Error("No GPU adapter found");
    }
    
    this.device = await adapter.requestDevice();
    console.log("✓ WebGPU initialized");
  }
  
  /**
   * 並行處理多個粒子
   */
  async processParticlesBatch(particles: Particle[]): Promise<Particle[]> {
    if (!this.device) {
      throw new Error("WebGPU not initialized");
    }
    
    // 創建計算著色器
    const shaderModule = this.device.createShaderModule({
      code: `
        // origin_signature: MrLiouWord
        
        struct Particle {
          content: array<f32, 128>,
          layer: u32,
          timestamp: f32
        }
        
        @group(0) @binding(0) var<storage, read_write> particles: array<Particle>;
        
        @compute @workgroup_size(64)
        fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
          let idx = global_id.x;
          if (idx >= arrayLength(&particles)) {
            return;
          }
          
          // 粒子處理邏輯 - 這裡做簡單的歸一化
          var particle = particles[idx];
          var sum: f32 = 0.0;
          
          for (var i: u32 = 0u; i < 128u; i = i + 1u) {
            sum = sum + particle.content[i] * particle.content[i];
          }
          
          let norm = sqrt(sum);
          if (norm > 0.0) {
            for (var i: u32 = 0u; i < 128u; i = i + 1u) {
              particle.content[i] = particle.content[i] / norm;
            }
          }
          
          particles[idx] = particle;
        }
      `
    });
    
    // 創建計算管線
    const pipeline = this.device.createComputePipeline({
      layout: "auto",
      compute: {
        module: shaderModule,
        entryPoint: "main"
      }
    });
    
    // 創建緩衝區並上傳數據
    const particleBuffer = this.createParticleBuffer(particles);
    
    // 創建綁定組
    const bindGroup = this.device.createBindGroup({
      layout: pipeline.getBindGroupLayout(0),
      entries: [{
        binding: 0,
        resource: { buffer: particleBuffer }
      }]
    });
    
    // 執行計算
    const commandEncoder = this.device.createCommandEncoder();
    const passEncoder = commandEncoder.beginComputePass();
    
    passEncoder.setPipeline(pipeline);
    passEncoder.setBindGroup(0, bindGroup);
    passEncoder.dispatchWorkgroups(Math.ceil(particles.length / 64));
    passEncoder.end();
    
    this.device.queue.submit([commandEncoder.finish()]);
    
    // 讀回結果
    await this.device.queue.onSubmittedWorkDone();
    const results = await this.readParticleBuffer(particleBuffer, particles.length);
    
    return results;
  }
  
  private createParticleBuffer(particles: Particle[]): GPUBuffer {
    // 實現細節...
    throw new Error("Not implemented");
  }
  
  private async readParticleBuffer(
    buffer: GPUBuffer,
    count: number
  ): Promise<Particle[]> {
    // 實現細節...
    throw new Error("Not implemented");
  }
}

// 使用示例
async function main() {
  const processor = new WebGPUParticleProcessor();
  await processor.initialize();
  
  const particles: Particle[] = [
    {
      id: "P_001",
      content: new Array(128).fill(0).map(() => Math.random()),
      layer: 1,
      timestamp: Date.now(),
      origin_signature: "MrLiouWord"
    }
    // ... 更多粒子
  ];
  
  const processed = await processor.processParticlesBatch(particles);
  console.log(`✓ Processed ${processed.length} particles with WebGPU`);
}
```

## 相關文檔

- [核心組件中心](../core/components.md)
- [用戶指南](../core/user-guide.md)
- [最佳實踐](../core/best-practices.md)
- [WebGPU 整合架構](../architecture/webgpu-integration.md)
- [Cloudflare 部署](../deployment/l-1-to-l1.md)

---

**怎麼過去，就怎麼回來**

_最後更新：2026-01-26 by MR.liou_
