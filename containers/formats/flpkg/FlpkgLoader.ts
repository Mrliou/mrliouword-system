import * as fs from 'fs/promises'
import * as path from 'path'
import { FlpkgContainer } from '../../runtime/types'

export async function load(filepath: string): Promise<FlpkgContainer> {
  const ext = path.extname(filepath)
  
  if (ext === '.json') {
    return loadJson(filepath)
  } else if (ext === '.zip' || ext === '.flpkg') {
    return loadZip(filepath)
  }
  
  throw new Error(`Unsupported file format: ${ext}`)
}

async function loadJson(filepath: string): Promise<FlpkgContainer> {
  const content = await fs.readFile(filepath, 'utf-8')
  return JSON.parse(content)
}

async function loadZip(filepath: string): Promise<FlpkgContainer> {
  // Extract and parse .flpkg zip file
  const AdmZip = (await import('adm-zip')).default
  const zip = new AdmZip(filepath)
  const entries = zip.getEntries()
  
  const manifestEntry = entries.find(e => e.entryName === 'manifest.json')
  if (!manifestEntry) {
    throw new Error('No manifest.json found in .flpkg')
  }
  
  const manifest = JSON.parse(manifestEntry.getData().toString('utf-8'))
  return manifest
}

export async function pack(container: FlpkgContainer, outputPath: string): Promise<void> {
  const AdmZip = (await import('adm-zip')).default
  const zip = new AdmZip()
  
  // Add manifest
  zip.addFile('manifest.json', Buffer.from(JSON.stringify(container, null, 2)))
  
  // Add particles if present
  if (container.content.particles) {
    zip.addFile('particles.json', Buffer.from(JSON.stringify(container.content.particles, null, 2)))
  }
  
  zip.writeZip(outputPath)
  console.log(`[FlpkgLoader] Packed container to ${outputPath}`)
}
