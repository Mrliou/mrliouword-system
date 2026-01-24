/**
 * Manual tests for MCP CLI commands
 * Run these tests to verify functionality
 */

import { McpConfigManager } from '../cli/mcp-config'
import { McpServerHeader } from '../cli/mcp-types'
import * as fs from 'fs/promises'
import * as path from 'path'
import * as os from 'os'

const TEST_CONFIG_DIR = path.join(os.tmpdir(), '.mrliouword-test')
const TEST_CONFIG_FILE = path.join(TEST_CONFIG_DIR, 'mcp-config.json')

async function cleanup() {
  try {
    await fs.rm(TEST_CONFIG_DIR, { recursive: true, force: true })
  } catch (error) {
    // Ignore errors
  }
}

async function testAddServer() {
  console.log('\n🧪 Test: Add MCP server')
  const manager = new McpConfigManager()
  
  // Override config path for testing
  Object.defineProperty(manager, 'getConfigPath', {
    value: () => TEST_CONFIG_FILE
  })
  
  const headers: McpServerHeader[] = [
    { key: 'Authorization', value: 'Bearer test-token' }
  ]
  
  await manager.addServer('https://test.com/mcp', headers)
  
  const servers = await manager.listServers()
  
  if (servers.length !== 1) {
    throw new Error(`Expected 1 server, got ${servers.length}`)
  }
  
  if (servers[0].url !== 'https://test.com/mcp') {
    throw new Error(`Expected URL to be https://test.com/mcp, got ${servers[0].url}`)
  }
  
  if (servers[0].headers?.length !== 1) {
    throw new Error(`Expected 1 header, got ${servers[0].headers?.length}`)
  }
  
  console.log('✅ Add server test passed')
}

async function testAddMultipleHeaders() {
  console.log('\n🧪 Test: Add server with multiple headers')
  const manager = new McpConfigManager()
  
  Object.defineProperty(manager, 'getConfigPath', {
    value: () => TEST_CONFIG_FILE
  })
  
  const headers: McpServerHeader[] = [
    { key: 'Authorization', value: 'Bearer xyz' },
    { key: 'X-API-Key', value: 'secret' },
    { key: 'Content-Type', value: 'application/json' }
  ]
  
  await manager.addServer('https://multi.com/api', headers)
  
  const servers = await manager.listServers()
  const server = servers.find(s => s.url === 'https://multi.com/api')
  
  if (!server) {
    throw new Error('Server not found')
  }
  
  if (server.headers?.length !== 3) {
    throw new Error(`Expected 3 headers, got ${server.headers?.length}`)
  }
  
  console.log('✅ Multiple headers test passed')
}

async function testRemoveServer() {
  console.log('\n🧪 Test: Remove MCP server')
  const manager = new McpConfigManager()
  
  Object.defineProperty(manager, 'getConfigPath', {
    value: () => TEST_CONFIG_FILE
  })
  
  const removed = await manager.removeServer('https://test.com/mcp')
  
  if (!removed) {
    throw new Error('Expected server to be removed')
  }
  
  const servers = await manager.listServers()
  const found = servers.find(s => s.url === 'https://test.com/mcp')
  
  if (found) {
    throw new Error('Server should have been removed')
  }
  
  console.log('✅ Remove server test passed')
}

async function testUpdateServer() {
  console.log('\n🧪 Test: Update existing server')
  const manager = new McpConfigManager()
  
  Object.defineProperty(manager, 'getConfigPath', {
    value: () => TEST_CONFIG_FILE
  })
  
  const initialServers = await manager.listServers()
  const initialCount = initialServers.length
  
  // Add with new headers
  const newHeaders: McpServerHeader[] = [
    { key: 'Authorization', value: 'Bearer updated-token' }
  ]
  
  await manager.addServer('https://multi.com/api', newHeaders)
  
  const servers = await manager.listServers()
  
  if (servers.length !== initialCount) {
    throw new Error(`Server count should not change, was ${initialCount}, now ${servers.length}`)
  }
  
  const server = servers.find(s => s.url === 'https://multi.com/api')
  
  if (!server) {
    throw new Error('Server not found')
  }
  
  if (server.headers?.length !== 1) {
    throw new Error(`Expected 1 header after update, got ${server.headers?.length}`)
  }
  
  if (server.headers[0].value !== 'Bearer updated-token') {
    throw new Error('Header value was not updated')
  }
  
  console.log('✅ Update server test passed')
}

async function runTests() {
  console.log('🚀 Running MCP Config Manager Tests\n')
  
  try {
    await cleanup()
    await testAddServer()
    await testAddMultipleHeaders()
    await testRemoveServer()
    await testUpdateServer()
    
    console.log('\n✅ All tests passed!')
  } catch (error) {
    console.error('\n❌ Test failed:', error)
    process.exit(1)
  } finally {
    await cleanup()
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runTests()
}

export { runTests }
