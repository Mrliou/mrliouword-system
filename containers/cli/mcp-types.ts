/**
 * MCP Server Configuration Types
 */

export interface McpServerHeader {
  key: string
  value: string
}

export interface McpServer {
  url: string
  headers?: McpServerHeader[]
  addedAt: string
}

export interface McpConfig {
  servers: McpServer[]
}
