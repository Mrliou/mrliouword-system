#!/usr/bin/env node

import { Command } from 'commander'
import { UniversalRuntime } from '../runtime/UniversalRuntime'
import { MetaEnvController } from '../metaenv/MetaEnvController'
import { McpConfigManager } from './mcp-config'
import { McpServerHeader } from './mcp-types'
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

// Copilot MCP commands
const copilot = program.command('copilot').description('GitHub Copilot integration commands')

const mcp = copilot.command('mcp').description('Model Context Protocol server management')

mcp
  .command('add <url>')
  .description('Add an MCP server with optional headers')
  .option('--header <header>', 'Add custom header in format "Key=Value" (can be used multiple times)', (value, previous: string[] = []) => {
    previous.push(value)
    return previous
  }, [])
  .action(async (url: string, options: { header: string[] }) => {
    console.log('🔗 Adding MCP server...')
    
    const configManager = new McpConfigManager()
    
    // Parse headers
    const headers: McpServerHeader[] = []
    for (const headerStr of options.header) {
      const separatorIndex = headerStr.indexOf('=')
      if (separatorIndex === -1) {
        console.error(`❌ Invalid header format: ${headerStr}`)
        console.error('   Expected format: "Key=Value"')
        process.exit(1)
      }
      
      const key = headerStr.substring(0, separatorIndex)
      const value = headerStr.substring(separatorIndex + 1)
      headers.push({ key, value })
    }
    
    try {
      await configManager.addServer(url, headers)
      console.log(`✅ MCP server added: ${url}`)
      if (headers.length > 0) {
        console.log('   Headers:')
        headers.forEach(h => {
          // Mask sensitive values
          const displayValue = h.key.toLowerCase().includes('auth') || h.key.toLowerCase().includes('token') 
            ? '***' 
            : h.value
          console.log(`     ${h.key}: ${displayValue}`)
        })
      }
      console.log(`   Config saved to: ${configManager.getConfigPath()}`)
    } catch (error) {
      console.error('❌ Failed to add MCP server:', error)
      process.exit(1)
    }
  })

mcp
  .command('list')
  .description('List all configured MCP servers')
  .action(async () => {
    console.log('📋 Configured MCP servers:')
    
    const configManager = new McpConfigManager()
    const servers = await configManager.listServers()
    
    if (servers.length === 0) {
      console.log('   No servers configured')
      console.log(`   Add a server with: copilot mcp add <url>`)
      return
    }
    
    servers.forEach((server, index) => {
      console.log(`\n${index + 1}. ${server.url}`)
      console.log(`   Added: ${new Date(server.addedAt).toLocaleString()}`)
      if (server.headers && server.headers.length > 0) {
        console.log('   Headers:')
        server.headers.forEach(h => {
          const displayValue = h.key.toLowerCase().includes('auth') || h.key.toLowerCase().includes('token')
            ? '***'
            : h.value
          console.log(`     ${h.key}: ${displayValue}`)
        })
      }
    })
  })

mcp
  .command('remove <url>')
  .description('Remove an MCP server')
  .action(async (url: string) => {
    console.log('🗑️  Removing MCP server...')
    
    const configManager = new McpConfigManager()
    const removed = await configManager.removeServer(url)
    
    if (removed) {
      console.log(`✅ MCP server removed: ${url}`)
    } else {
      console.log(`⚠️  MCP server not found: ${url}`)
      process.exit(1)
    }
  })

program.parse()
