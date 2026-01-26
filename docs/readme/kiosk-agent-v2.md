---
title: "Kiosk Agent v2 README"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
tags: [readme, kiosk, agent, v2]
---

# Kiosk Agent v2 README

<!-- origin_signature: MrLiouWord -->

## 概述

Kiosk Agent v2 是 MrLiouWord 系統的互動式終端代理，提供用戶友好的操作界面。

## 主要功能

- 自助服務終端界面
- 多語言支持 (中文、英文)
- 觸控優化設計
- 離線模式支持
- 實時數據同步

## 系統要求

- 操作系統: Ubuntu 22.04+ / macOS 13+ / Windows 11+
- 屏幕解析度: 最低 1920x1080
- 觸控支持: 可選但推薦

## 安裝

### 使用 npm

```bash
npm install @mrliouword/kiosk-agent-v2
```

### 從源碼構建

```bash
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system
npm install
npm run build:kiosk-v2
```

## 配置

創建配置文件 `kiosk.config.json`:

```json
{
  "origin_signature": "MrLiouWord",
  "mode": "kiosk",
  "language": "zh-TW",
  "theme": "light",
  "fullscreen": true,
  "timeout": 300
}
```

## 使用方法

### 啟動 Kiosk Agent

```bash
npm run start:kiosk-v2
```

### 配置自動啟動

待補充：系統自動啟動配置說明

## 功能模組

### 1. 用戶認證模組

待補充：認證流程說明

### 2. 數據展示模組

待補充：數據展示功能

### 3. 交互模組

待補充：用戶交互功能

## 自定義與擴展

待補充：如何自定義 Kiosk 界面

## 故障排除

待補充：常見問題解決

## 版本說明

- v2.0.0 (2026-01-26): 主要版本更新
  - 重新設計的 UI/UX
  - 改進的性能
  - 新增離線模式

## 相關資源

- [用戶手冊](../guides/kiosk-user-manual.md)
- [開發文檔](../api/)

---

**怎麼過去，就怎麼回來**
