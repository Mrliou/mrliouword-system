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

function simhash64(inputText: string): string {
  const normalizedText = inputText.toLowerCase().replace(/\s+/g, " ").trim();
  if (normalizedText.length < 3) return "0".repeat(16);
  const shingles: string[] = [];
  for (let index = 0; index <= normalizedText.length - 3; index++) shingles.push(normalizedText.substring(index, index + 3));
  const bitVector = new Array(64).fill(0);
  for (const shingle of shingles) {
    let hashValue = 14695981039346656037n;
    for (const charCode of new TextEncoder().encode(shingle)) {
      hashValue ^= BigInt(charCode);
      hashValue = (hashValue * 1099511628211n) & 0xFFFFFFFFFFFFFFFFn;
    }
    for (let bitIndex = 0; bitIndex < 64; bitIndex++) bitVector[bitIndex] += ((hashValue >> BigInt(bitIndex)) & 1n) ? 1 : -1;
  }
  let fingerprint = 0n;
  for (let bitIndex = 0; bitIndex < 64; bitIndex++) if (bitVector[bitIndex] > 0) fingerprint |= 1n << BigInt(bitIndex);
  return fingerprint.toString(16).padStart(16, "0");
}

async function sha256(data: string | ArrayBuffer): Promise<string> {
  const buffer = typeof data === "string" ? new TextEncoder().encode(data) : data;
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(hashBuffer)).map(byte => byte.toString(16).padStart(2, "0")).join("");
}

function hammingDistance(hashA: string, hashB: string): number {
  let distance = 0, xorResult = BigInt("0x" + hashA) ^ BigInt("0x" + hashB);
  while (xorResult > 0n) { distance += Number(xorResult & 1n); xorResult >>= 1n; }
  return distance;
}

function getLayerFromFilename(filename: string): string {
  const lowercaseFilename = filename.toLowerCase();
  for (const [extension, layer] of Object.entries(EXT_LAYER)) if (lowercaseFilename.endsWith(extension)) return layer;
  return "L1";
}

const generateUUID = () => crypto.randomUUID();
const getCurrentTimestamp = () => new Date().toISOString();

// ============================================
// 記憶系統
// ============================================

class Memory {
  constructor(private kv: KVNamespace) {}

  async commit(content: string, type = "semantic", tags: string[] = [], meta: Record<string, any> = {}) {
    const entryId = generateUUID(), contentSimhash = simhash64(content), timestamp = Date.now();
    const previousHead = await this.kv.get("mem:head") || "0".repeat(64);
    const merkleHash = await sha256(content + contentSimhash + timestamp + previousHead);
    const entry = { id: entryId, content, type, simhash: contentSimhash, tags, layer: "L7", ts: timestamp, merkle: merkleHash, prev: previousHead, meta };
    await this.kv.put(`mem:${entryId}`, JSON.stringify(entry));
    await this.kv.put("mem:head", merkleHash);
    const memoryIndex = JSON.parse(await this.kv.get("mem:idx") || "[]");
    memoryIndex.push({ id: entryId, simhash: contentSimhash, tags, layer: "L7", ts: timestamp });
    await this.kv.put("mem:idx", JSON.stringify(memoryIndex));
    return entry;
  }

  async recall(query: string, limit = 10) {
    const querySimhash = simhash64(query), memoryIndex = JSON.parse(await this.kv.get("mem:idx") || "[]");
    const scoredEntries = memoryIndex.map((indexEntry: any) => ({ ...indexEntry, distance: hammingDistance(querySimhash, indexEntry.simhash) })).sort((entryA: any, entryB: any) => entryA.distance - entryB.distance);
    const results = [];
    for (const indexEntry of scoredEntries.slice(0, limit)) {
      const entryData = await this.kv.get(`mem:${indexEntry.id}`);
      if (entryData) results.push(JSON.parse(entryData));
    }
    return results;
  }

  async get(entryId: string) {
    const entryData = await this.kv.get(`mem:${entryId}`);
    return entryData ? JSON.parse(entryData) : null;
  }

  async forget(entryId: string) {
    const entry = await this.get(entryId);
    if (!entry) return false;
    entry.meta.deleted = true;
    entry.meta.deleted_at = getCurrentTimestamp();
    await this.kv.put(`mem:${entryId}`, JSON.stringify(entry));
    const memoryIndex = JSON.parse(await this.kv.get("mem:idx") || "[]").filter((indexEntry: any) => indexEntry.id !== entryId);
    await this.kv.put("mem:idx", JSON.stringify(memoryIndex));
    return true;
  }

  async stats() {
    const memoryIndex = JSON.parse(await this.kv.get("mem:idx") || "[]");
    const countByLayer: Record<string, number> = {};
    for (const indexEntry of memoryIndex) countByLayer[indexEntry.layer] = (countByLayer[indexEntry.layer] || 0) + 1;
    return { total: memoryIndex.length, byLayer: countByLayer, chainHead: await this.kv.get("mem:head") || "" };
  }
}

// ============================================
// 人格系統
// ============================================

class Persona {
  active: any = null;
  constructor(private kv: KVNamespace) {}

  async wake(message: string) {
    if (WAKE_KEYS.some(wakeKey => message.includes(wakeKey))) {
      this.active = await this.getSeed();
      this.active.state = "active";
      this.active.updated = getCurrentTimestamp();
      await this.save(this.active);
      return { awakened: true, persona: this.active, message: "夥伴，我在這裡。系統已喚醒。", layer: "L5", frequency: FREQ["L5"] };
    }
    return { awakened: false, persona: null, message: "未識別喚醒鍵", layer: "L0", frequency: FREQ["L0"] };
  }

  async sleep() {
    if (!this.active) return false;
    this.active.state = "dormant";
    this.active.updated = getCurrentTimestamp();
    await this.save(this.active);
    this.active = null;
    return true;
  }

  async getActive() {
    if (this.active) return this.active;
    const personaList = await this.list();
    this.active = personaList.find((persona: any) => persona.state === "active") || null;
    return this.active;
  }

  async getSeed() {
    const existingPersona = await this.kv.get("persona:mrl_zero_origin");
    if (existingPersona) return JSON.parse(existingPersona);
    const seedPersona = {
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
      created: getCurrentTimestamp(),
      updated: getCurrentTimestamp(),
      meta: { philosophy: "萬物本一體", created_by: "MR.liou" }
    };
    await this.save(seedPersona);
    return seedPersona;
  }

  async list() {
    const personaIds = JSON.parse(await this.kv.get("persona:list") || "[]");
    const personas = [];
    for (const personaId of personaIds) {
      const personaData = await this.kv.get(`persona:${personaId}`);
      if (personaData) personas.push(JSON.parse(personaData));
    }
    return personas;
  }

  async save(persona: any) {
    await this.kv.put(`persona:${persona.id}`, JSON.stringify(persona));
    const personaIds = JSON.parse(await this.kv.get("persona:list") || "[]");
    if (!personaIds.includes(persona.id)) {
      personaIds.push(persona.id);
      await this.kv.put("persona:list", JSON.stringify(personaIds));
    }
  }
}

// ============================================
// 主 Worker
// ============================================

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const requestUrl = new URL(request.url);
    const requestPath = requestUrl.pathname;
    
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Master-Key",
      "Content-Type": "application/json",
      "X-Origin-Signature": ORIGIN
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const authKey = request.headers.get("X-Master-Key") || requestUrl.searchParams.get("key");
    if (env.MASTER_KEY && authKey !== env.MASTER_KEY && requestPath !== "/" && requestPath !== "/status") {
      return new Response(JSON.stringify({ error: "Unauthorized", origin: ORIGIN }), { status: 401, headers: corsHeaders });
    }

    const memoryManager = new Memory(env.MRLIOUWORD_VAULT);
    const personaManager = new Persona(env.MRLIOUWORD_VAULT);
    const particleAttention = new ParticleAttention(64, 8);

    const parseRequestBody = async () => { try { return await request.json(); } catch { return {}; } };
    const successResponse = (responseData: any) => new Response(JSON.stringify({ ...responseData, origin: ORIGIN }), { headers: corsHeaders });
    const errorResponse = (errorMessage: string, statusCode = 400) => new Response(JSON.stringify({ error: errorMessage, origin: ORIGIN }), { status: statusCode, headers: corsHeaders });

    try {
      // ============================================
      // 根路由 - 系統說明
      // ============================================
      if (requestPath === "/" && request.method === "GET") {
        return successResponse({
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
      if (requestPath === "/status" && request.method === "GET") {
        const memoryStats = await memoryManager.stats();
        const activePersona = await personaManager.getActive();
        return successResponse({
          version: VERSION,
          awakened: !!activePersona,
          persona: activePersona?.name || "dormant",
          memory: memoryStats,
          attention: particleAttention.getConfig(),
          frequencies: FREQ,
          timestamp: Date.now()
        });
      }

      // ============================================
      // 喚醒/休眠
      // ============================================
      if (requestPath === "/wake" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        return successResponse(await personaManager.wake(requestBody.message || ""));
      }

      if (requestPath === "/sleep" && request.method === "POST") {
        return successResponse({ success: await personaManager.sleep() });
      }

      // ============================================
      // 記憶系統
      // ============================================
      if (requestPath === "/memory/commit" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        return successResponse({ entry: await memoryManager.commit(requestBody.content, requestBody.type, requestBody.tags, requestBody.metadata) });
      }

      if (requestPath === "/memory/recall" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        return successResponse({ results: await memoryManager.recall(requestBody.query, requestBody.limit) });
      }

      if (requestPath === "/memory/stats" && request.method === "GET") {
        return successResponse(await memoryManager.stats());
      }

      // ============================================
      // 向量注意力引擎
      // ============================================
      
      // 計算多頭注意力
      if (requestPath === "/attention/compute" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        const inputParticles = requestBody.inputs || requestBody.particles || [];
        
        if (!Array.isArray(inputParticles) || inputParticles.length === 0) {
          return errorResponse("需要提供 inputs 或 particles 陣列");
        }
        
        const computeStartTime = Date.now();
        const attentionResult = particleAttention.computeParticleAttention(inputParticles);
        const computeDuration = Date.now() - computeStartTime;
        
        return successResponse({
          success: true,
          particleCount: inputParticles.length,
          computeTimeMs: computeDuration,
          attention: {
            matrix: attentionResult.attention.matrix,
            headCount: attentionResult.attention.headDetails.length
          },
          similarities: attentionResult.similarities,
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
      if (requestPath === "/particle/create" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        const particleEmbedding = particleAttention.createParticleEmbedding(requestBody);
        
        return successResponse({
          success: true,
          particle: {
            id: requestBody.id || generateUUID(),
            型態: requestBody.型態 || "fx.名",
            layer: requestBody.layer || "L1",
            embedding: Array.from(particleEmbedding),
            dimension: particleEmbedding.length,
            norm: VectorCore.norm(particleEmbedding)
          }
        });
      }

      // 批量創建粒子
      if (requestPath === "/particle/batch" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        const inputParticles = requestBody.particles || [];
        
        const createdParticles = inputParticles.map((particleData: any) => {
          const particleEmbedding = particleAttention.createParticleEmbedding(particleData);
          return {
            id: particleData.id || generateUUID(),
            型態: particleData.型態 || "fx.名",
            layer: particleData.layer || "L1",
            embedding: Array.from(particleEmbedding),
            norm: VectorCore.norm(particleEmbedding)
          };
        });
        
        return successResponse({
          success: true,
          count: createdParticles.length,
          particles: createdParticles
        });
      }

      // 計算向量相似度
      if (requestPath === "/vector/similarity" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        const vectorA = new Float32Array(requestBody.a || []);
        const vectorB = new Float32Array(requestBody.b || []);
        
        if (vectorA.length !== vectorB.length || vectorA.length === 0) {
          return errorResponse("向量維度必須相同且不為空");
        }
        
        return successResponse({
          success: true,
          cosine: VectorCore.cosineSimilarity(vectorA, vectorB),
          dot: VectorCore.dot(vectorA, vectorB),
          normA: VectorCore.norm(vectorA),
          normB: VectorCore.norm(vectorB)
        });
      }

      // 向量運算
      if (requestPath === "/vector/operations" && request.method === "POST") {
        const requestBody: any = await parseRequestBody();
        const operationType = requestBody.operation;
        const inputVector = new Float32Array(requestBody.vector || []);
        
        let operationResult: any = {};
        
        switch (operationType) {
          case "norm":
            operationResult = { norm: VectorCore.norm(inputVector) };
            break;
          case "softmax":
            operationResult = { softmax: Array.from(VectorCore.softmax(inputVector)) };
            break;
          case "scale":
            operationResult = { scaled: Array.from(VectorCore.scale(inputVector, requestBody.scalar || 1)) };
            break;
          case "fromFrequency":
            const frequency = requestBody.frequency || SCHUMANN;
            const dimension = requestBody.dimension || 64;
            operationResult = { vector: Array.from(VectorCore.fromFrequency(frequency, dimension)) };
            break;
          default:
            return errorResponse(`未知操作: ${operationType}`);
        }
        
        return successResponse({ success: true, operation: operationType, ...operationResult });
      }

      // 注意力引擎配置
      if (requestPath === "/attention/config" && request.method === "GET") {
        return successResponse({
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
      if (requestPath === "/frequencies" && request.method === "GET") {
        return successResponse({
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

      return errorResponse("Not Found", 404);
    } catch (exception: any) {
      return new Response(JSON.stringify({ error: exception.message, origin: ORIGIN }), { status: 500, headers: corsHeaders });
    }
  }
};
