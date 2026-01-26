/**
 * FlpkgLoader - Integration loader for UniversalRuntime
 * Origin Signature: MrLiouWord
 */

import { FlpkgLoader as Loader, FlpkgManifest } from '../../formats/flpkg/FlpkgLoader';
import { FlpkgPacker as Packer } from '../../formats/flpkg/FlpkgPacker';

export async function load(path: string): Promise<FlpkgManifest> {
  const loader = new Loader();
  return loader.load(path);
}

export async function pack(manifest: FlpkgManifest, outputPath: string): Promise<void> {
  const packer = new Packer();
  return packer.pack(manifest, outputPath);
}

export { FlpkgManifest };
