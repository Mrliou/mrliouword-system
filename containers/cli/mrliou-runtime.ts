#!/usr/bin/env node

import { Command } from 'commander'
import { UniversalRuntime } from '../runtime/UniversalRuntime'
import { MetaEnvController } from '../metaenv/MetaEnvController'
import * as fs from 'fs/promises'

const program = new Command()

program
  .name('mrliou-runtime')
  .description('MrLiouWord Universal Container Runtime CLI')
  .version('1.0.0')

program
  .command('init')
  .description('Initialize runtime environment')
  .action(async () => {
    console.log('🚀 Initializing MrLiouWord Runtime...')
    const runtime = new UniversalRuntime()
    console.log('✅ Runtime initialized')
  })

program
  .command('load <file>')
  .description('Load a .flpkg container')
  .option('-l, --layer <layer>', 'Layer to apply (L0-L7)', 'L2')
  .action(async (file, options) => {
    console.log(`📦 Loading container: ${file}`)
    const runtime = new UniversalRuntime()
    
    try {
      const container = await runtime.load(file)
      console.log(`✅ Container loaded: ${container.id}`)
      console.log(`   Origin: ${container.origin_signature}`)
      console.log(`   Layer: ${container.layer}`)
    } catch (error) {
      console.error('❌ Failed to load container:', error)
      process.exit(1)
    }
  })

program
  .command('spawn')
  .description('Spawn a MetaEnv environment')
  .option('--cpu <cores>', 'CPU cores', '4')
  .option('--ram <size>', 'RAM size', '8G')
  .option('--policy <policy>', 'Security policy')
  .action(async (options) => {
    console.log('🌱 Spawning MetaEnv...')
    const controller = new MetaEnvController()
    
    const result = await controller.spawn({
      shape: {
        cpu: parseInt(options.cpu),
        ram: options.ram
      },
      policy: options.policy
    })
    
    console.log(`✅ Environment spawned: ${result.env_id}`)
    console.log(`   Status: ${result.status}`)
  })

program
  .command('reverse-mine')
  .description('Run reverse mining on trace files')
  .requiredOption('--trace-fs <file>', 'trace_fs.csv file')
  .requiredOption('--trace-ops <file>', 'trace_ops.csv file')
  .option('-o, --output <file>', 'Output file', 'rules_output.yaml')
  .action(async (options) => {
    console.log('🔍 Running Trace Miner...')
    // Call Python script
    const { spawn } = await import('child_process')
    const python = spawn('python', [
      'containers/reverse-engine/TraceMiner.py',
      options.traceFs,
      options.traceOps
    ])
    
    python.stdout.on('data', (data) => console.log(data.toString()))
    python.stderr.on('data', (data) => console.error(data.toString()))
    python.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Reverse mining completed')
      } else {
        console.error('❌ Reverse mining failed')
        process.exit(1)
      }
    })
  })

program.parse()
