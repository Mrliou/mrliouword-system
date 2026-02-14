# MCP Server Management

<!-- origin_signature: MrLiouWord -->

This document describes how to manage Model Context Protocol (MCP) servers using the mrliou-runtime CLI.

## Overview

The `copilot mcp` commands allow you to configure MCP servers with custom headers for authentication. This is useful when you need to connect to MCP servers that require API keys, bearer tokens, or other custom headers.

## Commands

### Add an MCP Server

Add a new MCP server to your configuration:

```bash
mrliou-runtime copilot mcp add <URL> [--header "Key=Value"]
```

**Arguments:**
- `<URL>`: The URL of the MCP server (required)

**Options:**
- `--header <header>`: Add a custom header in the format "Key=Value". This option can be used multiple times to add multiple headers.

**Examples:**

Add an MCP server with an authorization header:
```bash
mrliou-runtime copilot mcp add https://api.example.com/mcp --header "Authorization=Bearer token123"
```

Add an MCP server with multiple headers:
```bash
mrliou-runtime copilot mcp add https://api.example.com/mcp \
  --header "Authorization=Bearer token123" \
  --header "X-API-Key=secret456" \
  --header "Content-Type=application/json"
```

Add an MCP server without headers:
```bash
mrliou-runtime copilot mcp add https://public.example.com/mcp
```

**Note:** Sensitive header values (those containing "auth" or "token" in the key name) are automatically masked in the output for security.

### List MCP Servers

View all configured MCP servers:

```bash
mrliou-runtime copilot mcp list
```

This command displays:
- The URL of each server
- When it was added
- Any configured headers (with sensitive values masked)

**Example output:**
```
📋 Configured MCP servers:

1. https://api.example.com/mcp
   Added: 1/24/2026, 11:05:33 AM
   Headers:
     Authorization: ***
     X-API-Key: secret456
```

### Remove an MCP Server

Remove an MCP server from your configuration:

```bash
mrliou-runtime copilot mcp remove <URL>
```

**Arguments:**
- `<URL>`: The URL of the MCP server to remove (required)

**Example:**
```bash
mrliou-runtime copilot mcp remove https://api.example.com/mcp
```

## Configuration Storage

MCP server configurations are stored in:
```
~/.mrliouword/mcp-config.json
```

The configuration file contains:
- Server URLs
- Headers (including authentication tokens)
- Timestamps for when servers were added

**Security Note:** The configuration file contains sensitive information like API keys and tokens. Ensure proper file permissions are set on this file.

## Header Format

Headers must be specified in the format `Key=Value`:
- The key and value are separated by the first `=` sign
- Everything after the first `=` is treated as the value
- Spaces are preserved in both key and value

**Valid header formats:**
```bash
--header "Authorization=Bearer token123"
--header "X-API-Key=my-secret-key"
--header "Content-Type=application/json"
--header "Custom-Header=value with spaces"
```

**Invalid header formats:**
```bash
--header "InvalidHeader"  # Missing '=' separator
```

## Error Handling

The CLI provides clear error messages for common issues:

- **Invalid header format:** If a header is not in the "Key=Value" format, the command will fail with an error message explaining the expected format.

- **Server not found:** When removing a server, if the URL is not in the configuration, the command will fail with an appropriate message.

- **Permission issues:** If the configuration file cannot be created or written, an error will be displayed.

## Use Cases

### Private MCP Servers

When connecting to private MCP servers that require authentication:
```bash
mrliou-runtime copilot mcp add https://internal.company.com/mcp \
  --header "Authorization=Bearer eyJhbGc..."
```

### API Key Authentication

For services that use API key authentication:
```bash
mrliou-runtime copilot mcp add https://api.service.com/mcp \
  --header "X-API-Key=your-api-key-here"
```

### Multiple Authentication Methods

Some servers may require multiple authentication headers:
```bash
mrliou-runtime copilot mcp add https://secure.example.com/mcp \
  --header "Authorization=Bearer token123" \
  --header "X-Client-ID=client-id" \
  --header "X-Tenant-ID=tenant-id"
```

## Testing

Run the test suite to verify MCP configuration management:

```bash
node containers/dist/cli/mcp-config.test.js
```

The test suite verifies:
- Adding servers with headers
- Adding multiple headers
- Removing servers
- Updating existing servers
- Configuration persistence
