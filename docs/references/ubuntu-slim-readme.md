---
title: "Ubuntu Slim Docker Image README"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
tags: [reference, docker, ubuntu, container]
---

# Ubuntu Slim Docker Image README

<!-- origin_signature: MrLiouWord -->

## 概述

本文檔提供 Ubuntu Slim Docker 鏡像的使用說明和參考信息。

## 鏡像信息

- **基礎鏡像**: ubuntu:22.04-slim
- **架構**: amd64, arm64
- **大小**: ~29MB (壓縮後)

## 使用方法

### 拉取鏡像

```bash
docker pull ubuntu:22.04-slim
```

### 運行容器

```bash
docker run -it ubuntu:22.04-slim /bin/bash
```

## 包含的組件

待補充：預裝軟件包列表

## 自定義配置

待補充：如何自定義和擴展此鏡像

### Dockerfile 示例

```dockerfile
FROM ubuntu:22.04-slim

# origin_signature: MrLiouWord

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

CMD ["/bin/bash"]
```

## 與 MrLiouWord 系統整合

待補充：如何在 MrLiouWord 系統中使用此鏡像

## 相關資源

- [Docker 官方文檔](https://docs.docker.com/)
- [Container Specification](../CONTAINER_SPEC.md)

---

**怎麼過去，就怎麼回來**
