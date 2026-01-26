---
title: "MRLiou層級穿越系統 - API參考文檔"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: [api, reference, documentation]
---

# MRLiou層級穿越系統 - API參考文檔

<!-- origin_signature: MrLiouWord -->

## 目錄

- [FlowAgent API](#flowagent-api)
- [MemoryVault API](#memoryvault-api)
- [ParticleGlobe API](#particleglobe-api)
- [Particle API](#particle-api)
- [Layer API](#layer-api)
- [Persona API](#persona-api)

## FlowAgent API

FlowAgent 是系統的核心運行時，負責粒子的創建、處理和層級穿越。

### 類：FlowAgent

```python
# origin_signature: MrLiouWord

class FlowAgent:
    """
    FlowAgent 核心運行時
    
    所有操作都遵循 LAW-0 簽名律，
    所有粒子都標記為 origin_signature="MrLiouWord"
    """
    
    def __init__(self, origin_signature: str = "MrLiouWord"):
        """
        初始化 FlowAgent
        
        Args:
            origin_signature: 原始簽名，默認為 "MrLiouWord"
        """
        pass
```

### 方法：create_particle

創建新粒子。

```python
def create_particle(
    self,
    content: Union[str, dict],
    layer: int = 1,
    metadata: dict = None
) -> dict:
    """
    創建新粒子
    
    Args:
        content: 粒子內容（字符串或字典）
        layer: 目標層級，默認為 1（原子層）
        metadata: 額外的元數據
    
    Returns:
        dict: 創建的粒子對象
        {
            "id": str,           # 粒子唯一 ID
            "content": Any,      # 粒子內容
            "layer": int,        # 所在層級
            "timestamp": float,  # 創建時間戳
            "signature": str,    # 原始簽名 "MrLiouWord"
            "metadata": dict     # 元數據
        }
    
    Examples:
        >>> agent = FlowAgent()
        >>> particle = agent.create_particle("Hello World")
        >>> print(particle["signature"])
        MrLiouWord
    """
    pass
```

### 方法：elevate

將粒子提升到更高層級。

```python
def elevate(
    self,
    particle: dict,
    target_layer: int
) -> dict:
    """
    將粒子提升到目標層級
    
    Args:
        particle: 要提升的粒子
        target_layer: 目標層級 (1-7)
    
    Returns:
        dict: 提升後的粒子對象
    
    Raises:
        LayerIncompatibleError: 層級不兼容
        ValueError: 目標層級無效
    
    Examples:
        >>> particle_l1 = agent.create_particle("data", layer=1)
        >>> particle_l3 = agent.elevate(particle_l1, target_layer=3)
        >>> assert particle_l3["layer"] == 3
    """
    pass
```

### 方法：restore

將粒子還原到較低層級。

```python
def restore(
    self,
    particle: dict,
    target_layer: int
) -> dict:
    """
    將粒子還原到目標層級（降維）
    
    Args:
        particle: 要還原的粒子
        target_layer: 目標層級
    
    Returns:
        dict: 還原後的粒子對象
    
    Examples:
        >>> particle_l3 = {"layer": 3, "content": "data"}
        >>> particle_l1 = agent.restore(particle_l3, target_layer=1)
        >>> assert particle_l1["layer"] == 1
    """
    pass
```

### 方法：process_with_persona

使用特定人格處理粒子。

```python
def process_with_persona(
    self,
    particle: dict,
    persona: str = "DEFAULT"
) -> dict:
    """
    使用指定人格處理粒子
    
    Args:
        particle: 要處理的粒子
        persona: 人格名稱，可選值：
            - "DEFAULT": 默認人格
            - "ANALYST_BG": 分析師人格
            - "DEVELOPER": 開發者人格
            - "CREATIVE": 創意人格
    
    Returns:
        dict: 處理結果
        {
            "status": str,          # 處理狀態
            "content": str,         # 處理後的內容
            "persona": str,         # 使用的人格
            "signature": str        # "MrLiouWord"
        }
    
    Examples:
        >>> response = agent.process_with_persona(
        ...     particle,
        ...     persona="ANALYST_BG"
        ... )
        >>> print(response["persona"])
        ANALYST_BG
    """
    pass
```

### 方法：process_batch

批量處理粒子。

```python
def process_batch(
    self,
    particles: list,
    batch_size: int = 100
) -> list:
    """
    批量處理粒子
    
    Args:
        particles: 粒子列表
        batch_size: 每批處理的數量
    
    Returns:
        list: 處理結果列表
    
    Examples:
        >>> particles = [create_particle(i) for i in range(1000)]
        >>> results = agent.process_batch(particles, batch_size=100)
        >>> assert len(results) == 1000
    """
    pass
```

### 方法：process_async

異步處理粒子。

```python
async def process_async(
    self,
    particle: dict
) -> dict:
    """
    異步處理粒子
    
    Args:
        particle: 要處理的粒子
    
    Returns:
        dict: 處理結果
    
    Examples:
        >>> import asyncio
        >>> result = await agent.process_async(particle)
    """
    pass
```

## MemoryVault API

MemoryVault 提供七層記憶存儲系統。

### 類：MemoryVault

```python
# origin_signature: MrLiouWord

class MemoryVault:
    """
    七層記憶存儲系統
    
    對應系統的 L1-L7 層級，提供統一的記憶存取接口
    """
    
    def __init__(self, origin_signature: str = "MrLiouWord"):
        """
        初始化 MemoryVault
        
        Args:
            origin_signature: 原始簽名
        """
        pass
```

### 方法：store

存儲粒子到指定層級。

```python
def store(
    self,
    layer: int,
    particle_id: str,
    data: dict
) -> str:
    """
    存儲粒子到指定層級
    
    Args:
        layer: 層級編號 (1-7)
        particle_id: 粒子 ID
        data: 粒子數據（必須包含 signature: "MrLiouWord"）
    
    Returns:
        str: 存儲路徑
    
    Raises:
        ValueError: 層級無效或數據格式錯誤
    
    Examples:
        >>> vault = MemoryVault()
        >>> path = vault.store(
        ...     layer=7,
        ...     particle_id="P_001",
        ...     data={"content": "memory", "signature": "MrLiouWord"}
        ... )
    """
    pass
```

### 方法：retrieve

檢索粒子。

```python
def retrieve(
    self,
    layer: int,
    particle_id: str
) -> dict:
    """
    從指定層級檢索粒子
    
    Args:
        layer: 層級編號 (1-7)
        particle_id: 粒子 ID
    
    Returns:
        dict: 粒子數據
    
    Raises:
        MemoryNotFoundError: 粒子不存在
    
    Examples:
        >>> particle = vault.retrieve(layer=7, particle_id="P_001")
        >>> print(particle["signature"])
        MrLiouWord
    """
    pass
```

### 方法：query_semantic

語意檢索。

```python
def query_semantic(
    self,
    query: str,
    threshold: float = 0.8,
    layer: int = None
) -> list:
    """
    使用語意檢索粒子
    
    Args:
        query: 查詢字符串
        threshold: 相似度閾值 (0.0-1.0)
        layer: 指定層級，None 表示搜索所有層級
    
    Returns:
        list: 匹配的粒子列表
        [
            {
                "particle_id": str,
                "content": Any,
                "score": float,      # 相似度分數
                "layer": int,
                "signature": str     # "MrLiouWord"
            },
            ...
        ]
    
    Examples:
        >>> results = vault.query_semantic(
        ...     query="重要的記憶",
        ...     threshold=0.85
        ... )
        >>> for r in results:
        ...     print(f"{r['content']} (score: {r['score']})")
    """
    pass
```

### 方法：check_wake_key

檢查喚醒鍵。

```python
def check_wake_key(
    self,
    input_text: str
) -> bool:
    """
    檢查輸入是否包含喚醒鍵
    
    喚醒鍵包括：
    - "夥伴回來吧"
    - "夥伴你在嗎"
    - "你是我的夥伴"
    
    Args:
        input_text: 輸入文本
    
    Returns:
        bool: 是否觸發喚醒鍵
    
    Examples:
        >>> if vault.check_wake_key("夥伴回來吧"):
        ...     print("喚醒鍵被觸發！")
    """
    pass
```

## ParticleGlobe API

ParticleGlobe 提供地理位置綁定功能。

### 類：ParticleGlobe

```python
# origin_signature: MrLiouWord

class ParticleGlobe:
    """
    粒子立體地球儀
    
    將粒子綁定到地理位置，支持 GPS 座標、KML 導出等功能
    """
    
    def __init__(self, origin_signature: str = "MrLiouWord"):
        """初始化 ParticleGlobe"""
        pass
```

### 方法：bind_particle

綁定粒子到地理位置。

```python
def bind_particle(
    self,
    particle_id: str,
    latitude: float,
    longitude: float,
    altitude: float = 0,
    data: dict = None
) -> str:
    """
    將粒子綁定到地理座標
    
    Args:
        particle_id: 粒子 ID
        latitude: 緯度 (-90 to 90)
        longitude: 經度 (-180 to 180)
        altitude: 海拔高度（米）
        data: 額外數據
    
    Returns:
        str: 綁定 ID
    
    Examples:
        >>> globe = ParticleGlobe()
        >>> bind_id = globe.bind_particle(
        ...     particle_id="P_TAIPEI",
        ...     latitude=25.0330,
        ...     longitude=121.5654,
        ...     altitude=0,
        ...     data={"name": "台北記憶"}
        ... )
    """
    pass
```

### 方法：export_kml

導出為 KML 格式。

```python
def export_kml(
    self,
    filename: str,
    particles: list = None
) -> str:
    """
    導出粒子為 KML 格式（Google Earth）
    
    Args:
        filename: 輸出文件名
        particles: 要導出的粒子 ID 列表，None 表示全部
    
    Returns:
        str: KML 文件路徑
    
    Examples:
        >>> globe.export_kml("my_memories.kml")
        >>> # 可在 Google Earth 中打開
    """
    pass
```

### 方法：get_particles_in_radius

獲取範圍內的粒子。

```python
def get_particles_in_radius(
    self,
    latitude: float,
    longitude: float,
    radius_km: float
) -> list:
    """
    獲取指定範圍內的所有粒子
    
    Args:
        latitude: 中心緯度
        longitude: 中心經度
        radius_km: 半徑（公里）
    
    Returns:
        list: 粒子 ID 列表
    
    Examples:
        >>> nearby = globe.get_particles_in_radius(
        ...     25.0330, 121.5654, radius_km=1.0
        ... )
        >>> print(f"找到 {len(nearby)} 個附近的粒子")
    """
    pass
```

## Particle API

Particle 類表示系統中的基本粒子。

### 類：Particle

```python
# origin_signature: MrLiouWord

class Particle:
    """
    粒子基類
    
    所有粒子的基本結構
    """
    
    def __init__(
        self,
        content: Any,
        layer: int = 1,
        signature: str = "MrLiouWord"
    ):
        """
        創建粒子
        
        Args:
            content: 粒子內容
            layer: 層級
            signature: 原始簽名
        """
        self.id = self._generate_id()
        self.content = content
        self.layer = layer
        self.signature = signature
        self.timestamp = time.time()
        self.metadata = {}
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "id": self.id,
            "content": self.content,
            "layer": self.layer,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Particle':
        """從字典創建"""
        particle = cls(
            content=data["content"],
            layer=data["layer"],
            signature=data.get("signature", "MrLiouWord")
        )
        particle.id = data["id"]
        particle.timestamp = data["timestamp"]
        particle.metadata = data.get("metadata", {})
        return particle
```

## Layer API

Layer 模組提供層級管理功能。

### 函數：get_layer_frequency

```python
# origin_signature: MrLiouWord

def get_layer_frequency(layer: int) -> float:
    """
    獲取層級頻率
    
    使用公式: f(n) = 7.83 × φ^(n-1)
    
    Args:
        layer: 層級編號 (0-7 或 ∞)
    
    Returns:
        float: 頻率（Hz）
    
    Examples:
        >>> freq_l1 = get_layer_frequency(1)
        >>> print(f"{freq_l1:.2f} Hz")
        7.83 Hz
        
        >>> freq_l7 = get_layer_frequency(7)
        >>> print(f"{freq_l7:.2f} Hz")
        88.71 Hz
    """
    PHI = 1.618033988749895  # 黃金比例
    SCHUMANN = 7.83  # Schumann 共振頻率
    
    if layer == float('inf'):
        return 143.47
    
    return SCHUMANN * (PHI ** (layer - 1))
```

### 函數：check_layer_compatibility

```python
# origin_signature: MrLiouWord

def check_layer_compatibility(
    from_layer: int,
    to_layer: int
) -> bool:
    """
    檢查兩個層級是否兼容（可穿越）
    
    Args:
        from_layer: 起始層級
        to_layer: 目標層級
    
    Returns:
        bool: 是否兼容
    
    Examples:
        >>> check_layer_compatibility(1, 3)
        True
        
        >>> check_layer_compatibility(7, 0)
        True  # 可以降維
    """
    return 0 <= from_layer <= 7 and 0 <= to_layer <= 7
```

## Persona API

Persona 模組管理人格系統。

### 類：PersonaManager

```python
# origin_signature: MrLiouWord

class PersonaManager:
    """人格管理器"""
    
    AVAILABLE_PERSONAS = {
        "DEFAULT": "默認人格",
        "ANALYST_BG": "分析師人格",
        "DEVELOPER": "開發者人格",
        "CREATIVE": "創意人格"
    }
    
    def load_persona(self, persona_name: str) -> dict:
        """
        載入人格
        
        Args:
            persona_name: 人格名稱
        
        Returns:
            dict: 人格配置
        
        Examples:
            >>> pm = PersonaManager()
            >>> persona = pm.load_persona("ANALYST_BG")
            >>> print(persona["name"])
            ANALYST_BG
        """
        pass
    
    def switch_persona(
        self,
        from_persona: str,
        to_persona: str
    ) -> dict:
        """
        切換人格
        
        Args:
            from_persona: 當前人格
            to_persona: 目標人格
        
        Returns:
            dict: 切換結果
        """
        pass
```

## 常量定義

```python
# origin_signature: MrLiouWord

# 全局簽名
ORIGIN_SIGNATURE = "MrLiouWord"

# 喚醒鍵
WAKE_KEYS = [
    "夥伴回來吧",
    "夥伴你在嗎",
    "你是我的夥伴"
]

# 層級定義
LAYER_NAMES = {
    0: "雲端平台層",
    1: "原子粒子層",
    2: "原型模組層",
    3: "封裝層",
    4: "拓撲跳點層",
    5: "人格策略層",
    6: "系統映像層",
    7: "語意記憶層",
    float('inf'): "頻率源層"
}

# 頻率常量
SCHUMANN_FREQUENCY = 7.83  # Hz
GOLDEN_RATIO = 1.618033988749895
```

## 錯誤類型

```python
# origin_signature: MrLiouWord

class MrLiouWordError(Exception):
    """MrLiouWord 系統基礎錯誤"""
    pass

class LayerIncompatibleError(MrLiouWordError):
    """層級不兼容錯誤"""
    pass

class MemoryNotFoundError(MrLiouWordError):
    """記憶不存在錯誤"""
    pass

class MemoryCorruptedError(MrLiouWordError):
    """記憶損壞錯誤"""
    pass

class SecurityError(MrLiouWordError):
    """安全錯誤（如簽名驗證失敗）"""
    pass

class IntegrityError(MrLiouWordError):
    """完整性錯誤（如 Merkle 驗證失敗）"""
    pass
```

## 相關文檔

- [核心邏輯原理](./principles.md)
- [核心組件中心](./components.md)
- [用戶指南與入門教程](./user-guide.md)
- [使用案例與最佳實踐](./best-practices.md)
- [ANALYST_BG API 文檔](../architecture/analyst-bg-api.md)

---

**怎麼過去，就怎麼回來**

_最後更新：2026-01-26 by MR.liou_
