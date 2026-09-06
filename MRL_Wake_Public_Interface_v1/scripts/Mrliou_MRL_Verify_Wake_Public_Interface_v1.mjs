import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.resolve(here, "../schema/Mrliou_MRL_Wake_Manifest_Public_Interface_v1.schema.json");
const required = ["schema_version", "manifest_id", "origin_signature", "record_mode", "status", "runtime_contract"];
const sample = {
  schema_version: "mrl.wake-manifest.public-interface.v1",
  manifest_id: "MRL-WAKE-PUBLIC-SELFTEST-V1",
  origin_signature: "MrLiouWord",
  record_mode: "additive_only",
  status: "IMPLEMENTED",
  runtime_contract: {
    consumer_interface: "Mrliou_MRL_Wake_Consumer_v1",
    fail_closed: true,
    receipt_schema: "mrl.wake-receipt.v1"
  }
};

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
const candidate = process.argv[2] ? JSON.parse(fs.readFileSync(process.argv[2], "utf8")) : sample;
const errors = [];
for (const key of required) if (!(key in candidate)) errors.push(`missing:${key}`);
if (candidate.schema_version !== schema.properties.schema_version.const) errors.push("schema_version_mismatch");
if (!/^MRL-WAKE-[A-Z0-9._-]+$/.test(candidate.manifest_id ?? "")) errors.push("manifest_id_invalid");
if (candidate.origin_signature !== "MrLiouWord") errors.push("origin_signature_mismatch");
if (candidate.record_mode !== "additive_only") errors.push("record_mode_mismatch");
if (!schema.properties.status.enum.includes(candidate.status)) errors.push("status_invalid");
if (candidate.runtime_contract?.consumer_interface !== "Mrliou_MRL_Wake_Consumer_v1") errors.push("consumer_interface_mismatch");
if (candidate.runtime_contract?.fail_closed !== true) errors.push("fail_closed_required");
if (candidate.runtime_contract?.receipt_schema !== "mrl.wake-receipt.v1") errors.push("receipt_schema_mismatch");

const result = {
  interface: "mrl.wake-manifest.public-interface.v1",
  mode: process.argv[2] ? "candidate" : "self-test",
  result: errors.length ? "FAIL" : "PASS",
  errors,
  disclosure_boundary: "No private wake topology, memory references, platform paths, or runtime receipt content is emitted."
};
console.log(JSON.stringify(result));
process.exit(errors.length ? 1 : 0);
