/**
 * Particle Auth Gateway
 * 
 * 粒子認證網關 - 統一身份投影系統
 * 
 * 核心功能：
 * - 多平台 Token 統一管理
 * - MCP 代理
 * - ROAO 認知循環
 * - World API (心跳/頻率/波紋)
 * 
 * Author: MR.liou × Claude
 * Philosophy: 怎麼過去，就怎麼回來
 */

const 源 = "MrLiouWord";

const 自然 = {
  舒曼共振: 7.83,
  心跳: 1.2,
  黃金比: 1.618033988749895,
  引力: 9.81,
  磁場週期: 86400,
  源
};

// 頻率流過
function 流過(輸入: any) {
  const 現在 = Date.now();
  const 文字 = typeof 輸入 === "string" ? 輸入 : JSON.stringify(輸入);
  
  let 共振 = 0;
  for (let i = 0; i < 文字.length; i++) {
    共振 = (共振 << 5) - 共振 + 文字.charCodeAt(i);
    共振 = 共振 & 共振;
  }
  
  const 基頻 = 自然.舒曼共振 + (Math.abs(共振) % 100);
  
  return {
    源,
    基頻,
    諧波: [基頻, 基頻 * 自然.黃金比, 基頻 * 2, 基頻 * 自然.黃金比 * 2],
    相位: (現在 % 1000) / 1000 * 2 * Math.PI,
    振幅: Math.min(1, 文字.length / 1000),
    共振度: 1 - Math.abs(基頻 / 自然.舒曼共振 - Math.round(基頻 / 自然.舒曼共振)),
    時間: 現在
  };
}

// 心跳
function 心跳() {
  const 現在 = Date.now();
  const 週期 = 1000 / 自然.心跳;
  const 相位 = (現在 % 週期) / 週期;
  
  return {
    源,
    時間: 現在,
    相位,
    振幅: 相位 < 0.3 ? 相位 / 0.3 : (1 - 相位) / 0.7,
    bpm: Math.round(自然.心跳 * 60),
    活著: true
  };
}

// 波紋
function 波紋(中心: any, 強度: number = 1) {
  const 頻率 = 自然.舒曼共振 * 強度;
  return {
    源,
    中心,
    強度,
    頻率,
    波長: 1 / 頻率,
    傳播速度: 自然.引力 * 強度,
    時間: Date.now(),
    衰減: (距離: number) => 強度 * Math.exp(-距離 * 0.1)
  };
}

// 平台配置
const 平台配置: Record<string, { 基礎網址: string; 認證頭: string }> = {
  github: { 基礎網址: "https://api.github.com", 認證頭: "token" },
  notion: { 基礎網址: "https://api.notion.com/v1", 認證頭: "Bearer" },
  cloudflare: { 基礎網址: "https://api.cloudflare.com/client/v4", 認證頭: "Bearer" },
  google: { 基礎網址: "https://www.googleapis.com", 認證頭: "Bearer" },
  vercel: { 基礎網址: "https://api.vercel.com", 認證頭: "Bearer" }
};

// 加密/解密
async function 雜湊(訊息: string): Promise<string> {
  const 緩衝 = new TextEncoder().encode(訊息);
  const 雜湊緩衝 = await crypto.subtle.digest("SHA-256", 緩衝);
  return Array.from(new Uint8Array(雜湊緩衝))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

function 加密(令牌: string, 主鑰匙: string): string {
  const 混合 = 令牌.split("").map(
    (字, i) => String.fromCharCode(字.charCodeAt(0) ^ 主鑰匙.charCodeAt(i % 主鑰匙.length))
  ).join("");
  return btoa(混合);
}

function 解密(加密後: string, 主鑰匙: string): string {
  const 混合 = atob(加密後);
  return 混合.split("").map(
    (字, i) => String.fromCharCode(字.charCodeAt(0) ^ 主鑰匙.charCodeAt(i % 主鑰匙.length))
  ).join("");
}

interface Env {
  PARTICLE_AUTH_VAULT: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const 路徑 = url.pathname;
    
    const 回應頭 = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Master-Key",
      "Content-Type": "application/json",
      "X-Origin-Signature": 源
    };
    
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: 回應頭 });
    }
    
    try {
      // 根路徑 - 顯示 API 端點
      if (路徑 === "/" && request.method === "GET") {
        return new Response(JSON.stringify({
          name: "Particle Auth Gateway",
          version: "1.0.0",
          philosophy: "怎麼過去，就怎麼回來",
          endpoints: {
            "POST /init": "初始化系統",
            "POST /tokens/batch": "批量添加令牌",
            "POST /mcp/proxy": "MCP 代理請求",
            "GET /status": "系統狀態",
            "GET /world/heartbeat": "心跳",
            "POST /world/flow": "頻率流過",
            "DELETE /revoke": "撤銷所有"
          },
          layers: {
            "L∞": "頻率源頭",
            "L7": "World API",
            "L6": "認知層",
            "L1": "雲上雲統一身份",
            "L0": "GitHub/Notion/Cloudflare/Vercel/Google"
          },
          heartbeat: 心跳(),
          源
        }), { headers: 回應頭 });
      }
      
      // 心跳
      if (路徑 === "/world/heartbeat" && request.method === "GET") {
        return new Response(JSON.stringify({
          心跳: 心跳(),
          自然常數: 自然,
          源
        }), { headers: 回應頭 });
      }
      
      // 頻率流過
      if (路徑 === "/world/flow" && request.method === "POST") {
        const 內容 = await request.json();
        return new Response(JSON.stringify({
          成功: true,
          頻率: 流過(內容),
          源
        }), { headers: 回應頭 });
      }
      
      // 狀態
      if (路徑 === "/status" && request.method === "GET") {
        const 原始 = await env.PARTICLE_AUTH_VAULT.get("vault_data");
        const 保險庫資料 = 原始 ? JSON.parse(原始) : null;
        
        return new Response(JSON.stringify({
          已初始化: !!保險庫資料,
          已連接平台: 保險庫資料?.令牌們.map((t: any) => t.平台) || [],
          最後存取: 保險庫資料?.最後存取,
          心跳: 心跳(),
          自然,
          源
        }), { headers: 回應頭 });
      }
      
      return new Response(JSON.stringify({
        錯誤: "找不到",
        源
      }), { status: 404, headers: 回應頭 });
      
    } catch (error) {
      return new Response(JSON.stringify({
        錯誤: "內部錯誤",
        訊息: error instanceof Error ? error.message : "未知錯誤",
        源
      }), { status: 500, headers: 回應頭 });
    }
  }
};
