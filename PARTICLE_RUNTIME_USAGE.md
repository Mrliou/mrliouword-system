# MrLiouWord Particle Plugin Runtime v0.2 - Usage Guide

origin_signature: MrLiouWord

## Overview

The particle plugin runtime system provides a manifest-based plugin architecture with built-in policy enforcement, tracing, and deployment capabilities.

## Installation

The system is implemented as a single TypeScript file that can be used directly:

```bash
# Compile TypeScript
npx tsc --target ES2022 --lib ES2022 --module commonjs --esModuleInterop --skipLibCheck mrliou_particle_plugin_runtime_v0.2_pack.ts

# Run self-test
node mrliou_particle_plugin_runtime_v0.2_pack.js
```

## CLI Usage

### Self-Test and Package Generation

Run the self-test to generate a deployable package:

```bash
node mrliou_particle_plugin_runtime_v0.2_pack.js
```

This creates `dist/mrliou_particle_pack/` with:
- Particle manifests
- Sealed trace logs
- Cloudflare Worker bundle
- GitHub Actions workflow

Output example:
```json
{
  "ok": true,
  "package_path": "/path/to/dist/mrliou_particle_pack",
  "files_written": 11,
  "package_merkle_root": "...",
  "trace_merkle_root": "...",
  "trace_events": 6
}
```

## Programmatic Usage

### Basic Example

```javascript
const runtime = require('./mrliou_particle_plugin_runtime_v0.2_pack.js');

async function main() {
  // Create runtime with default plugins
  const { runtime: rt, plugins } = runtime.createDefaultRuntime();
  
  // Create execution context
  const ctx = runtime.createContext({
    persona_id: "my_persona",
    caller_role: "planner",
    auth_token: "internal"
  });
  
  // Invoke a particle
  const result = await rt.invoke(ctx, {
    particle_id: "role.persona.bind.v1",
    input: {
      task_intent: "規劃系統架構",
      context_snapshot: { project: "particle_system" }
    }
  });
  
  console.log("Result:", result);
  console.log("Trace events:", ctx.trace.list().length);
  console.log("Merkle root:", ctx.merkle.getRoot());
}

main().catch(console.error);
```

### Available Particles

#### 1. role.persona.bind.v1

Binds task intent to persona state with weighted vectors.

```javascript
const result = await rt.invoke(ctx, {
  particle_id: "role.persona.bind.v1",
  input: {
    task_intent: "規劃並部署系統",
    context_snapshot: { environment: "production" }
  }
});
// Output: { persona_state: { persona_id, intent, context_hash, weights, memory_pointer } }
```

#### 2. flow.task.decompose.v1

Decomposes goals into task graphs (DAG).

```javascript
const result = await rt.invoke(ctx, {
  particle_id: "flow.task.decompose.v1",
  input: {
    goal_spec: {
      title: "Deploy Particle System",
      deliverable: "production_bundle",
      targets: ["github", "cloudflare"]
    }
  }
});
// Output: { task_graph: { goal, nodes, edges, dag_hash } }
```

#### 3. connector.api.mount.v1

Mounts and dispatches API connectors.

```javascript
// First, mount an adapter on the plugin
plugins.connectorApiMount.mount("myapi", async (ctx, request) => {
  return { status: "ok", data: request };
});

// Then invoke
const result = await rt.invoke(ctx, {
  particle_id: "connector.api.mount.v1",
  input: {
    request_packet: {
      adapter: "myapi",
      request: { action: "fetch", id: 123 }
    }
  }
});
// Output: { response_packet: { adapter, response, response_hash } }
```

#### 4. plugin.pack.export.v1

Exports deployable bundles.

```javascript
const result = await rt.invoke(ctx, {
  particle_id: "plugin.pack.export.v1",
  input: {
    out_dir: "dist",
    package_name: "my_particle_pack",
    include_cloudflare: true,
    include_github_actions: true,
    include_trace: true
  }
});
// Output: { package_path, files_written, package_merkle_root }
```

### Custom Plugin Development

```javascript
class MyCustomPlugin {
  manifest = {
    particle_id: "my.custom.plugin.v1",
    role_binding: ["operator"],
    capability: "custom_operation",
    io_contract: {
      input: { data: "string" },
      output: { result: "string" }
    },
    state_model: { type: "stateless", persist: false },
    exec_adapter: { type: "local", entry: "process" },
    policy_gate: { auth: "internal", rate_limit: "10/s" },
    trace_hook: { emit: ["invoke", "ok", "error"] },
    version: "1.0.0",
    origin_signature: "MrLiouWord",
    created_at: new Date().toISOString()
  };
  
  execute(entry, ctx, input) {
    if (entry !== "process") throw new Error(`Unknown entry: ${entry}`);
    
    // Your custom logic here
    const result = input.data.toUpperCase();
    
    return { result };
  }
}

// Register custom plugin
const registry = new runtime.ParticleRegistry();
registry.register(new MyCustomPlugin());
const rt = new runtime.ParticleRuntime(registry);
```

## Policy Enforcement

### Authentication Modes

- `internal`: Requires `auth_token: "internal"`
- `scoped`: Requires any auth_token
- `public`: No auth required
- `deny`: Always denied

### Rate Limiting

Configurable per particle: `"10/s"`, `"100/m"`, `"1000/h"`

### Role-Based Access

```javascript
policy_gate: {
  auth: "internal",
  allow_roles: ["planner", "operator"],  // Only these roles allowed
  deny_roles: ["guest"],                 // Explicitly denied
  rate_limit: "10/s"
}
```

## Trace System

All particle invocations are automatically traced with merkle verification:

```javascript
// Access traces
const traces = ctx.trace.list();

// Get merkle root
const merkleRoot = ctx.merkle.getRoot();

// Each trace includes:
// - event_id, rid, tick, persona_id
// - particle_id, event, ts
// - merkle_root, payload
```

## Deployment

The generated package in `dist/mrliou_particle_pack/` is ready for deployment:

### Cloudflare Workers

```bash
cd dist/mrliou_particle_pack/cloudflare_worker
npm install
npx wrangler deploy
```

### GitHub Actions

Automatically deploys on push to main. Requires `CLOUDFLARE_API_TOKEN` secret.

## Philosophy

> 怎麼過去，就怎麼回來
> (How you come is how you return)

The system ensures:
- Complete audit trails via merkle trees
- Manifest-based transparency
- Policy-enforced security
- Reproducible deployments

## API Reference

See generated `dist/mrliou_particle_pack/manifests.json` for complete particle specifications.
