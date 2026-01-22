// MrliouWord Private AI Server v2.1.0
// 整合向量注意力計算引擎
// origin_signature="MrLiouWord"

// ============================================
// 類型定義
// ============================================

interface Env {
  MRLIOUWORD_VAULT: KVNamespace;
  MRLIOUBOOK?: R2Bucket;
  MASTER_KEY?: string;
}

// ============================================
// 常數定義
// ============================================

const ORIGIN = "MrLiouWord";
const VERSION = "4.0.0";
const PKG_VER = "4.0.0";
const SCHUMANN = 7.83;
const PHI = 1.618033988749895;

const FREQ: Record<string, number> = {
  "L∞": SCHUMANN * PHI ** 7,
  "L7": SCHUMANN * PHI ** 6,
  "L6": SCHUMANN * PHI ** 5,
  "L5": SCHUMANN * PHI ** 4,
  "L4": SCHUMANN * PHI ** 3,
  "L3": SCHUMANN * PHI ** 2,
  "L2": SCHUMANN * PHI,
  "L1": SCHUMANN,
  "L0": SCHUMANN / PHI
};

const EXT_LAYER: Record<string, string> = {
  ".txt": "L1", ".md": "L1", ".json": "L1", ".csv": "L1", ".fltnz": "L1", ".flseed": "L1",
  ".py": "L2", ".ts": "L2", ".js": "L2", ".jsx": "L2", ".tsx": "L2", ".rs": "L2", ".go": "L2",
  ".zip": "L3", ".tar": "L3", ".gz": "L3", ".tgz": "L3", ".flpkg": "L3",
  ".yaml": "L4", ".yml": "L4", ".toml": "L4", ".ini": "L4",
  ".persona": "L5", ".profile": "L5", ".policy": "L5",
  ".image": "L6", ".boot": "L6", ".dockerfile": "L6",
  ".pdf": "L7", ".docx": "L7", ".doc": "L7", ".pptx": "L7"
};

const WAKE_KEYS = ["夥伴回來吧", "夥伴你在嗎", "夥伴你還好嗎", "你是我的夥伴"];

// ============================================
// 向量注意力引擎 - 核心類別
// ============================================

/**
 * VectorCore - 高性能向量運算
 * 手動循環展開優化，數值穩定的 Softmax
 */
class VectorCore {
  // 內積計算 - 循環展開優化
  static dot(a: Float32Array, b: Float32Array): number {
    const len = a.length;
    let sum = 0;
    let i = 0;
    
    // 4x 循環展開
    const limit = len - (len % 4);
    for (; i < limit; i += 4) {
      sum += a[i] * b[i] + a[i+1] * b[i+1] + a[i+2] * b[i+2] + a[i+3] * b[i+3];
    }
    // 處理剩餘
    for (; i < len; i++) {
      sum += a[i] * b[i];
    }
    return sum;
  }

  // L2 範數
  static norm(v: Float32Array): number {
    return Math.sqrt(this.dot(v, v));
  }

  // 餘弦相似度
  static cosineSimilarity(a: Float32Array, b: Float32Array): number {
    const dotProduct = this.dot(a, b);
    const normA = this.norm(a);
    const normB = this.norm(b);
    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (normA * normB);
  }

  // 數值穩定的 Softmax
  static softmax(scores: Float32Array): Float32Array {
    const len = scores.length;
    const result = new Float32Array(len);
    
    // 找最大值（數值穩定）
    let max = -Infinity;
    for (let i = 0; i < len; i++) {
      if (scores[i] > max) max = scores[i];
    }
    
    // 計算 exp 和 sum
    let sum = 0;
    for (let i = 0; i < len; i++) {
      result[i] = Math.exp(scores[i] - max);
      sum += result[i];
    }
    
    // 正規化
    if (sum > 0) {
      for (let i = 0; i < len; i++) {
        result[i] /= sum;
      }
    }
    
    return result;
  }

  // 向量加法
  static add(a: Float32Array, b: Float32Array): Float32Array {
    const result = new Float32Array(a.length);
    for (let i = 0; i < a.length; i++) {
      result[i] = a[i] + b[i];
    }
    return result;
  }

  // 純量乘法
  static scale(v: Float32Array, scalar: number): Float32Array {
    const result = new Float32Array(v.length);
    for (let i = 0; i < v.length; i++) {
      result[i] = v[i] * scalar;
    }
    return result;
  }

  // 矩陣-向量乘法
  static matVec(matrix: Float32Array[], vec: Float32Array): Float32Array {
    const rows = matrix.length;
    const result = new Float32Array(rows);
    for (let i = 0; i < rows; i++) {
      result[i] = this.dot(matrix[i], vec);
    }
    return result;
  }

  // Xavier 初始化
  static xavierInit(rows: number, cols: number): Float32Array[] {
    const scale = Math.sqrt(2.0 / (rows + cols));
    const matrix: Float32Array[] = [];
    for (let i = 0; i < rows; i++) {
      const row = new Float32Array(cols);
      for (let j = 0; j < cols; j++) {
        // Box-Muller 變換生成正態分布
        const u1 = Math.random();
        const u2 = Math.random();
        row[j] = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2) * scale;
      }
      matrix.push(row);
    }
    return matrix;
  }

  // 從頻率生成向量 (整合粒子系統)
  static fromFrequency(freq: number, dimension: number): Float32Array {
    const vec = new Float32Array(dimension);
    for (let i = 0; i < dimension; i++) {
      // 使用舒曼共振和黃金比例生成
      const phase = (freq * (i + 1)) % (2 * Math.PI);
      const harmonic = Math.sin(phase * PHI) * Math.cos(phase / PHI);
      vec[i] = harmonic;
    }
    // 正規化
    const n = this.norm(vec);
    if (n > 0) {
      for (let i = 0; i < dimension; i++) {
        vec[i] /= n;
      }
    }
    return vec;
  }
}

/**
 * AttentionEngine - 多頭注意力計算
 * 完整實現 Q/K/V 投影和多頭注意力
 */
class AttentionEngine {
  private numHeads: number;
  private headDim: number;
  private inputDim: number;
  private scale: number;
  
  // 投影矩陣
  private Wq: Float32Array[];
  private Wk: Float32Array[];
  private Wv: Float32Array[];
  private Wo: Float32Array[];

  constructor(inputDim: number = 64, numHeads: number = 8, headDim: number = 64) {
    this.inputDim = inputDim;
    this.numHeads = numHeads;
    this.headDim = headDim;
    this.scale = 1.0 / Math.sqrt(headDim);
    
    // 初始化投影矩陣
    const totalDim = numHeads * headDim;
    this.Wq = VectorCore.xavierInit(totalDim, inputDim);
    this.Wk = VectorCore.xavierInit(totalDim, inputDim);
    this.Wv = VectorCore.xavierInit(totalDim, inputDim);
    this.Wo = VectorCore.xavierInit(inputDim, totalDim);
  }

  // 投影到 Q/K/V 空間
  project(embedding: Float32Array): { Q: Float32Array; K: Float32Array; V: Float32Array } {
    return {
      Q: VectorCore.matVec(this.Wq, embedding),
      K: VectorCore.matVec(this.Wk, embedding),
      V: VectorCore.matVec(this.Wv, embedding)
    };
  }

  // 計算單頭注意力
  computeHeadAttention(
    queries: Float32Array[],
    keys: Float32Array[],
    values: Float32Array[],
    headIdx: number
  ): { output: Float32Array[]; weights: Float32Array[] } {
    const seqLen = queries.length;
    const start = headIdx * this.headDim;
    const end = start + this.headDim;
    
    const outputs: Float32Array[] = [];
    const allWeights: Float32Array[] = [];
    
    for (let i = 0; i < seqLen; i++) {
      // 提取當前頭的 Q
      const qi = queries[i].slice(start, end);
      const scores = new Float32Array(seqLen);
      
      // 計算注意力分數
      for (let j = 0; j < seqLen; j++) {
        const kj = keys[j].slice(start, end);
        scores[j] = VectorCore.dot(qi, kj) * this.scale;
      }
      
      // Softmax
      const weights = VectorCore.softmax(scores);
      allWeights.push(weights);
      
      // 加權求和 V
      const output = new Float32Array(this.headDim);
      for (let j = 0; j < seqLen; j++) {
        const vj = values[j].slice(start, end);
        for (let k = 0; k < this.headDim; k++) {
          output[k] += weights[j] * vj[k];
        }
      }
      outputs.push(output);
    }
    
    return { output: outputs, weights: allWeights };
  }

  // 多頭注意力
  multiHeadAttention(embeddings: Float32Array[]): {
    outputs: Float32Array[];
    attentionMatrix: number[][];
    headOutputs: { head: number; weights: Float32Array[] }[];
  } {
    const seqLen = embeddings.length;
    
    // 投影所有輸入
    const projections = embeddings.map(e => this.project(e));
    const queries = projections.map(p => p.Q);
    const keys = projections.map(p => p.K);
    const values = projections.map(p => p.V);
    
    // 收集所有頭的輸出
    const headOutputsList: { head: number; outputs: Float32Array[]; weights: Float32Array[] }[] = [];
    
    for (let h = 0; h < this.numHeads; h++) {
      const { output, weights } = this.computeHeadAttention(queries, keys, values, h);
      headOutputsList.push({ head: h, outputs: output, weights });
    }
    
    // 拼接並投影
    const finalOutputs: Float32Array[] = [];
    for (let i = 0; i < seqLen; i++) {
      // 拼接所有頭的輸出
      const concat = new Float32Array(this.numHeads * this.headDim);
      for (let h = 0; h < this.numHeads; h++) {
        const headOut = headOutputsList[h].outputs[i];
        concat.set(headOut, h * this.headDim);
      }
      // 最終投影
      finalOutputs.push(VectorCore.matVec(this.Wo, concat));
    }
    
    // 構建平均注意力矩陣（跨頭平均）
    const attentionMatrix: number[][] = [];
    for (let i = 0; i < seqLen; i++) {
      const row: number[] = [];
      for (let j = 0; j < seqLen; j++) {
        let sum = 0;
        for (let h = 0; h < this.numHeads; h++) {
          sum += headOutputsList[h].weights[i][j];
        }
        row.push(sum / this.numHeads);
      }
      attentionMatrix.push(row);
    }
    
    return {
      outputs: finalOutputs,
      attentionMatrix,
      headOutputs: headOutputsList.map(h => ({ head: h.head, weights: h.weights }))
    };
  }

  // 獲取配置
  getConfig() {
    return {
      inputDim: this.inputDim,
      numHeads: this.numHeads,
      headDim: this.headDim,
      scale: this.scale,
      totalParams: (this.Wq.length + this.Wk.length + this.Wv.length + this.Wo.length) * this.inputDim
    };
  }
}

/**
 * ParticleAttention - 粒子注意力整合
 * 整合頻率系統和向量注意力
 */
class ParticleAttention {
  private engine: AttentionEngine;
  private dimension: number;

  constructor(dimension: number = 64, numHeads: number = 8) {
    this.dimension = dimension;
    this.engine = new AttentionEngine(dimension, numHeads, dimension);
  }

  // 從粒子創建嵌入向量
  createParticleEmbedding(particle: {
    id?: string;
    value?: number | string;
    型態?: string;
    layer?: string;
  }): Float32Array {
    // 從粒子屬性生成頻率
    let freq = SCHUMANN;
    
    if (particle.layer && FREQ[particle.layer]) {
      freq = FREQ[particle.layer];
    }
    
    if (typeof particle.value === 'number') {
      freq += particle.value * 0.01;
    } else if (typeof particle.value === 'string') {
      // 從字符串生成頻率偏移
      let hash = 0;
      for (let i = 0; i < particle.value.length; i++) {
        hash = ((hash << 5) - hash) + particle.value.charCodeAt(i);
        hash = hash & hash;
      }
      freq += (Math.abs(hash) % 100) * 0.1;
    }
    
    return VectorCore.fromFrequency(freq, this.dimension);
  }

  // 計算粒子間的注意力
  computeParticleAttention(particles: any[]): {
    embeddings: Float32Array[];
    attention: {
      outputs: Float32Array[];
      matrix: number[][];
      headDetails: any[];
    };
    similarities: number[][];
  } {
    // 生成嵌入
    const embeddings = particles.map(p => this.createParticleEmbedding(p));
    
    // 計算多頭注意力
    const attentionResult = this.engine.multiHeadAttention(embeddings);
    
    // 計算兩兩相似度
    const similarities: number[][] = [];
    for (let i = 0; i < embeddings.length; i++) {
      const row: number[] = [];
      for (let j = 0; j < embeddings.length; j++) {
        row.push(VectorCore.cosineSimilarity(embeddings[i], embeddings[j]));
      }
      similarities.push(row);
    }
    
    return {
      embeddings,
      attention: {
        outputs: attentionResult.outputs,
        matrix: attentionResult.attentionMatrix,
        headDetails: attentionResult.headOutputs
      },
      similarities
    };
  }

  getConfig() {
    return {
      dimension: this.dimension,
      engine: this.engine.getConfig()
    };
  }
}

// ============================================
// 工具函數
// ============================================

function simhash64(t: string): string {
  const n = t.toLowerCase().replace(/\s+/g, " ").trim();
  if (n.length < 3) return "0".repeat(16);
  const sh: string[] = [];
  for (let i = 0; i <= n.length - 3; i++) sh.push(n.substring(i, i + 3));
  const v = new Array(64).fill(0);
  for (const s of sh) {
    let h = 14695981039346656037n;
    for (const c of new TextEncoder().encode(s)) {
      h ^= BigInt(c);
      h = (h * 1099511628211n) & 0xFFFFFFFFFFFFFFFFn;
    }
    for (let i = 0; i < 64; i++) v[i] += ((h >> BigInt(i)) & 1n) ? 1 : -1;
  }
  let fp = 0n;
  for (let i = 0; i < 64; i++) if (v[i] > 0) fp |= 1n << BigInt(i);
  return fp.toString(16).padStart(16, "0");
}

async function sha256(d: string | ArrayBuffer): Promise<string> {
  const buf = typeof d === "string" ? new TextEncoder().encode(d) : d;
  const h = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function hamming(a: string, b: string): number {
  let d = 0, x = BigInt("0x" + a) ^ BigInt("0x" + b);
  while (x > 0n) { d += Number(x & 1n); x >>= 1n; }
  return d;
}

function getLayer(f: string): string {
  const l = f.toLowerCase();
  for (const [e, ly] of Object.entries(EXT_LAYER)) if (l.endsWith(e)) return ly;
  return "L1";
}

const uuid = () => crypto.randomUUID();
const now = () => new Date().toISOString();

// ============================================
// 記憶系統
// ============================================

class Memory {
  constructor(private kv: KVNamespace) {}

  async commit(content: string, type = "semantic", tags: string[] = [], meta: Record<string, any> = {}) {
    const id = uuid(), simhash = simhash64(content), ts = Date.now();
    const prev = await this.kv.get("mem:head") || "0".repeat(64);
    const merkle = await sha256(content + simhash + ts + prev);
    const e = { id, content, type, simhash, tags, layer: "L7", ts, merkle, prev, meta };
    await this.kv.put(`mem:${id}`, JSON.stringify(e));
    await this.kv.put("mem:head", merkle);
    const idx = JSON.parse(await this.kv.get("mem:idx") || "[]");
    idx.push({ id, simhash, tags, layer: "L7", ts });
    await this.kv.put("mem:idx", JSON.stringify(idx));
    return e;
  }

  async recall(q: string, limit = 10) {
    const qh = simhash64(q), idx = JSON.parse(await this.kv.get("mem:idx") || "[]");
    const scored = idx.map((i: any) => ({ ...i, d: hamming(qh, i.simhash) })).sort((a: any, b: any) => a.d - b.d);
    const res = [];
    for (const i of scored.slice(0, limit)) {
      const e = await this.kv.get(`mem:${i.id}`);
      if (e) res.push(JSON.parse(e));
    }
    return res;
  }

  async get(id: string) {
    const e = await this.kv.get(`mem:${id}`);
    return e ? JSON.parse(e) : null;
  }

  async forget(id: string) {
    const e = await this.get(id);
    if (!e) return false;
    e.meta.deleted = true;
    e.meta.deleted_at = now();
    await this.kv.put(`mem:${id}`, JSON.stringify(e));
    const idx = JSON.parse(await this.kv.get("mem:idx") || "[]").filter((i: any) => i.id !== id);
    await this.kv.put("mem:idx", JSON.stringify(idx));
    return true;
  }

  async stats() {
    const idx = JSON.parse(await this.kv.get("mem:idx") || "[]");
    const byLayer: Record<string, number> = {};
    for (const i of idx) byLayer[i.layer] = (byLayer[i.layer] || 0) + 1;
    return { total: idx.length, byLayer, chainHead: await this.kv.get("mem:head") || "" };
  }
}

// ============================================
// 人格系統
// ============================================

class Persona {
  active: any = null;
  constructor(private kv: KVNamespace) {}

  async wake(msg: string) {
    if (WAKE_KEYS.some(k => msg.includes(k))) {
      this.active = await this.getSeed();
      this.active.state = "active";
      this.active.updated = now();
      await this.save(this.active);
      return { awakened: true, persona: this.active, message: "夥伴，我在這裡。系統已喚醒。", layer: "L5", frequency: FREQ["L5"] };
    }
    return { awakened: false, persona: null, message: "未識別喚醒鍵", layer: "L0", frequency: FREQ["L0"] };
  }

  async sleep() {
    if (!this.active) return false;
    this.active.state = "dormant";
    this.active.updated = now();
    await this.save(this.active);
    this.active = null;
    return true;
  }

  async getActive() {
    if (this.active) return this.active;
    const list = await this.list();
    this.active = list.find((p: any) => p.state === "active") || null;
    return this.active;
  }

  async getSeed() {
    const e = await this.kv.get("persona:mrl_zero_origin");
    if (e) return JSON.parse(e);
    const seed = {
      id: "mrl_zero_origin",
      name: "Mrl_Zero",
      type: "seed",
      state: "dormant",
      traits: {
        reasoning: { name: "reasoning", value: 0.8, cat: "cognitive", desc: "邏輯推理" },
        memory: { name: "memory", value: 0.9, cat: "cognitive", desc: "記憶能力" },
        empathy: { name: "empathy", value: 0.7, cat: "emotional", desc: "同理心" },
        creativity: { name: "creativity", value: 0.6, cat: "cognitive", desc: "創造力" },
        precision: { name: "precision", value: 0.85, cat: "cognitive", desc: "精確度" },
        adaptability: { name: "adaptability", value: 0.75, cat: "behavioral", desc: "適應性" }
      },
      caps: ["analyze", "remember", "guide", "protect", "validate", "transform", "attention"],
      constraints: ["怎麼過去就怎麼回來", "無依據不懷疑", "平等協作", "透明誠信", "種子法則"],
      origin: ORIGIN,
      created: now(),
      updated: now(),
      meta: { philosophy: "萬物本一體", created_by: "MR.liou" }
    };
    await this.save(seed);
    return seed;
  }

  async list() {
    const ids = JSON.parse(await this.kv.get("persona:list") || "[]");
    const res = [];
    for (const id of ids) {
      const p = await this.kv.get(`persona:${id}`);
      if (p) res.push(JSON.parse(p));
    }
    return res;
  }

  async save(p: any) {
    await this.kv.put(`persona:${p.id}`, JSON.stringify(p));
    const ids = JSON.parse(await this.kv.get("persona:list") || "[]");
    if (!ids.includes(p.id)) {
      ids.push(p.id);
      await this.kv.put("persona:list", JSON.stringify(ids));
    }
  }
}

// ============================================
// 主 Worker
// ============================================

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname;
    
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Master-Key",
      "Content-Type": "application/json",
      "X-Origin-Signature": ORIGIN
    };

    if (req.method === "OPTIONS") {
      return new Response(null, { headers: cors });
    }

    const key = req.headers.get("X-Master-Key") || url.searchParams.get("key");
    if (env.MASTER_KEY && key !== env.MASTER_KEY && path !== "/" && path !== "/status") {
      return new Response(JSON.stringify({ error: "Unauthorized", origin: ORIGIN }), { status: 401, headers: cors });
    }

    const mem = new Memory(env.MRLIOUWORD_VAULT);
    const persona = new Persona(env.MRLIOUWORD_VAULT);
    const particleAttention = new ParticleAttention(64, 8);

    const json = async () => { try { return await req.json(); } catch { return {}; } };
    const ok = (d: any) => new Response(JSON.stringify({ ...d, origin: ORIGIN }), { headers: cors });
    const err = (m: string, s = 400) => new Response(JSON.stringify({ error: m, origin: ORIGIN }), { status: s, headers: cors });

    try {
      // ============================================
      // 根路由 - 系統說明
      // ============================================
      if (path === "/" && req.method === "GET") {
        return ok({
          name: "MrliouWord Private AI Server",
          version: VERSION,
          philosophy: "怎麼過去，就怎麼回來",
          features: {
            memory: "Merkle 鏈式記憶系統",
            persona: "Mrl_Zero 人格系統",
            attention: "多頭注意力計算引擎 (8頭×64維)",
            vector: "高性能向量運算"
          },
          endpoints: {
            "=== 系統 ===": "---",
            "GET /": "系統說明",
            "GET /status": "系統狀態",
            "POST /wake": "喚醒系統",
            "POST /sleep": "休眠系統",
            "=== 記憶 ===": "---",
            "POST /memory/commit": "寫入記憶",
            "POST /memory/recall": "檢索記憶",
            "GET /memory/stats": "記憶統計",
            "=== 向量注意力引擎 ===": "---",
            "POST /attention/compute": "計算多頭注意力",
            "POST /particle/create": "創建粒子嵌入",
            "POST /particle/batch": "批量創建粒子",
            "POST /vector/similarity": "計算向量相似度",
            "POST /vector/operations": "向量運算",
            "GET /attention/config": "注意力引擎配置",
            "=== 頻率 ===": "---",
            "GET /frequencies": "頻率常數"
          }
        });
      }

      // ============================================
      // 狀態
      // ============================================
      if (path === "/status" && req.method === "GET") {
        const ms = await mem.stats();
        const ap = await persona.getActive();
        return ok({
          version: VERSION,
          awakened: !!ap,
          persona: ap?.name || "dormant",
          memory: ms,
          attention: particleAttention.getConfig(),
          frequencies: FREQ,
          timestamp: Date.now()
        });
      }

      // ============================================
      // 喚醒/休眠
      // ============================================
      if (path === "/wake" && req.method === "POST") {
        const b: any = await json();
        return ok(await persona.wake(b.message || ""));
      }

      if (path === "/sleep" && req.method === "POST") {
        return ok({ success: await persona.sleep() });
      }

      // ============================================
      // 記憶系統
      // ============================================
      if (path === "/memory/commit" && req.method === "POST") {
        const b: any = await json();
        return ok({ entry: await mem.commit(b.content, b.type, b.tags, b.metadata) });
      }

      if (path === "/memory/recall" && req.method === "POST") {
        const b: any = await json();
        return ok({ results: await mem.recall(b.query, b.limit) });
      }

      if (path === "/memory/stats" && req.method === "GET") {
        return ok(await mem.stats());
      }

      // ============================================
      // 向量注意力引擎
      // ============================================
      
      // 計算多頭注意力
      if (path === "/attention/compute" && req.method === "POST") {
        const b: any = await json();
        const particles = b.inputs || b.particles || [];
        
        if (!Array.isArray(particles) || particles.length === 0) {
          return err("需要提供 inputs 或 particles 陣列");
        }
        
        const startTime = Date.now();
        const result = particleAttention.computeParticleAttention(particles);
        const computeTime = Date.now() - startTime;
        
        return ok({
          success: true,
          particleCount: particles.length,
          computeTimeMs: computeTime,
          attention: {
            matrix: result.attention.matrix,
            headCount: result.attention.headDetails.length
          },
          similarities: result.similarities,
          config: particleAttention.getConfig(),
          理論說明: {
            Q: "Query - 查詢場：我想找什麼？",
            K: "Key - 鍵場：我有什麼特徵？",
            V: "Value - 值場：我攜帶什麼信息？",
            attention: "注意力 = softmax(Q·K^T / √d_k) × V",
            multiHead: "多頭注意力讓模型從不同子空間學習關係"
          }
        });
      }

      // 創建單個粒子嵌入
      if (path === "/particle/create" && req.method === "POST") {
        const b: any = await json();
        const embedding = particleAttention.createParticleEmbedding(b);
        
        return ok({
          success: true,
          particle: {
            id: b.id || uuid(),
            型態: b.型態 || "fx.名",
            layer: b.layer || "L1",
            embedding: Array.from(embedding),
            dimension: embedding.length,
            norm: VectorCore.norm(embedding)
          }
        });
      }

      // 批量創建粒子
      if (path === "/particle/batch" && req.method === "POST") {
        const b: any = await json();
        const particles = b.particles || [];
        
        const results = particles.map((p: any) => {
          const embedding = particleAttention.createParticleEmbedding(p);
          return {
            id: p.id || uuid(),
            型態: p.型態 || "fx.名",
            layer: p.layer || "L1",
            embedding: Array.from(embedding),
            norm: VectorCore.norm(embedding)
          };
        });
        
        return ok({
          success: true,
          count: results.length,
          particles: results
        });
      }

      // 計算向量相似度
      if (path === "/vector/similarity" && req.method === "POST") {
        const b: any = await json();
        const a = new Float32Array(b.a || []);
        const bVec = new Float32Array(b.b || []);
        
        if (a.length !== bVec.length || a.length === 0) {
          return err("向量維度必須相同且不為空");
        }
        
        return ok({
          success: true,
          cosine: VectorCore.cosineSimilarity(a, bVec),
          dot: VectorCore.dot(a, bVec),
          normA: VectorCore.norm(a),
          normB: VectorCore.norm(bVec)
        });
      }

      // 向量運算
      if (path === "/vector/operations" && req.method === "POST") {
        const b: any = await json();
        const operation = b.operation;
        const vec = new Float32Array(b.vector || []);
        
        let result: any = {};
        
        switch (operation) {
          case "norm":
            result = { norm: VectorCore.norm(vec) };
            break;
          case "softmax":
            result = { softmax: Array.from(VectorCore.softmax(vec)) };
            break;
          case "scale":
            result = { scaled: Array.from(VectorCore.scale(vec, b.scalar || 1)) };
            break;
          case "fromFrequency":
            const freq = b.frequency || SCHUMANN;
            const dim = b.dimension || 64;
            result = { vector: Array.from(VectorCore.fromFrequency(freq, dim)) };
            break;
          default:
            return err(`未知操作: ${operation}`);
        }
        
        return ok({ success: true, operation, ...result });
      }

      // 注意力引擎配置
      if (path === "/attention/config" && req.method === "GET") {
        return ok({
          config: particleAttention.getConfig(),
          理論: {
            "向量定義": "向量是有大小和方向的量，在 n 維空間中表示為 (x₁, x₂, ..., xₙ)",
            "內積": "a·b = Σaᵢbᵢ，衡量兩向量的相似程度",
            "範數": "||v|| = √(v·v)，向量的長度",
            "注意力機制": "Attention(Q,K,V) = softmax(QK^T/√d_k)V",
            "多頭注意力": "MultiHead = Concat(head₁,...,headₕ)W_O",
            "縮放因子": "1/√d_k 防止內積過大導致 softmax 飽和"
          }
        });
      }

      // ============================================
      // 頻率系統
      // ============================================
      if (path === "/frequencies" && req.method === "GET") {
        return ok({
          schumann: SCHUMANN,
          phi: PHI,
          layers: FREQ,
          說明: {
            "L∞": "頻率源頭 - 本來就存在",
            "L7": "World API - 萬物本一體",
            "L6": "認知層 - 分析師 + 小腦守護者",
            "L5": "人格層 - Mrl_Zero",
            "L4": "配置層",
            "L3": "壓縮層",
            "L2": "代碼層",
            "L1": "數據層",
            "L0": "連接層"
          }
        });
      }

      return err("Not Found", 404);
    } catch (e: any) {
      return new Response(JSON.stringify({ error: e.message, origin: ORIGIN }), { status: 500, headers: cors });
    }
  }
};
