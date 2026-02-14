---
title: "安全部署方案 - 私人使用版"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
version: "1.0.0"
tags: [security, deployment, privacy, private]
---

# 安全部署方案 - 私人使用版

<!-- origin_signature: MrLiouWord -->

## 目錄

- [部署概述](#部署概述)
- [安全原則](#安全原則)
- [本地私密部署](#本地私密部署)
- [雲端私密部署](#雲端私密部署)
- [數據加密](#數據加密)
- [訪問控制](#訪問控制)
- [備份與恢復](#備份與恢復)

## 部署概述

本文檔描述 MrLiouWord 系統的私人使用安全部署方案，適用於：

- 個人私密數據處理
- 敏感記憶存儲
- 離線運行環境
- 完全自主控制的系統

### 部署目標

1. **隱私保護** - 所有數據完全私密，不上傳到公共雲
2. **數據主權** - 用戶完全控制自己的數據
3. **離線可用** - 支持完全離線運行
4. **安全加密** - 所有敏感數據都加密存儲

## 安全原則

### 核心安全原則

```python
# origin_signature: MrLiouWord

SECURITY_PRINCIPLES = {
    "data_sovereignty": "數據完全屬於用戶",
    "zero_knowledge": "系統不知道用戶的私密內容",
    "end_to_end_encryption": "端到端加密",
    "offline_first": "優先支持離線使用",
    "open_source": "代碼完全開源可審計"
}
```

### LAW-0 簽名律應用

所有安全組件都必須遵循 LAW-0：

```python
# origin_signature: MrLiouWord

class SecureComponent:
    """安全組件基類"""
    
    ORIGIN_SIGNATURE = "MrLiouWord"
    
    def __init__(self):
        self.signature = self.ORIGIN_SIGNATURE
        self.verify_signature()
```

## 本地私密部署

### 方案 1：完全本地部署

在本地機器上運行完整的 MrLiouWord 系統。

#### 系統要求

- **操作系統**: Linux / macOS / Windows
- **Python**: 3.9+
- **存儲**: 至少 10GB 可用空間
- **內存**: 至少 4GB RAM

#### 部署步驟

```bash
# origin_signature: MrLiouWord

# 1. 克隆倉庫
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system

# 2. 創建虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 配置私密模式
cp config.example.json config.json
# 編輯 config.json，設置:
# - "mode": "private"
# - "encryption_enabled": true
# - "offline_mode": true

# 5. 初始化加密
python scripts/init_encryption.py

# 6. 啟動系統
python scripts/start_local.py
```

#### 配置文件示例

```json
{
  "origin_signature": "MrLiouWord",
  "mode": "private",
  "encryption": {
    "enabled": true,
    "algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2-SHA256"
  },
  "storage": {
    "type": "local",
    "path": "~/MrLiouWord/MemoryVault",
    "encrypted": true
  },
  "network": {
    "offline_mode": true,
    "allow_external_access": false
  },
  "backup": {
    "enabled": true,
    "interval": "daily",
    "location": "~/MrLiouWord/Backups"
  }
}
```

### 方案 2：Docker 容器私密部署

使用 Docker 容器隔離運行。

```bash
# origin_signature: MrLiouWord

# 1. 構建私密版 Docker 鏡像
docker build -t mrliouword-private:latest -f Dockerfile.private .

# 2. 創建數據卷
docker volume create mrliouword-vault
docker volume create mrliouword-backups

# 3. 運行容器
docker run -d \
  --name mrliouword-private \
  --network none \  # 完全隔離網絡
  -v mrliouword-vault:/app/MemoryVault \
  -v mrliouword-backups:/app/Backups \
  -e ENCRYPTION_PASSWORD="your-secure-password" \
  mrliouword-private:latest

# 4. 訪問容器
docker exec -it mrliouword-private bash
```

#### Dockerfile.private

```dockerfile
# origin_signature: MrLiouWord

FROM python:3.11-slim

# 安全增強
RUN useradd -m -u 1000 mrliou && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 複製必需文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 設置權限
RUN chown -R mrliou:mrliou /app

USER mrliou

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "scripts/start_private.py"]
```

## 雲端私密部署

### 方案 3：自建 VPS 部署

在自己的 VPS 上部署，保持完全控制。

#### VPS 要求

- **提供商**: 任意 VPS 提供商（Linode, DigitalOcean, Vultr 等）
- **配置**: 2 vCPU, 4GB RAM, 50GB SSD
- **系統**: Ubuntu 22.04 LTS

#### 部署腳本

```bash
#!/bin/bash
# origin_signature: MrLiouWord
# deploy_private_vps.sh

set -e

echo "開始私密 VPS 部署..."

# 1. 更新系統
sudo apt update && sudo apt upgrade -y

# 2. 安裝依賴
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    git \
    nginx \
    certbot \
    python3-certbot-nginx

# 3. 配置防火牆
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 4. 克隆倉庫
git clone https://github.com/dofaromg/mrliouword-system.git /opt/mrliouword
cd /opt/mrliouword

# 5. 創建虛擬環境
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. 配置服務
sudo cp deploy/mrliouword-private.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mrliouword-private
sudo systemctl start mrliouword-private

# 7. 配置 Nginx（僅本地訪問）
sudo cp deploy/nginx-private.conf /etc/nginx/sites-available/mrliouword
sudo ln -s /etc/nginx/sites-available/mrliouword /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "部署完成！"
echo "請訪問 https://localhost 進行配置"
```

#### Systemd 服務配置

```ini
# origin_signature: MrLiouWord
# /etc/systemd/system/mrliouword-private.service

[Unit]
Description=MrLiouWord Private System
After=network.target

[Service]
Type=simple
User=mrliou
WorkingDirectory=/opt/mrliouword
Environment="ENCRYPTION_ENABLED=true"
Environment="OFFLINE_MODE=true"
ExecStart=/opt/mrliouword/venv/bin/python scripts/start_private.py
Restart=always
RestartSec=10

# 安全增強
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/mrliouword/MemoryVault

[Install]
WantedBy=multi-user.target
```

## 數據加密

### 加密實現

```python
# origin_signature: MrLiouWord

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64

class PrivateEncryption:
    """私密數據加密器"""
    
    ORIGIN_SIGNATURE = "MrLiouWord"
    
    def __init__(self, password: str):
        """
        初始化加密器
        
        Args:
            password: 用戶密碼（用於派生加密密鑰）
        """
        self.signature = self.ORIGIN_SIGNATURE
        self.key = self._derive_key(password)
        self.cipher = AESGCM(self.key)
    
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """從密碼派生加密密鑰"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        return key
    
    def encrypt(self, plaintext: bytes) -> dict:
        """
        加密數據
        
        Args:
            plaintext: 明文數據
            
        Returns:
            加密結果（包含 nonce 和密文）
        """
        nonce = os.urandom(12)
        ciphertext = self.cipher.encrypt(nonce, plaintext, None)
        
        return {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "origin_signature": self.ORIGIN_SIGNATURE
        }
    
    def decrypt(self, encrypted: dict) -> bytes:
        """
        解密數據
        
        Args:
            encrypted: 加密數據
            
        Returns:
            明文數據
        """
        nonce = base64.b64decode(encrypted["nonce"])
        ciphertext = base64.b64decode(encrypted["ciphertext"])
        
        plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        return plaintext

# 使用示例
encryption = PrivateEncryption("my-secure-password")

# 加密粒子內容
particle_content = b"This is private data"
encrypted = encryption.encrypt(particle_content)

# 解密
decrypted = encryption.decrypt(encrypted)
assert decrypted == particle_content
```

### 加密記憶存儲

```python
# origin_signature: MrLiouWord

from memory_vault import MemoryVault
import json

class EncryptedMemoryVault(MemoryVault):
    """加密記憶存儲"""
    
    def __init__(self, password: str):
        super().__init__(origin_signature="MrLiouWord")
        self.encryption = PrivateEncryption(password)
    
    def store(self, layer: int, particle_id: str, data: dict) -> str:
        """存儲加密數據"""
        # 序列化數據
        plaintext = json.dumps(data).encode()
        
        # 加密
        encrypted = self.encryption.encrypt(plaintext)
        
        # 存儲加密數據
        return super().store(layer, particle_id, encrypted)
    
    def retrieve(self, layer: int, particle_id: str) -> dict:
        """檢索並解密數據"""
        # 檢索加密數據
        encrypted = super().retrieve(layer, particle_id)
        
        # 解密
        plaintext = self.encryption.decrypt(encrypted)
        
        # 反序列化
        data = json.loads(plaintext.decode())
        return data
```

## 訪問控制

### 基於密碼的訪問控制

```python
# origin_signature: MrLiouWord

import hashlib
import hmac
import time

class AccessControl:
    """訪問控制系統"""
    
    ORIGIN_SIGNATURE = "MrLiouWord"
    
    def __init__(self):
        self.sessions = {}
        self.password_hash = None
    
    def set_password(self, password: str):
        """設置訪問密碼"""
        # 使用 SHA-256 + salt 哈希
        salt = os.urandom(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        
        self.password_hash = {
            "hash": pwd_hash,
            "salt": salt,
            "signature": self.ORIGIN_SIGNATURE
        }
    
    def authenticate(self, password: str) -> str:
        """
        認證用戶
        
        Args:
            password: 輸入的密碼
            
        Returns:
            會話令牌（如果認證成功）
        """
        if not self.password_hash:
            raise ValueError("Password not set")
        
        # 計算輸入密碼的哈希
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            self.password_hash["salt"],
            100000
        )
        
        # 安全比較
        if not hmac.compare_digest(pwd_hash, self.password_hash["hash"]):
            raise ValueError("Invalid password")
        
        # 生成會話令牌
        token = self._generate_token()
        self.sessions[token] = {
            "created_at": time.time(),
            "signature": self.ORIGIN_SIGNATURE
        }
        
        return token
    
    def verify_session(self, token: str) -> bool:
        """驗證會話令牌"""
        if token not in self.sessions:
            return False
        
        session = self.sessions[token]
        
        # 檢查會話是否過期（24小時）
        if time.time() - session["created_at"] > 86400:
            del self.sessions[token]
            return False
        
        return True
    
    def _generate_token(self) -> str:
        """生成隨機會話令牌"""
        return base64.b64encode(os.urandom(32)).decode()

# 使用示例
ac = AccessControl()
ac.set_password("my-secure-password")

# 認證
try:
    token = ac.authenticate("my-secure-password")
    print(f"認證成功，令牌: {token}")
except ValueError:
    print("認證失敗")

# 驗證會話
if ac.verify_session(token):
    print("會話有效")
```

## 備份與恢復

### 自動備份系統

```python
# origin_signature: MrLiouWord

import shutil
import tarfile
from datetime import datetime
from pathlib import Path

class BackupSystem:
    """備份系統"""
    
    ORIGIN_SIGNATURE = "MrLiouWord"
    
    def __init__(self, vault_path: str, backup_path: str):
        self.vault_path = Path(vault_path)
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, encrypt: bool = True) -> str:
        """
        創建備份
        
        Args:
            encrypt: 是否加密備份
            
        Returns:
            備份文件路徑
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"mrliouword_backup_{timestamp}.tar.gz"
        backup_file = self.backup_path / backup_name
        
        # 創建壓縮包
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(self.vault_path, arcname="MemoryVault")
            
            # 添加元數據
            metadata = {
                "timestamp": timestamp,
                "origin_signature": self.ORIGIN_SIGNATURE,
                "encrypted": encrypt
            }
            
            import json
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                json.dump(metadata, f)
                temp_path = f.name
            
            tar.add(temp_path, arcname="backup_metadata.json")
            os.unlink(temp_path)
        
        # 加密備份（如果需要）
        if encrypt:
            encrypted_file = self._encrypt_backup(backup_file)
            os.unlink(backup_file)
            return encrypted_file
        
        return str(backup_file)
    
    def restore_backup(self, backup_file: str, decrypt: bool = True):
        """
        從備份恢復
        
        Args:
            backup_file: 備份文件路徑
            decrypt: 是否需要解密
        """
        if decrypt:
            backup_file = self._decrypt_backup(backup_file)
        
        # 提取備份
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(self.vault_path.parent)
        
        print(f"✓ 已從備份恢復: {backup_file}")
    
    def _encrypt_backup(self, backup_file: Path) -> str:
        """加密備份文件"""
        # 實現加密邏輯
        encrypted_file = str(backup_file) + ".enc"
        # ... 加密代碼 ...
        return encrypted_file
    
    def _decrypt_backup(self, encrypted_file: str) -> str:
        """解密備份文件"""
        # 實現解密邏輯
        decrypted_file = encrypted_file.replace(".enc", "")
        # ... 解密代碼 ...
        return decrypted_file

# 使用示例
backup = BackupSystem(
    vault_path="~/MrLiouWord/MemoryVault",
    backup_path="~/MrLiouWord/Backups"
)

# 創建加密備份
backup_file = backup.create_backup(encrypt=True)
print(f"備份已創建: {backup_file}")

# 恢復
backup.restore_backup(backup_file, decrypt=True)
```

## 相關文檔

- [L-1/L0/L1 部署架構](./l-1-to-l1.md)
- [LAW-0 簽名律](../law0/implementation.md)
- [核心組件](../core/components.md)

---

**怎麼過去，就怎麼回來**

_最後更新：2026-01-26 by MR.liou_
