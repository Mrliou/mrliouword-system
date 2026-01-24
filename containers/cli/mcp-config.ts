/**
 * MCP Configuration Manager
 * Handles loading, saving, and managing MCP server configurations
 */

import * as fs from 'fs/promises'
import * as path from 'path'
import * as os from 'os'
import { McpConfig, McpServer, McpServerHeader } from './mcp-types'

const CONFIG_DIR = path.join(os.homedir(), '.mrliouword')
const CONFIG_FILE = path.join(CONFIG_DIR, 'mcp-config.json')

export class McpConfigManager {
  /**
   * Ensure configuration directory exists
   */
  private async ensureConfigDir(): Promise<void> {
    try {
      await fs.mkdir(CONFIG_DIR, { recursive: true })
    } catch (error) {
      // Directory already exists
    }
  }

  /**
   * Load MCP configuration from file
   */
  async load(): Promise<McpConfig> {
    await this.ensureConfigDir()
    
    try {
      const content = await fs.readFile(CONFIG_FILE, 'utf-8')
      return JSON.parse(content)
    } catch (error) {
      // Config file doesn't exist, return empty config
      return { servers: [] }
    }
  }

  /**
   * Save MCP configuration to file
   */
  async save(config: McpConfig): Promise<void> {
    await this.ensureConfigDir()
    await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8')
  }

  /**
   * Add a new MCP server
   */
  async addServer(url: string, headers?: McpServerHeader[]): Promise<void> {
    const config = await this.load()
    
    // Check if server already exists
    const existingIndex = config.servers.findIndex(s => s.url === url)
    
    const server: McpServer = {
      url,
      headers: headers || [],
      addedAt: new Date().toISOString()
    }
    
    if (existingIndex >= 0) {
      // Update existing server
      config.servers[existingIndex] = server
    } else {
      // Add new server
      config.servers.push(server)
    }
    
    await this.save(config)
  }

  /**
   * Remove an MCP server by URL
   */
  async removeServer(url: string): Promise<boolean> {
    const config = await this.load()
    const initialLength = config.servers.length
    config.servers = config.servers.filter(s => s.url !== url)
    
    if (config.servers.length < initialLength) {
      await this.save(config)
      return true
    }
    return false
  }

  /**
   * List all MCP servers
   */
  async listServers(): Promise<McpServer[]> {
    const config = await this.load()
    return config.servers
  }

  /**
   * Get config file path
   */
  getConfigPath(): string {
    return CONFIG_FILE
  }
}
