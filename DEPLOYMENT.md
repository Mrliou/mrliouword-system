# MrLiouWord System - Deployment Guide

This guide explains how to set up and deploy the MrLiouWord System to Cloudflare Workers.

## Prerequisites

Before you can deploy this system, you need:

1. **Node.js** (v18 or later)
2. **npm** (comes with Node.js)
3. **A Cloudflare account** with Workers enabled
4. **GitHub repository secrets configured** (for automated deployment)

## Required GitHub Secrets

For the automated CI/CD workflow to deploy to Cloudflare Workers, you must configure the following secrets in your GitHub repository:

### Setting Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

#### `CLOUDFLARE_API_TOKEN`

**Required**: Yes

**Description**: API token for authenticating with Cloudflare.

**How to get it**:
1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to **My Profile** → **API Tokens**
3. Click **Create Token**
4. Use the **Edit Cloudflare Workers** template or create a custom token with the following permissions:
   - Account → Workers Scripts → Edit
   - Account → Workers KV Storage → Edit
   - Account → D1 → Edit
   - Account → R2 → Edit
5. Copy the generated token and add it as a GitHub secret

#### `CLOUDFLARE_ACCOUNT_ID`

**Required**: Yes

**Description**: Your Cloudflare account ID.

**How to get it**:
1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select any website (or go to Workers & Pages)
3. Find your Account ID in the right sidebar
4. Copy the Account ID and add it as a GitHub secret

#### `NOTION_TOKEN` (Optional)

**Required**: Only if you want to use Notion integration

**Description**: Integration token for syncing with Notion.

**How to get it**:
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the Internal Integration Token
4. Share your Notion database with the integration

## Cloudflare Resources Setup

Before deploying, ensure you have created the following resources in your Cloudflare account:

### KV Namespaces

1. **mrliouword-vault**
   - Purpose: Memory chain storage
   - Binding: `MRLIOUWORD_VAULT`
   - ID: Update in `cloudflare/mrliouword-private/wrangler.jsonc`

2. **particle-auth-vault** (if using auth gateway)
   - Purpose: Authentication token storage
   - Binding: `PARTICLE_AUTH_VAULT`

### D1 Database

1. **mrliouword-db**
   - Purpose: Structured queries
   - Binding: `MRLIOUWORD_DB`
   - Database ID: Update in `cloudflare/mrliouword-private/wrangler.jsonc`

### R2 Bucket

1. **mrlioubook**
   - Purpose: File storage
   - Binding: `MRLIOUBOOK`

### Creating Resources via Wrangler CLI

```bash
# Install Wrangler globally
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create KV namespace
wrangler kv:namespace create "MRLIOUWORD_VAULT"

# Create D1 database
wrangler d1 create mrliouword-db

# Create R2 bucket
wrangler r2 bucket create mrlioubook
```

After creating these resources, update the IDs in `cloudflare/mrliouword-private/wrangler.jsonc`.

## Manual Deployment

If you want to deploy manually instead of using GitHub Actions:

```bash
# Navigate to the worker directory
cd cloudflare/mrliouword-private

# Install dependencies
npm install

# Deploy to Cloudflare
npx wrangler deploy
```

You'll be prompted to log in to Cloudflare if you haven't already.

## Automated Deployment

The system uses GitHub Actions for automated deployment. The workflow is triggered:

- **Automatically**: On every push to the `main` branch
- **Manually**: Via workflow dispatch

### Workflow Jobs

1. **Deploy to Cloudflare Workers**: Deploys the `mrliouword-private` worker
2. **Generate Documentation**: Updates system status documentation
3. **Sync to Notion**: (Optional) Syncs particle dictionary to Notion

## Troubleshooting

### "CLOUDFLARE_API_TOKEN environment variable is required"

**Cause**: The GitHub secret `CLOUDFLARE_API_TOKEN` is not configured or is empty.

**Solution**: Follow the steps above to create and add the Cloudflare API token to GitHub secrets.

### "KV namespace not found"

**Cause**: The KV namespace ID in `wrangler.jsonc` doesn't match an existing namespace in your account.

**Solution**: Create the KV namespace using `wrangler kv:namespace create` and update the ID in `wrangler.jsonc`.

### "Database not found"

**Cause**: The D1 database ID in `wrangler.jsonc` doesn't match an existing database.

**Solution**: Create the D1 database using `wrangler d1 create` and update the ID in `wrangler.jsonc`.

## Verification

After deployment, you can verify the system is working:

```bash
# Check the root endpoint
curl https://mrliouword-private.mrliou.workers.dev/

# Check system status
curl https://mrliouword-private.mrliou.workers.dev/status

# Check frequencies
curl https://mrliouword-private.mrliou.workers.dev/frequencies
```

Expected response format:
```json
{
  "name": "MrliouWord Private AI Server",
  "version": "2.0.0",
  "philosophy": "怎麼過去，就怎麼回來",
  "endpoints": ["GET /status", "POST /wake", "..."],
  "origin": "MrLiouWord"
}
```

## Additional Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

**MR.liou © 2026 | 怎麼過去，就怎麼回來**
