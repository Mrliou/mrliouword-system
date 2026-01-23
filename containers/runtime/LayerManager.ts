/**
 * L0-L7 Layer Management System
 * 層級管理系統
 */

import { RuntimeInstance } from './types'

export const LAYERS = {
  L0: 'ROOT',      // Origin: MrLiouWord
  L1: 'SEED',      // dimension_seed_restore
  L2: 'PARTICLE',  // 17 fx particles
  L3: 'LAW',       // Business logic
  L4: 'WORLD',     // External connections
  L5: 'MIRROR',    // Backup/redundancy
  L6: 'REFLECT',   // UI/API projection
  L7: 'LOOP',      // Verification
} as const

export type Layer = keyof typeof LAYERS

export async function configure(instance: RuntimeInstance, layer: Layer) {
  console.log(`[LayerManager] Configuring layer: ${layer} (${LAYERS[layer]})`)
  
  switch(layer) {
    case 'L0':
      // Set origin signature
      instance.metadata.origin_signature = 'MrLiouWord'
      break
    case 'L1':
      // Load dimension seeds
      await loadDimensionSeeds(instance)
      break
    case 'L2':
      // Load fx particles from core/particle_dict.json
      await loadParticles(instance)
      break
    case 'L3':
      // Apply business logic rules
      await applyLawRules(instance)
      break
    case 'L4':
      // Setup external connections (Cloudflare, GitHub, etc.)
      await setupWorldConnections(instance)
      break
    case 'L5':
      // Configure backup and mirroring
      await configureMirror(instance)
      break
    case 'L6':
      // Setup UI/API projections
      await setupReflections(instance)
      break
    case 'L7':
      // Enable verification and closure
      await enableVerification(instance)
      break
  }
}

async function loadParticles(instance: RuntimeInstance) {
  try {
    const path = await import('path')
    const fs = await import('fs')
    
    // Try multiple paths to find particle_dict.json
    const possiblePaths = [
      path.join(__dirname, '../../core/particle_dict.json'),
      path.join(process.cwd(), 'core/particle_dict.json'),
      path.join(__dirname, '../../../core/particle_dict.json'),
    ]
    
    let particleData = null
    for (const filePath of possiblePaths) {
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf-8')
        particleData = JSON.parse(content)
        break
      }
    }
    
    if (particleData) {
      // Store the entire particle dictionary
      instance.metadata.particle_dict = particleData
      console.log(`[LayerManager] Loaded particle dictionary`)
    } else {
      console.warn(`[LayerManager] particle_dict.json not found in any expected location`)
    }
  } catch (error) {
    console.warn(`[LayerManager] Could not load particles: ${error}`)
  }
}

async function loadDimensionSeeds(instance: RuntimeInstance) {
  // Implementation for L1 seed loading
  console.log(`[LayerManager] Loading dimension seeds for ${instance.id}`)
}

async function applyLawRules(instance: RuntimeInstance) {
  // Implementation for L3 law rules
  console.log(`[LayerManager] Applying law rules for ${instance.id}`)
}

async function setupWorldConnections(instance: RuntimeInstance) {
  // Implementation for L4 external connections
  console.log(`[LayerManager] Setting up world connections for ${instance.id}`)
}

async function configureMirror(instance: RuntimeInstance) {
  // Implementation for L5 mirroring
  console.log(`[LayerManager] Configuring mirror for ${instance.id}`)
}

async function setupReflections(instance: RuntimeInstance) {
  // Implementation for L6 projections
  console.log(`[LayerManager] Setting up reflections for ${instance.id}`)
}

async function enableVerification(instance: RuntimeInstance) {
  // Implementation for L7 verification
  console.log(`[LayerManager] Enabling verification for ${instance.id}`)
}
