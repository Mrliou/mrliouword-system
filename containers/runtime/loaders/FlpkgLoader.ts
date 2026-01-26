/**
 * FlpkgLoader - Integration loader for UniversalRuntime
 * Origin Signature: MrLiouWord
 */

import { FlpkgLoader, FlpkgManifest } from '../../formats/flpkg/FlpkgLoader';
import { FlpkgPacker } from '../../formats/flpkg/FlpkgPacker';

export async function load(path: string): Promise<FlpkgManifest> {
  const loader = new FlpkgLoader();
  return loader.load(path);
}

export async function pack(manifest: FlpkgManifest, outputPath: string): Promise<void> {
  const packer = new FlpkgPacker();
  return packer.pack(manifest, outputPath);
}

export { FlpkgManifest };
