/* mrliou_particle_plugin_runtime_v0.2_pack.ts
 * origin_signature: MrLiouWord
 * single-file closure: runtime + plugin pack exporter (GitHub/Cloudflare deployable bundle)
 */

import crypto from "crypto";
import fs from "fs";
import path from "path";

/* ----------------------------- Types & Contracts ---------------------------- */

type JSONValue =
  | string
  | number
  | boolean
  | null
  | { [k: string]: JSONValue }
  | JSONValue[];

export type Dict<T = JSONValue> = Record<string, T>;

export type ExecAdapterType = "local" | "edge" | "cloud";
export type AuthMode = "internal" | "scoped" | "public" | "deny";

export interface ParticleIOContract {
  input: Dict<string>;
  output: Dict<string>;
}

export interface ParticleStateModel {
  type: string;
  persist: boolean;
}

export interface ParticleExecAdapter {
  type: ExecAdapterType;
  entry: string;
}

export interface ParticlePolicyGate {
  rate_limit?: string; // "10/s"
  auth: AuthMode;
  allow_roles?: string[];
  deny_roles?: string[];
}

export interface ParticleTraceHook {
  emit: string[];
}

export interface ParticleManifest {
  particle_id: string;
  role_binding: string[];
  capability: string;
  io_contract: ParticleIOContract;
  state_model: ParticleStateModel;
  exec_adapter: ParticleExecAdapter;
  policy_gate: ParticlePolicyGate;
  trace_hook: ParticleTraceHook;
  version?: string;
  origin_signature?: string;
  created_at?: string;
}

export interface TraceEnvelope {
  event_id: string;
  rid: string;
  tick: number;
  persona_id: string;
  merkle_root: string;
  particle_id: string;
  event: string;
  ts: number;
  payload: Dict;
}

export interface ParticleContext {
  rid: string;
  tick: number;
  persona_id: string;
  now: number;

  world: Dict;
  memory: MemoryBus;
  trace: TraceBus;

  caller_role: string;
  auth_token?: string;

  merkle: MerkleFold;
}

export interface ParticleInvokePacket {
  particle_id: string;
  input: Dict;
  intent?: string;
}

export interface ParticleInvokeResult {
  ok: boolean;
  output?: Dict;
  error?: string;
  trace_merkle_root: string;
}

/* ------------------------------ Utils: Hashes ------------------------------ */

function sha256Hex(s: string): string {
  return crypto.createHash("sha256").update(s).digest("hex");
}

function stableStringify(v: any): string {
  const seen = new WeakSet();
  const sorter = (obj: any): any => {
    if (obj === null || typeof obj !== "object") return obj;
    if (seen.has(obj)) return "[Circular]";
    seen.add(obj);
    if (Array.isArray(obj)) return obj.map(sorter);
    const keys = Object.keys(obj).sort();
    const out: any = {};
    for (const k of keys) out[k] = sorter(obj[k]);
    return out;
  };
  return JSON.stringify(sorter(v));
}

function parseRateLimit(spec?: string): { n: number; perMs: number } | null {
  if (!spec) return null;
  const m = spec.trim().match(/^(\d+)\s*\/\s*([smh])$/i);
  if (!m) return null;
  const n = Number(m[1]);
  const unit = m[2].toLowerCase();
  const perMs = unit === "s" ? 1000 : unit === "m" ? 60000 : 3600000;
  return { n, perMs };
}

function newId(prefix: string): string {
  return `${prefix}_${crypto.randomBytes(8).toString("hex")}`;
}

function ensureDir(p: string) {
  fs.mkdirSync(p, { recursive: true });
}

function writeFileAtomic(filePath: string, content: string | Buffer) {
  ensureDir(path.dirname(filePath));
  const tmp = `${filePath}.tmp_${crypto.randomBytes(4).toString("hex")}`;
  fs.writeFileSync(tmp, content);
  fs.renameSync(tmp, filePath);
}

function listFilesRec(root: string): string[] {
  const out: string[] = [];
  const walk = (dir: string) => {
    for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, ent.name);
      if (ent.isDirectory()) walk(p);
      else if (ent.isFile()) out.push(p);
    }
  };
  walk(root);
  return out.sort();
}

/* ------------------------------ Trace / Merkle ----------------------------- */

export class MerkleFold {
  private leaves: string[] = [];
  private root: string = sha256Hex("mrliou_merkle_root_init");

  addLeaf(data: Dict): string {
    const leaf = sha256Hex(stableStringify(data));
    this.leaves.push(leaf);
    this.root = sha256Hex(this.root + leaf);
    return leaf;
  }

  getRoot(): string {
    return this.root;
  }

  getLeaves(): string[] {
    return [...this.leaves];
  }
}

export class TraceBus {
  private events: TraceEnvelope[] = [];
  emit(env: TraceEnvelope) {
    this.events.push(env);
  }
  list(): TraceEnvelope[] {
    return [...this.events];
  }
}

export class MemoryBus {
  private kv: Map<string, Dict> = new Map();
  put(key: string, value: Dict) {
    this.kv.set(key, value);
  }
  get(key: string): Dict | undefined {
    return this.kv.get(key);
  }
  has(key: string): boolean {
    return this.kv.has(key);
  }
}

/* ------------------------------ Policy / Rate ------------------------------ */

class RateLimiter {
  private buckets = new Map<string, { windowStart: number; count: number }>();

  allow(key: string, spec?: string, now = Date.now()): boolean {
    const conf = parseRateLimit(spec);
    if (!conf) return true;
    const b = this.buckets.get(key);
    if (!b) {
      this.buckets.set(key, { windowStart: now, count: 1 });
      return true;
    }
    if (now - b.windowStart >= conf.perMs) {
      b.windowStart = now;
      b.count = 1;
      return true;
    }
    if (b.count < conf.n) {
      b.count += 1;
      return true;
    }
    return false;
  }
}

/* ------------------------------- Plugin API -------------------------------- */

export interface ParticlePlugin {
  manifest: ParticleManifest;
  execute(entry: string, ctx: ParticleContext, input: Dict): Promise<Dict> | Dict;
}

export class ParticleRegistry {
  private plugins = new Map<string, ParticlePlugin>();

  register(plugin: ParticlePlugin) {
    validateManifest(plugin.manifest);
    const id = plugin.manifest.particle_id;
    if (this.plugins.has(id)) throw new Error(`Particle already registered: ${id}`);
    this.plugins.set(id, plugin);
  }

  get(particle_id: string): ParticlePlugin | undefined {
    return this.plugins.get(particle_id);
  }

  list(): ParticleManifest[] {
    return [...this.plugins.values()].map((p) => p.manifest);
  }
}

function validateManifest(m: ParticleManifest) {
  const required = [
    "particle_id",
    "role_binding",
    "capability",
    "io_contract",
    "state_model",
    "exec_adapter",
    "policy_gate",
    "trace_hook",
  ];
  for (const k of required) {
    if ((m as any)[k] === undefined) throw new Error(`Manifest missing: ${k}`);
  }
  if (!m.particle_id.includes(".")) {
    throw new Error(`particle_id should be namespaced, got: ${m.particle_id}`);
  }
  if (m.origin_signature && m.origin_signature !== "MrLiouWord") {
    throw new Error(`origin_signature mismatch: ${m.origin_signature}`);
  }
}

/* --------------------------------- Runtime --------------------------------- */

export class ParticleRuntime {
  private registry: ParticleRegistry;
  private limiter = new RateLimiter();

  constructor(registry: ParticleRegistry) {
    this.registry = registry;
  }

  async invoke(ctx: ParticleContext, packet: ParticleInvokePacket): Promise<ParticleInvokeResult> {
    const plugin = this.registry.get(packet.particle_id);
    if (!plugin) {
      return { ok: false, error: `Particle not found: ${packet.particle_id}`, trace_merkle_root: ctx.merkle.getRoot() };
    }

    const m = plugin.manifest;

    // auth gate
    const auth = m.policy_gate.auth;
    if (auth === "deny") {
      return { ok: false, error: "Denied by policy", trace_merkle_root: ctx.merkle.getRoot() };
    }
    if (auth === "internal" && ctx.auth_token !== "internal") {
      return { ok: false, error: "Auth required: internal", trace_merkle_root: ctx.merkle.getRoot() };
    }
    if (auth === "scoped" && !ctx.auth_token) {
      return { ok: false, error: "Auth required: scoped", trace_merkle_root: ctx.merkle.getRoot() };
    }

    // role gate
    if (m.policy_gate.allow_roles && !m.policy_gate.allow_roles.includes(ctx.caller_role)) {
      return { ok: false, error: "Role not allowed", trace_merkle_root: ctx.merkle.getRoot() };
    }
    if (m.policy_gate.deny_roles && m.policy_gate.deny_roles.includes(ctx.caller_role)) {
      return { ok: false, error: "Role denied", trace_merkle_root: ctx.merkle.getRoot() };
    }

    // rate limit
    const rlKey = `${ctx.persona_id}:${ctx.caller_role}:${m.particle_id}`;
    if (!this.limiter.allow(rlKey, m.policy_gate.rate_limit, ctx.now)) {
      this.emitTrace(ctx, m.particle_id, "rate_limited", { rate_limit: m.policy_gate.rate_limit || "" });
      return { ok: false, error: "Rate limited", trace_merkle_root: ctx.merkle.getRoot() };
    }

    // input shallow contract
    for (const key of Object.keys(m.io_contract.input || {})) {
      if (packet.input[key] === undefined) {
        this.emitTrace(ctx, m.particle_id, "input_missing", { key });
        return { ok: false, error: `Input missing: ${key}`, trace_merkle_root: ctx.merkle.getRoot() };
      }
    }

    this.emitTrace(ctx, m.particle_id, "invoke", {
      intent: packet.intent || "",
      input_hash: sha256Hex(stableStringify(packet.input)),
    });

    try {
      const out = await plugin.execute(m.exec_adapter.entry, ctx, packet.input);

      for (const key of Object.keys(m.io_contract.output || {})) {
        if ((out as any)[key] === undefined) {
          this.emitTrace(ctx, m.particle_id, "output_missing", { key });
          return { ok: false, error: `Output missing: ${key}`, trace_merkle_root: ctx.merkle.getRoot() };
        }
      }

      this.emitTrace(ctx, m.particle_id, "ok", { output_hash: sha256Hex(stableStringify(out)) });
      return { ok: true, output: out, trace_merkle_root: ctx.merkle.getRoot() };
    } catch (e: any) {
      this.emitTrace(ctx, m.particle_id, "error", { message: String(e?.message || e) });
      return { ok: false, error: String(e?.message || e), trace_merkle_root: ctx.merkle.getRoot() };
    }
  }

  private emitTrace(ctx: ParticleContext, particle_id: string, event: string, payload: Dict) {
    const base = {
      rid: ctx.rid,
      tick: ctx.tick,
      persona_id: ctx.persona_id,
      particle_id,
      event,
      ts: ctx.now,
      payload,
    };
    const leaf = ctx.merkle.addLeaf(base);
    const env: TraceEnvelope = {
      event_id: newId("evt"),
      rid: ctx.rid,
      tick: ctx.tick,
      persona_id: ctx.persona_id,
      merkle_root: ctx.merkle.getRoot(),
      particle_id,
      event,
      ts: ctx.now,
      payload: { ...payload, leaf },
    };
    ctx.trace.emit(env);
  }
}

/* --------------------------- Core Particle Plugins -------------------------- */

export class RolePersonaBindPlugin implements ParticlePlugin {
  manifest: ParticleManifest = {
    particle_id: "role.persona.bind.v1",
    role_binding: ["planner", "operator"],
    capability: "bind_intent_to_persona_state",
    io_contract: { input: { task_intent: "string", context_snapshot: "object" }, output: { persona_state: "object" } },
    state_model: { type: "persona_vector", persist: true },
    exec_adapter: { type: "local", entry: "bind" },
    policy_gate: { auth: "internal", rate_limit: "30/s" },
    trace_hook: { emit: ["invoke", "ok", "error"] },
    version: "0.2.0",
    origin_signature: "MrLiouWord",
    created_at: new Date().toISOString(),
  };

  execute(entry: string, ctx: ParticleContext, input: Dict): Dict {
    if (entry !== "bind") throw new Error(`Unknown entry: ${entry}`);
    const task_intent = String(input.task_intent || "");
    const snapshot = (input.context_snapshot || {}) as Dict;
    const persona_state = {
      persona_id: ctx.persona_id,
      intent: task_intent,
      context_hash: sha256Hex(stableStringify(snapshot)),
      weights: {
        planning: task_intent.includes("規劃") ? 0.8 : 0.5,
        execution: task_intent.includes("部署") ? 0.8 : 0.5,
        analysis: task_intent.includes("分析") ? 0.8 : 0.5,
      },
      memory_pointer: `mem://persona/${ctx.persona_id}/${sha256Hex(task_intent).slice(0, 12)}`,
    };
    ctx.memory.put(persona_state.memory_pointer, persona_state);
    return { persona_state };
  }
}

export class FlowTaskDecomposePlugin implements ParticlePlugin {
  manifest: ParticleManifest = {
    particle_id: "flow.task.decompose.v1",
    role_binding: ["planner"],
    capability: "decompose_goal_to_task_graph",
    io_contract: { input: { goal_spec: "object" }, output: { task_graph: "dag" } },
    state_model: { type: "dag_state", persist: true },
    exec_adapter: { type: "local", entry: "decompose" },
    policy_gate: { auth: "internal", rate_limit: "10/s" },
    trace_hook: { emit: ["task_created", "task_linked"] },
    version: "0.2.0",
    origin_signature: "MrLiouWord",
    created_at: new Date().toISOString(),
  };

  execute(entry: string, ctx: ParticleContext, input: Dict): Dict {
    if (entry !== "decompose") throw new Error(`Unknown entry: ${entry}`);
    const goal = (input.goal_spec || {}) as Dict;
    const title = String((goal as any).title || "goal");
    const deliverable = String((goal as any).deliverable || "artifact");
    const targets = Array.isArray((goal as any).targets) ? ((goal as any).targets as any[]) : [];
    const nodes = [
      { id: "t0", name: "collect_inputs", depends_on: [] as string[] },
      { id: "t1", name: "build_particle_manifests", depends_on: ["t0"] },
      { id: "t2", name: "implement_runtime_adapters", depends_on: ["t1"] },
      { id: "t3", name: "wire_policy_and_trace", depends_on: ["t2"] },
      { id: "t4", name: "package_deliverable", depends_on: ["t3"] },
    ];
    const task_graph = {
      goal: { title, deliverable, targets },
      nodes,
      edges: [
        ["t0", "t1"],
        ["t1", "t2"],
        ["t2", "t3"],
        ["t3", "t4"],
      ],
      dag_hash: sha256Hex(stableStringify({ title, deliverable, targets, nodes })),
    };
    ctx.memory.put(`mem://dag/${task_graph.dag_hash.slice(0, 16)}`, task_graph);
    return { task_graph };
  }
}

export type InProcAdapter = (ctx: ParticleContext, request: Dict) => Promise<Dict> | Dict;

export class ConnectorApiMountPlugin implements ParticlePlugin {
  private adapters = new Map<string, InProcAdapter>();

  manifest: ParticleManifest = {
    particle_id: "connector.api.mount.v1",
    role_binding: ["operator"],
    capability: "mount_and_dispatch_api_connector",
    io_contract: { input: { request_packet: "object" }, output: { response_packet: "object" } },
    state_model: { type: "connector_state", persist: false },
    exec_adapter: { type: "local", entry: "dispatch" },
    policy_gate: { auth: "scoped", rate_limit: "20/s" },
    trace_hook: { emit: ["invoke", "ok", "error"] },
    version: "0.2.0",
    origin_signature: "MrLiouWord",
    created_at: new Date().toISOString(),
  };

  mount(name: string, adapter: InProcAdapter) {
    if (this.adapters.has(name)) throw new Error(`Adapter already mounted: ${name}`);
    this.adapters.set(name, adapter);
  }

  async execute(entry: string, ctx: ParticleContext, input: Dict): Promise<Dict> {
    if (entry !== "dispatch") throw new Error(`Unknown entry: ${entry}`);
    const packet = (input.request_packet || {}) as Dict;
    const adapterName = String(packet.adapter || "");
    const request = (packet.request || {}) as Dict;
    if (!adapterName) throw new Error("request_packet.adapter required");
    const adapter = this.adapters.get(adapterName);
    if (!adapter) throw new Error(`Adapter not found: ${adapterName}`);
    const response = await adapter(ctx, request);
    return {
      response_packet: {
        adapter: adapterName,
        response,
        response_hash: sha256Hex(stableStringify(response)),
      },
    };
  }
}

/* -------------------- Pack Exporter Particle (GitHub/CF) -------------------- */

export class PluginPackExportPlugin implements ParticlePlugin {
  private registry: ParticleRegistry;

  constructor(registry: ParticleRegistry) {
    this.registry = registry;
  }

  manifest: ParticleManifest = {
    particle_id: "plugin.pack.export.v1",
    role_binding: ["operator", "planner"],
    capability: "export_deployable_bundle_for_github_and_cloudflare",
    io_contract: {
      input: {
        out_dir: "string",
        package_name: "string",
        include_cloudflare: "boolean",
        include_github_actions: "boolean",
        include_trace: "boolean",
      },
      output: {
        package_path: "string",
        files_written: "number",
        package_merkle_root: "string",
      },
    },
    state_model: { type: "pack_state", persist: true },
    exec_adapter: { type: "local", entry: "export" },
    policy_gate: { auth: "internal", rate_limit: "5/s" },
    trace_hook: { emit: ["invoke", "ok", "error"] },
    version: "0.2.0",
    origin_signature: "MrLiouWord",
    created_at: new Date().toISOString(),
  };

  execute(entry: string, ctx: ParticleContext, input: Dict): Dict {
    if (entry !== "export") throw new Error(`Unknown entry: ${entry}`);

    const out_dir = String(input.out_dir || "dist");
    const package_name = String(input.package_name || "mrliou_particle_pack");
    const include_cloudflare = Boolean(input.include_cloudflare);
    const include_github_actions = Boolean(input.include_github_actions);
    const include_trace = Boolean(input.include_trace);

    const pkgRoot = path.resolve(out_dir, package_name);
    ensureDir(pkgRoot);

    // 1) manifests
    const manifests = this.registry.list();
    writeFileAtomic(path.join(pkgRoot, "manifests.json"), stableStringify({ manifests }) + "\n");

    // 2) trace + merkle_root (封存)
    const sealDir = path.join(pkgRoot, "seal");
    ensureDir(sealDir);

    writeFileAtomic(
      path.join(sealDir, "trace_merkle_root.txt"),
      ctx.merkle.getRoot() + "\n"
    );

    if (include_trace) {
      const events = ctx.trace.list();
      // jsonl
      const jsonl = events.map((e) => stableStringify(e)).join("\n") + (events.length ? "\n" : "");
      writeFileAtomic(path.join(sealDir, "trace.jsonl"), jsonl);
      // summary
      writeFileAtomic(
        path.join(sealDir, "trace_summary.json"),
        stableStringify({
          rid: ctx.rid,
          persona_id: ctx.persona_id,
          tick: ctx.tick,
          events: events.length,
          merkle_root: ctx.merkle.getRoot(),
        }) + "\n"
      );
    }

    // 3) Cloudflare Worker bundle (minimal, runnable)
    if (include_cloudflare) {
      const workerDir = path.join(pkgRoot, "cloudflare_worker");
      ensureDir(workerDir);

      const pkgJson = {
        name: package_name + "-worker",
        private: true,
        type: "module",
        scripts: {
          "dev": "wrangler dev",
          "deploy": "wrangler deploy",
        },
        devDependencies: {
          wrangler: "^3.0.0",
        },
      };
      writeFileAtomic(path.join(workerDir, "package.json"), stableStringify(pkgJson) + "\n");

      const wranglerToml = [
        `name = "${package_name.replace(/[^a-zA-Z0-9_-]/g, "-")}"`,
        `main = "src/worker.ts"`,
        `compatibility_date = "${new Date().toISOString().slice(0, 10)}"`,
        ``,
      ].join("\n");
      writeFileAtomic(path.join(workerDir, "wrangler.toml"), wranglerToml);

      // worker exposes /manifests and /seal
      const workerTs = `
// origin_signature: MrLiouWord
export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/health") return new Response("ok", { status: 200 });

    if (url.pathname === "/manifests") {
      const data = await (await fetch(new URL("./manifests.json", import.meta.url))).text().catch(() => "");
      return new Response(data || "{}", { status: 200, headers: { "content-type": "application/json; charset=utf-8" } });
    }

    if (url.pathname === "/seal/merkle") {
      const data = await (await fetch(new URL("./seal/trace_merkle_root.txt", import.meta.url))).text().catch(() => "");
      return new Response(data || "", { status: 200, headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    if (url.pathname === "/seal/trace") {
      const data = await (await fetch(new URL("./seal/trace.jsonl", import.meta.url))).text().catch(() => "");
      return new Response(data || "", { status: 200, headers: { "content-type": "application/jsonl; charset=utf-8" } });
    }

    return new Response("not_found", { status: 404 });
  }
} satisfies ExportedHandler;
`;
      ensureDir(path.join(workerDir, "src"));
      writeFileAtomic(path.join(workerDir, "src/worker.ts"), workerTs.trimStart());

      // Copy manifests + seal into worker root so fetch(import.meta.url) works in dev
      // Wrangler will bundle these as modules only if referenced; we keep them in same folder for simplicity.
      writeFileAtomic(path.join(workerDir, "manifests.json"), stableStringify({ manifests }) + "\n");
      writeFileAtomic(path.join(workerDir, "seal/trace_merkle_root.txt"), ctx.merkle.getRoot() + "\n");
      if (include_trace) {
        const events = ctx.trace.list();
        const jsonl = events.map((e) => stableStringify(e)).join("\n") + (events.length ? "\n" : "");
        writeFileAtomic(path.join(workerDir, "seal/trace.jsonl"), jsonl);
      } else {
        writeFileAtomic(path.join(workerDir, "seal/trace.jsonl"), "");
      }
    }

    // 4) GitHub Actions (optional) – deploy worker with Wrangler
    if (include_github_actions) {
      const wfDir = path.join(pkgRoot, ".github", "workflows");
      ensureDir(wfDir);

      const deployYml = `
name: deploy-cloudflare-worker
on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: cloudflare_worker
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install
        run: npm install
      - name: Deploy
        env:
          CLOUDFLARE_API_TOKEN: \${{ secrets.CLOUDFLARE_API_TOKEN }}
        run: npx wrangler deploy
`.trimStart();
      writeFileAtomic(path.join(wfDir, "deploy-cloudflare-worker.yml"), deployYml);
    }

    // 5) package merkle root (封存：對整包檔案做 fold)
    const files = listFilesRec(pkgRoot);
    let pkgMerkle = sha256Hex("mrliou_package_merkle_init");
    for (const f of files) {
      const rel = path.relative(pkgRoot, f).replace(/\\/g, "/");
      const buf = fs.readFileSync(f);
      const leaf = sha256Hex(rel + "\n" + sha256Hex(buf.toString("utf8")));
      pkgMerkle = sha256Hex(pkgMerkle + leaf);
    }
    writeFileAtomic(path.join(sealDir, "package_merkle_root.txt"), pkgMerkle + "\n");

    // persist pack record
    ctx.memory.put(`mem://pack/${pkgMerkle.slice(0, 16)}`, {
      package_path: pkgRoot,
      package_merkle_root: pkgMerkle,
      trace_merkle_root: ctx.merkle.getRoot(),
      files_written: files.length,
      created_at: new Date().toISOString(),
    });

    return {
      package_path: pkgRoot,
      files_written: files.length,
      package_merkle_root: pkgMerkle,
    };
  }
}

/* ------------------------------ Bootstrap / API ----------------------------- */

export function createDefaultRuntime(): {
  registry: ParticleRegistry;
  runtime: ParticleRuntime;
  plugins: {
    rolePersonaBind: RolePersonaBindPlugin;
    flowTaskDecompose: FlowTaskDecomposePlugin;
    connectorApiMount: ConnectorApiMountPlugin;
    pluginPackExport: PluginPackExportPlugin;
  };
} {
  const registry = new ParticleRegistry();

  const rolePersonaBind = new RolePersonaBindPlugin();
  const flowTaskDecompose = new FlowTaskDecomposePlugin();
  const connectorApiMount = new ConnectorApiMountPlugin();

  connectorApiMount.mount("echo", (_ctx, req) => ({ ok: true, echo: req }));

  registry.register(rolePersonaBind);
  registry.register(flowTaskDecompose);
  registry.register(connectorApiMount);

  const pluginPackExport = new PluginPackExportPlugin(registry);
  registry.register(pluginPackExport);

  const runtime = new ParticleRuntime(registry);

  return {
    registry,
    runtime,
    plugins: { rolePersonaBind, flowTaskDecompose, connectorApiMount, pluginPackExport },
  };
}

export function createContext(params: {
  persona_id: string;
  caller_role: string;
  auth_token?: string;
  world?: Dict;
  rid?: string;
  tick?: number;
}): ParticleContext {
  const rid = params.rid || newId("rid");
  const tick = params.tick ?? 0;
  const now = Date.now();
  return {
    rid,
    tick,
    persona_id: params.persona_id,
    now,
    world: params.world || {},
    memory: new MemoryBus(),
    trace: new TraceBus(),
    caller_role: params.caller_role,
    auth_token: params.auth_token,
    merkle: new MerkleFold(),
  };
}

/* ------------------------------- Self-test CLI ------------------------------ */
/* Run:
 *   ts-node mrliou_particle_plugin_runtime_v0.2_pack.ts
 * Output: creates dist/mrliou_particle_pack with manifests + seal + optional worker + optional github action
 */
if (require.main === module) {
  (async () => {
    const { runtime } = createDefaultRuntime();

    // create traces first
    const plannerCtx = createContext({ persona_id: "persona_partner", caller_role: "planner", auth_token: "internal" });

    await runtime.invoke(plannerCtx, {
      particle_id: "role.persona.bind.v1",
      input: { task_intent: "規劃並部署粒子插件系統", context_snapshot: { x: 1 } },
    });

    await runtime.invoke(plannerCtx, {
      particle_id: "flow.task.decompose.v1",
      input: { goal_spec: { title: "Particle Pack", deliverable: "github_cloudflare_bundle", targets: ["github", "cloudflare"] } },
    });

    // export package (needs internal auth)
    const packRes = await runtime.invoke(plannerCtx, {
      particle_id: "plugin.pack.export.v1",
      input: {
        out_dir: "dist",
        package_name: "mrliou_particle_pack",
        include_cloudflare: true,
        include_github_actions: true,
        include_trace: true,
      },
    });

    const out = {
      ok: packRes.ok,
      package_path: packRes.output?.package_path,
      files_written: packRes.output?.files_written,
      package_merkle_root: packRes.output?.package_merkle_root,
      trace_merkle_root: plannerCtx.merkle.getRoot(),
      trace_events: plannerCtx.trace.list().length,
    };

    process.stdout.write(stableStringify(out) + "\n");
  })().catch((e) => {
    process.stderr.write(String(e?.stack || e) + "\n");
    process.exit(1);
  });
}
