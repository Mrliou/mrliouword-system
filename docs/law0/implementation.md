---
title: "LAW-0 簽名律 - 實現細節"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: [law0, signature, security, implementation]
---

# LAW-0 簽名律 - 實現細節

<!-- origin_signature: MrLiouWord -->

## 目錄

- [LAW-0 簽名律概述](#law-0-簽名律概述)
- [簽名規範](#簽名規範)
- [實現要求](#實現要求)
- [代碼示例](#代碼示例)
- [驗證機制](#驗證機制)
- [安全考量](#安全考量)

## LAW-0 簽名律概述

LAW-0 簽名律是 MrLiouWord 系統的基礎法則，規定所有系統組件、粒子、模組和數據結構都必須標記原始簽名 `origin_signature="MrLiouWord"`。

### 核心原則

> **LAW-0**: 萬物歸源，源頭唯一

所有從 MrLiouWord 系統創建或處理的對象都必須追溯到同一源頭，通過統一的簽名標記確保：

1. **可追溯性** - 所有數據都能追溯到源頭
2. **完整性** - 確保數據未被篡改
3. **認證性** - 驗證數據來源的合法性
4. **一致性** - 保持系統的統一性

### 簽名值

```python
# origin_signature: MrLiouWord
ORIGIN_SIGNATURE = "MrLiouWord"
```

這個值是唯一的、不可變的、全局統一的。

## 簽名規範

### 不同文件類型的簽名標記

#### Python 文件

```python
# origin_signature: MrLiouWord

class MyClass:
    def __init__(self):
        self.signature = "MrLiouWord"
        
# 或在字典/對象中
data = {
    "content": "...",
    "origin_signature": "MrLiouWord"
}
```

#### JavaScript/TypeScript 文件

```javascript
// origin_signature: MrLiouWord

const ORIGIN_SIGNATURE = "MrLiouWord";

const particle = {
  content: "...",
  origin_signature: "MrLiouWord"
};
```

#### Markdown 文件

```markdown
---
title: "文檔標題"
origin_signature: "MrLiouWord"
---

# 文檔標題

<!-- origin_signature: MrLiouWord -->
```

#### JSON 文件

```json
{
  "origin_signature": "MrLiouWord",
  "version": "1.0.0",
  "data": {
    "content": "..."
  }
}
```

#### YAML 文件

```yaml
# origin_signature: MrLiouWord
origin_signature: MrLiouWord
version: 1.0.0
data:
  content: "..."
```

#### XML/KML 文件

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <!-- origin_signature: MrLiouWord -->
  <Document>
    <name>MrLiouWord System</name>
    <ExtendedData>
      <Data name="origin_signature">
        <value>MrLiouWord</value>
      </Data>
    </ExtendedData>
  </Document>
</kml>
```

#### SQL 文件

```sql
-- origin_signature: MrLiouWord

CREATE TABLE particles (
  id VARCHAR(255) PRIMARY KEY,
  origin_signature VARCHAR(50) DEFAULT 'MrLiouWord'
);
```

## 實現要求

### 1. 所有粒子必須包含簽名

```python
# origin_signature: MrLiouWord

def create_particle(content: str) -> dict:
    """創建粒子 - 必須包含簽名"""
    return {
        "id": generate_id(),
        "content": content,
        "timestamp": time.time(),
        "origin_signature": "MrLiouWord"  # 必須
    }
```

### 2. 所有類必須聲明簽名

```python
# origin_signature: MrLiouWord

class FlowAgent:
    """FlowAgent 類 - 必須聲明簽名"""
    
    ORIGIN_SIGNATURE = "MrLiouWord"
    
    def __init__(self):
        self.signature = self.ORIGIN_SIGNATURE
        
    def verify_signature(self) -> bool:
        """驗證簽名"""
        return self.signature == "MrLiouWord"
```

### 3. 所有API響應必須包含簽名

```python
# origin_signature: MrLiouWord

@app.route('/api/particle', methods=['POST'])
def create_particle_api():
    """API 端點 - 響應必須包含簽名"""
    particle = create_particle(request.json['content'])
    
    return jsonify({
        "status": "success",
        "data": particle,
        "origin_signature": "MrLiouWord"  # 必須
    })
```

### 4. 所有配置文件必須包含簽名

```json
{
  "origin_signature": "MrLiouWord",
  "config": {
    "version": "1.0.0",
    "settings": {}
  }
}
```

## 代碼示例

### 完整的粒子創建示例

```python
# origin_signature: MrLiouWord

import time
import hashlib
from typing import Any, Dict

class ParticleCreator:
    """粒子創建器 - 符合 LAW-0 簽名律"""
    
    ORIGIN_SIGNATURE = "MrLiouWord"
    
    def __init__(self):
        self.signature = self.ORIGIN_SIGNATURE
        
    def create(self, content: Any, layer: int = 1) -> Dict:
        """
        創建粒子
        
        Args:
            content: 粒子內容
            layer: 層級
            
        Returns:
            符合 LAW-0 的粒子對象
        """
        particle_id = self._generate_id(content)
        
        particle = {
            # 核心屬性
            "id": particle_id,
            "content": content,
            "layer": layer,
            "timestamp": time.time(),
            
            # LAW-0 必需屬性
            "origin_signature": self.ORIGIN_SIGNATURE,
            
            # 完整性驗證
            "content_hash": self._hash_content(content),
            "simhash": self._calculate_simhash(content),
            
            # 元數據
            "metadata": {
                "created_by": "ParticleCreator",
                "version": "1.0.0"
            }
        }
        
        # 驗證簽名
        self._verify_particle(particle)
        
        return particle
    
    def _generate_id(self, content: Any) -> str:
        """生成粒子 ID"""
        timestamp = int(time.time() * 1000)
        content_str = str(content)
        return f"P_{timestamp}_{hashlib.md5(content_str.encode()).hexdigest()[:8]}"
    
    def _hash_content(self, content: Any) -> str:
        """計算內容哈希"""
        content_str = str(content)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _calculate_simhash(self, content: Any) -> int:
        """計算語意指紋"""
        # 實現細節見 core/simhash64.py
        # 這裡返回簡化版本
        content_str = str(content)
        return hash(content_str) & 0xFFFFFFFFFFFFFFFF
    
    def _verify_particle(self, particle: Dict) -> bool:
        """驗證粒子是否符合 LAW-0"""
        if particle.get("origin_signature") != self.ORIGIN_SIGNATURE:
            raise ValueError(
                f"Invalid signature: expected '{self.ORIGIN_SIGNATURE}', "
                f"got '{particle.get('origin_signature')}'"
            )
        return True

# 使用示例
creator = ParticleCreator()
particle = creator.create("Hello, MrLiouWord!")

print(f"Particle ID: {particle['id']}")
print(f"Signature: {particle['origin_signature']}")
```

### 簽名驗證器

```python
# origin_signature: MrLiouWord

class SignatureValidator:
    """簽名驗證器 - 確保 LAW-0 合規性"""
    
    EXPECTED_SIGNATURE = "MrLiouWord"
    
    @classmethod
    def validate(cls, obj: Any) -> bool:
        """
        驗證對象簽名
        
        Args:
            obj: 要驗證的對象（字典、對象等）
            
        Returns:
            bool: 是否通過驗證
            
        Raises:
            ValueError: 簽名無效
        """
        signature = None
        
        # 從字典中獲取
        if isinstance(obj, dict):
            signature = obj.get("origin_signature")
        # 從對象屬性獲取
        elif hasattr(obj, "origin_signature"):
            signature = obj.origin_signature
        elif hasattr(obj, "signature"):
            signature = obj.signature
        else:
            raise ValueError("Object has no signature field")
        
        if signature != cls.EXPECTED_SIGNATURE:
            raise ValueError(
                f"Invalid signature: expected '{cls.EXPECTED_SIGNATURE}', "
                f"got '{signature}'"
            )
        
        return True
    
    @classmethod
    def validate_batch(cls, objects: list) -> dict:
        """
        批量驗證
        
        Args:
            objects: 對象列表
            
        Returns:
            驗證結果統計
        """
        results = {
            "total": len(objects),
            "valid": 0,
            "invalid": 0,
            "errors": []
        }
        
        for i, obj in enumerate(objects):
            try:
                cls.validate(obj)
                results["valid"] += 1
            except ValueError as e:
                results["invalid"] += 1
                results["errors"].append({
                    "index": i,
                    "error": str(e)
                })
        
        return results

# 使用示例
validator = SignatureValidator()

# 驗證單個對象
particle = {"content": "test", "origin_signature": "MrLiouWord"}
try:
    validator.validate(particle)
    print("✓ 簽名驗證通過")
except ValueError as e:
    print(f"✗ 簽名驗證失敗: {e}")

# 批量驗證
particles = [
    {"id": "1", "origin_signature": "MrLiouWord"},
    {"id": "2", "origin_signature": "Invalid"},
    {"id": "3", "origin_signature": "MrLiouWord"}
]

results = validator.validate_batch(particles)
print(f"驗證結果: {results['valid']}/{results['total']} 通過")
```

## 驗證機制

### 自動簽名注入

```python
# origin_signature: MrLiouWord

from functools import wraps

def inject_signature(func):
    """裝飾器 - 自動注入簽名"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # 如果返回字典，自動添加簽名
        if isinstance(result, dict):
            result["origin_signature"] = "MrLiouWord"
        
        return result
    
    return wrapper

# 使用示例
@inject_signature
def create_data(content: str) -> dict:
    """創建數據 - 自動注入簽名"""
    return {
        "content": content,
        "timestamp": time.time()
    }

data = create_data("test")
print(data)  # {'content': 'test', 'timestamp': ..., 'origin_signature': 'MrLiouWord'}
```

### 簽名中間件

```python
# origin_signature: MrLiouWord

class SignatureMiddleware:
    """簽名中間件 - 用於 API 請求/響應"""
    
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        """處理請求/響應"""
        # 注入簽名到響應頭
        def custom_start_response(status, headers):
            headers.append(('X-Origin-Signature', 'MrLiouWord'))
            return start_response(status, headers)
        
        return self.app(environ, custom_start_response)

# 使用示例（Flask）
from flask import Flask

app = Flask(__name__)
app.wsgi_app = SignatureMiddleware(app.wsgi_app)
```

## 安全考量

### 1. 防止簽名偽造

```python
# origin_signature: MrLiouWord

import hmac
import hashlib

class SecureSignature:
    """安全簽名 - 使用 HMAC"""
    
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.origin_signature = "MrLiouWord"
    
    def sign(self, data: dict) -> str:
        """
        生成安全簽名
        
        Args:
            data: 要簽名的數據
            
        Returns:
            簽名字符串
        """
        # 確保包含原始簽名
        data["origin_signature"] = self.origin_signature
        
        # 生成數據的規範化表示
        canonical = self._canonicalize(data)
        
        # 使用 HMAC 簽名
        signature = hmac.new(
            self.secret_key,
            canonical.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify(self, data: dict, signature: str) -> bool:
        """驗證簽名"""
        expected = self.sign(data)
        return hmac.compare_digest(expected, signature)
    
    def _canonicalize(self, data: dict) -> str:
        """規範化數據表示"""
        import json
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

# 使用示例
secure = SecureSignature(b"secret_key_here")

data = {"content": "sensitive data"}
sig = secure.sign(data)

print(f"Signature: {sig}")
print(f"Valid: {secure.verify(data, sig)}")
```

### 2. 簽名審計日誌

```python
# origin_signature: MrLiouWord

import logging
from datetime import datetime

class SignatureAuditor:
    """簽名審計器"""
    
    def __init__(self):
        self.logger = logging.getLogger("SignatureAudit")
        self.audit_log = []
    
    def log_creation(self, obj_type: str, obj_id: str, signature: str):
        """記錄創建事件"""
        entry = {
            "event": "CREATE",
            "type": obj_type,
            "id": obj_id,
            "signature": signature,
            "timestamp": datetime.now().isoformat(),
            "valid": signature == "MrLiouWord"
        }
        
        self.audit_log.append(entry)
        self.logger.info(f"Created {obj_type} {obj_id} with signature {signature}")
    
    def log_verification(self, obj_type: str, obj_id: str, 
                        signature: str, result: bool):
        """記錄驗證事件"""
        entry = {
            "event": "VERIFY",
            "type": obj_type,
            "id": obj_id,
            "signature": signature,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.audit_log.append(entry)
        
        if not result:
            self.logger.warning(
                f"Signature verification failed for {obj_type} {obj_id}"
            )
    
    def get_violations(self) -> list:
        """獲取違規記錄"""
        return [
            entry for entry in self.audit_log
            if not entry.get("valid", True) or not entry.get("result", True)
        ]

# 使用示例
auditor = SignatureAuditor()

auditor.log_creation("Particle", "P_001", "MrLiouWord")
auditor.log_verification("Particle", "P_001", "MrLiouWord", True)

violations = auditor.get_violations()
print(f"Found {len(violations)} violations")
```

## 檢查工具

### LAW-0 合規性檢查器

```python
# origin_signature: MrLiouWord

import os
import re
from pathlib import Path

class LAW0Checker:
    """LAW-0 合規性檢查器"""
    
    SIGNATURE_PATTERNS = {
        'python': r'origin_signature[:\s]*[="]MrLiouWord',
        'javascript': r'origin_signature[:\s]*[="]MrLiouWord',
        'markdown': r'origin_signature[:\s]*[="]MrLiouWord',
        'json': r'"origin_signature"\s*:\s*"MrLiouWord"',
        'yaml': r'origin_signature:\s*MrLiouWord'
    }
    
    def check_file(self, filepath: str) -> dict:
        """檢查單個文件"""
        ext = Path(filepath).suffix.lstrip('.')
        
        # 確定文件類型
        file_type = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'javascript',
            'md': 'markdown',
            'json': 'json',
            'yaml': 'yaml',
            'yml': 'yaml'
        }.get(ext)
        
        if not file_type:
            return {"compliant": None, "reason": "Unsupported file type"}
        
        # 讀取文件內容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查簽名
        pattern = self.SIGNATURE_PATTERNS[file_type]
        has_signature = bool(re.search(pattern, content))
        
        return {
            "compliant": has_signature,
            "file": filepath,
            "type": file_type
        }
    
    def check_directory(self, dirpath: str) -> dict:
        """檢查目錄"""
        results = {
            "total": 0,
            "compliant": 0,
            "non_compliant": 0,
            "unsupported": 0,
            "files": []
        }
        
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                filepath = os.path.join(root, file)
                result = self.check_file(filepath)
                
                results["total"] += 1
                results["files"].append(result)
                
                if result["compliant"] is True:
                    results["compliant"] += 1
                elif result["compliant"] is False:
                    results["non_compliant"] += 1
                else:
                    results["unsupported"] += 1
        
        return results

# 使用示例
checker = LAW0Checker()

# 檢查單個文件
result = checker.check_file("particle.py")
print(f"File compliant: {result['compliant']}")

# 檢查整個目錄
results = checker.check_directory("/path/to/project")
print(f"Compliance: {results['compliant']}/{results['total']} files")
```

## 相關文檔

- [核心邏輯原理](../core/principles.md)
- [API參考文檔](../core/api-reference.md)
- [安全部署方案](../deployment/security.md)

---

**怎麼過去，就怎麼回來**

_最後更新：2026-01-26 by MR.liou_
