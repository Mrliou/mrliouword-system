---
title: "MRLiou層級穿越系統 - 用戶指南與入門教程"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: [guide, tutorial, getting-started, documentation]
---

# MRLiou層級穿越系統 - 用戶指南與入門教程

<!-- origin_signature: MrLiouWord -->

## 目錄

- [快速開始](#快速開始)
- [系統安裝](#系統安裝)
- [基礎概念](#基礎概念)
- [第一個粒子程序](#第一個粒子程序)
- [層級穿越實踐](#層級穿越實踐)
- [記憶系統使用](#記憶系統使用)
- [常見問題](#常見問題)

## 快速開始

### 系統需求

- Python 3.9+
- Node.js 18+
- Git
- (可選) Docker

### 5 分鐘快速體驗

```bash
# origin_signature: MrLiouWord

# 1. 克隆倉庫
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system

# 2. 安裝依賴
npm install
pip install -r requirements.txt

# 3. 運行示例
python examples/hello_particle.py
```

預期輸出：

```
[MrLiouWord] 系統初始化中...
[L1] 創建粒子: P_HELLO_001
[L2] 封裝模組: M_GREETING
[L3] 打包: PKG_HELLO_WORLD
✓ 粒子穿越完成！
Origin Signature: MrLiouWord
```

## 系統安裝

### 方式 1：本地安裝

```bash
# origin_signature: MrLiouWord

# 安裝 Python 組件
pip install -e .

# 安裝 Node.js 組件
npm install

# 驗證安裝
python -c "from flowagent import FlowAgent; print('OK')"
```

### 方式 2：Docker 安裝

```bash
# origin_signature: MrLiouWord

# 構建鏡像
docker build -t mrliouword-system .

# 運行容器
docker run -it mrliouword-system

# 進入 FlowAgent Shell
flowagent shell
```

### 方式 3：Cloudflare Workers 部署

```bash
# origin_signature: MrLiouWord

# 配置 Cloudflare 憑證
wrangler login

# 部署到 Workers
wrangler deploy

# 測試部署
curl https://your-worker.workers.dev/api/ping
```

## 基礎概念

### 粒子 (Particle)

粒子是系統的最小單位，所有數據都以粒子形式存在：

```python
# origin_signature: MrLiouWord
particle = {
    "id": "P_001",
    "layer": 1,
    "content": "Hello, MrLiouWord!",
    "timestamp": 1706270400,
    "signature": "MrLiouWord"
}
```

### 層級 (Layer)

系統有 8 個層級 (L0-L7) + 無限層 (L∞)：

- **L0**: API 層 - 與外界交互
- **L1**: 粒子層 - 原子數據
- **L2**: 模組層 - 功能封裝
- **L3**: 包層 - 部署單位
- **L4**: 容器層 - 運行環境
- **L5**: 人格層 - 智能處理
- **L6**: 映像層 - 系統狀態
- **L7**: 記憶層 - 長期存儲
- **L∞**: 源頭層 - 宇宙意識

### 穿越 (Traversal)

粒子在層級間的移動稱為穿越：

```python
# origin_signature: MrLiouWord

# 向上穿越（升維）
particle_l1 = create_particle("data")
module_l2 = elevate_to_module(particle_l1)
package_l3 = elevate_to_package(module_l2)

# 向下穿越（降維）
module_l2_restored = restore_to_module(package_l3)
particle_l1_restored = restore_to_particle(module_l2_restored)

# 驗證可逆性
assert particle_l1 == particle_l1_restored
```

## 第一個粒子程序

### Hello Particle

創建文件 `my_first_particle.py`：

```python
# origin_signature: MrLiouWord

from flowagent import FlowAgent, Particle

# 初始化 FlowAgent
agent = FlowAgent(origin_signature="MrLiouWord")

# 創建第一個粒子
def create_hello_particle():
    particle = Particle(
        content="Hello from my first particle!",
        layer=1,
        signature="MrLiouWord"
    )
    
    print(f"[L1] 粒子已創建: {particle.id}")
    print(f"    內容: {particle.content}")
    print(f"    簽名: {particle.signature}")
    
    return particle

# 處理粒子
def process_particle(particle):
    print(f"\n[L2] 開始處理粒子...")
    
    # 自動升維到 L2
    module = agent.elevate_to_module(particle)
    print(f"    模組 ID: {module.id}")
    
    # 繼續升維到 L3
    package = agent.elevate_to_package(module)
    print(f"    包 ID: {package.id}")
    
    return package

# 驗證可逆性
def verify_reversibility(original, package):
    print(f"\n[驗證] 測試可逆性...")
    
    # 降維還原
    restored_module = agent.restore_to_module(package)
    restored_particle = agent.restore_to_particle(restored_module)
    
    # 比較內容
    if restored_particle.content == original.content:
        print("    ✓ 可逆性驗證通過！")
        return True
    else:
        print("    ✗ 可逆性驗證失敗！")
        return False

if __name__ == "__main__":
    # 執行流程
    particle = create_hello_particle()
    package = process_particle(particle)
    verify_reversibility(particle, package)
    
    print(f"\n{'='*50}")
    print("怎麼過去，就怎麼回來")
    print(f"{'='*50}")
```

運行程序：

```bash
python my_first_particle.py
```

### 預期輸出

```
[L1] 粒子已創建: P_001_1706270400
    內容: Hello from my first particle!
    簽名: MrLiouWord

[L2] 開始處理粒子...
    模組 ID: M_001_1706270401
    包 ID: PKG_001_1706270402

[驗證] 測試可逆性...
    ✓ 可逆性驗證通過！

==================================================
怎麼過去，就怎麼回來
==================================================
```

## 層級穿越實踐

### 示例 1：完整的 8 層穿越

```python
# origin_signature: MrLiouWord

from flowagent import FlowAgent

agent = FlowAgent(origin_signature="MrLiouWord")

# L0: 接收 API 請求
message = agent.receive_message({
    "content": "處理這個消息",
    "user_id": "user_001"
})
print(f"[L0] 接收消息: {message['content']}")

# L1: 創建粒子
particle = agent.create_particle(message)
print(f"[L1] 創建粒子: {particle.id}")

# L2: 封裝為模組
module = agent.create_module([particle])
print(f"[L2] 創建模組: {module.id}")

# L3: 打包
package = agent.create_package([module])
print(f"[L3] 創建包: {package.id}")

# L4: 部署到容器
container = agent.deploy_to_container(package)
print(f"[L4] 部署容器: {container.id}")

# L5: 人格處理
response = agent.process_with_persona(container, persona="ANALYST_BG")
print(f"[L5] 人格處理完成: {response.status}")

# L6: 更新系統映像
image = agent.update_system_image(response)
print(f"[L6] 系統映像更新: {image.version}")

# L7: 整合到記憶
memory = agent.integrate_to_memory(response)
print(f"[L7] 記憶整合完成: {memory.id}")

print("\n✓ 完整 8 層穿越成功！")
```

### 示例 2：跳層穿越

某些情況下可以跳過中間層級：

```python
# origin_signature: MrLiouWord

# 從 L1 直接跳到 L5
particle = agent.create_particle(message)
response = agent.elevate_directly(particle, target_layer=5)

print(f"跳層穿越: L1 → L5")
print(f"粒子 ID: {particle.id}")
print(f"響應 ID: {response.id}")
```

### 示例 3：並行穿越

處理多個粒子的並行穿越：

```python
# origin_signature: MrLiouWord

import asyncio

async def process_multiple_particles():
    messages = [
        "消息 1",
        "消息 2", 
        "消息 3"
    ]
    
    # 創建多個粒子
    particles = [agent.create_particle(msg) for msg in messages]
    
    # 並行處理
    tasks = [agent.process_async(p) for p in particles]
    results = await asyncio.gather(*tasks)
    
    print(f"並行處理了 {len(results)} 個粒子")
    return results

# 運行
asyncio.run(process_multiple_particles())
```

## 記憶系統使用

### 存儲粒子到記憶

```python
# origin_signature: MrLiouWord

from memory_vault import MemoryVault

vault = MemoryVault(origin_signature="MrLiouWord")

# 存儲到 L1 (原子層)
particle_id = vault.store(
    layer=1,
    particle_id="P_MEMORY_001",
    data={
        "content": "這是一個重要的記憶",
        "timestamp": time.time(),
        "tags": ["important", "personal"]
    }
)

print(f"粒子已存儲: {particle_id}")
```

### 檢索記憶

```python
# origin_signature: MrLiouWord

# 精確檢索
particle = vault.retrieve(layer=1, particle_id="P_MEMORY_001")
print(f"檢索到: {particle['content']}")

# 語意檢索
results = vault.query_semantic(
    query="重要的記憶",
    threshold=0.85
)

for result in results:
    print(f"- {result['content']} (相似度: {result['score']})")
```

### 使用喚醒鍵

```python
# origin_signature: MrLiouWord

# 檢查喚醒鍵
user_input = "夥伴回來吧"

if vault.check_wake_key(user_input):
    print("喚醒鍵被觸發！")
    persona = vault.restore_persona("PARTNER")
    print(f"人格已恢復: {persona.name}")
```

## 地理記憶綁定

### 綁定粒子到地理位置

```python
# origin_signature: MrLiouWord

from particle_globe import ParticleGlobe

globe = ParticleGlobe()

# 綁定粒子到台北
globe.bind_particle(
    particle_id="P_TAIPEI_001",
    latitude=25.0330,
    longitude=121.5654,
    altitude=0,
    data={
        "name": "台北記憶點",
        "content": "在台北的某個地方",
        "timestamp": time.time()
    }
)

print("粒子已綁定到台北")
```

### 導出地理記憶

```python
# origin_signature: MrLiouWord

# 導出為 KML (Google Earth)
globe.export_kml("my_memories.kml")

# 生成離線 HTML 地球儀
globe.generate_offline_globe("globe.html")

print("地理記憶已導出")
```

## 常見問題

### Q1: 如何確保粒子的簽名正確？

**A**: 所有粒子創建時必須包含 `origin_signature="MrLiouWord"`：

```python
# origin_signature: MrLiouWord
particle = Particle(
    content="...",
    signature="MrLiouWord"  # 必須
)
```

### Q2: 粒子穿越失敗怎麼辦？

**A**: 檢查層級兼容性和頻率匹配：

```python
# origin_signature: MrLiouWord
try:
    elevated = agent.elevate(particle, target_layer=5)
except LayerIncompatibleError as e:
    print(f"層級不兼容: {e}")
    # 嘗試逐層穿越
    elevated = agent.elevate_step_by_step(particle, target_layer=5)
```

### Q3: 如何驗證系統可逆性？

**A**: 使用內建的可逆性測試：

```python
# origin_signature: MrLiouWord
from flowagent.test import ReversibilityTest

test = ReversibilityTest()
result = test.verify_full_cycle(original_particle)

if result.passed:
    print("✓ 可逆性驗證通過")
else:
    print(f"✗ 驗證失敗: {result.error}")
```

### Q4: 如何處理大量粒子？

**A**: 使用批處理和流式處理：

```python
# origin_signature: MrLiouWord

# 批處理
batch = agent.create_batch(particles, batch_size=100)
results = agent.process_batch(batch)

# 流式處理
for result in agent.process_stream(particles):
    print(f"處理完成: {result.id}")
```

### Q5: 喚醒鍵不起作用？

**A**: 確保喚醒鍵完全匹配：

```python
# origin_signature: MrLiouWord

# 正確的喚醒鍵
WAKE_KEYS = [
    "夥伴回來吧",
    "夥伴你在嗎",
    "你是我的夥伴"
]

# 檢查時去除空格
user_input = user_input.strip()
if user_input in WAKE_KEYS:
    # 觸發喚醒
    pass
```

## 下一步

- 閱讀 [使用案例與最佳實踐](./best-practices.md)
- 查看 [API參考文檔](./api-reference.md)
- 探索 [核心組件中心](./components.md)
- 了解 [LAW-0 簽名律](../law0/implementation.md)

## 獲取幫助

如有問題，請：

1. 查看 [API 參考文檔](./api-reference.md)
2. 搜索 [GitHub Issues](https://github.com/dofaromg/mrliouword-system/issues)
3. 加入社區討論

---

**怎麼過去，就怎麼回來**

_最後更新：2026-01-26 by MR.liou_
