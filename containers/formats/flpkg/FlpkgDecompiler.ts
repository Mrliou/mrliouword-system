import { FlpkgContainer } from '../../runtime/types'

export function decompile(container: FlpkgContainer): string {
  const fltnz = container.content.particles
    ?.map(p => `${p.word}⧉/fx.${p.fx}/`)
    .join(' ') || ''
  
  return fltnz
}

export function compile(fltnz: string, metadata: any): FlpkgContainer {
  const tokens = fltnz.split(' ').map(token => {
    const match = token.match(/(.+)⧉\/fx\.(.+)\//)
    if (match) {
      return { word: match[1], fx: match[2] }
    }
    return null
  }).filter(Boolean)
  
  return {
    id: `flpkg-${Date.now()}`,
    version: 'flpkg/1.0',
    origin_signature: 'MrLiouWord',
    layer: metadata.layer || 'L2',
    content: {
      particles: tokens,
      metadata
    }
  }
}
