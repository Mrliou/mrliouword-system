#!/usr/bin/env node
/**
 * MrLiouWord Runtime CLI
 * 統一容器運行時命令行工具
 * 
 * Origin Signature: MrLiouWord
 */

import { Command } from 'commander';
import { UniversalRuntime } from '../runtime/UniversalRuntime';
import { MetaEnvController } from '../metaenv/MetaEnvController';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const exec = promisify(require('child_process').exec);

const program = new Command();

program
  .name('mrliou-runtime')
  .description('MrLiouWord 統一容器運行時 CLI')
  .version('1.0.0');

// init 命令
program
  .command('init')
  .description('初始化運行時環境')
  .action(async () => {
    try {
      console.log('🚀 Initializing MrLiouWord Runtime...');
      const runtime = new UniversalRuntime();
      await runtime.init();
      console.log('✅ Runtime initialized');
      console.log('Origin Signature: MrLiouWord');
    } catch (error: any) {
      console.error('❌ Error initializing runtime:', error.message);
      process.exit(1);
    }
  });

// load 命令
program
  .command('load <container>')
  .description('載入 .flpkg 容器')
  .option('-l, --layer <layer>', 'Target layer', 'L3')
  .action(async (container, options) => {
    try {
      console.log(`📦 Loading container: ${container}`);
      
      // Validate file exists
      if (!fs.existsSync(container)) {
        console.error(`❌ Error: Container file not found: ${container}`);
        process.exit(1);
      }
      
      const runtime = new UniversalRuntime();
      await runtime.init();
      await runtime.load(container, options.layer);
      console.log(`✅ Container loaded successfully to ${options.layer}`);
    } catch (error: any) {
      console.error('❌ Error loading container:', error.message);
      process.exit(1);
    }
  });

// spawn 命令
program
  .command('spawn')
  .description('啟動 MetaEnv 沙盒')
  .option('--cpu <cpu>', 'CPU cores', '4')
  .option('--ram <ram>', 'RAM size', '8G')
  .option('--gpu <gpu>', 'GPU count', '0')
  .action(async (options) => {
    try {
      console.log('🚀 Spawning MetaEnv...');
      const controller = new MetaEnvController();
      const result = await controller.spawn({
        shape: {
          cpu: parseInt(options.cpu),
          ram: options.ram,
          gpu: parseInt(options.gpu)
        }
      });
      console.log('✅ Spawned:', result);
    } catch (error: any) {
      console.error('❌ Error spawning MetaEnv:', error.message);
      process.exit(1);
    }
  });

// health 命令
program
  .command('health')
  .description('檢查系統健康狀態')
  .option('--env-id <id>', 'Environment ID to check')
  .action(async (options) => {
    try {
      console.log('🏥 Checking system health...');
      
      const controller = new MetaEnvController();
      const health = await controller.health(options.envId);
      
      console.log('✅ System healthy');
      console.log(`Time: ${health.time}`);
      if (health.env_id) {
        console.log(`Environment: ${health.env_id}`);
        console.log(`Status: ${health.status}`);
      } else {
        console.log(`Total Environments: ${health.environments || 0}`);
      }
    } catch (error: any) {
      console.error('❌ Error checking health:', error.message);
      process.exit(1);
    }
  });

// reverse-mine 命令
program
  .command('reverse-mine')
  .description('執行反推分析，從 trace 檔案產生規則')
  .requiredOption('--trace-fs <file>', 'trace_fs.csv 檔案路徑')
  .requiredOption('--trace-ops <file>', 'trace_ops.csv 檔案路徑')
  .option('--output <file>', '輸出檔案路徑', 'rules.yaml')
  .action(async (options) => {
    try {
      console.log('🔍 Running reverse analysis...');
      
      // Validate input files exist
      if (!fs.existsSync(options.traceFs)) {
        console.error(`❌ Error: trace_fs file not found: ${options.traceFs}`);
        process.exit(1);
      }
      
      if (!fs.existsSync(options.traceOps)) {
        console.error(`❌ Error: trace_ops file not found: ${options.traceOps}`);
        process.exit(1);
      }
      
      console.log(`Input: ${options.traceFs}, ${options.traceOps}`);
      console.log(`Output: ${options.output}`);
      
      // Resolve absolute paths for security
      const traceFsPath = path.resolve(options.traceFs);
      const traceOpsPath = path.resolve(options.traceOps);
      
      // Get script path (from dist/cli, go to source reverse-engine)
      const scriptPath = path.resolve(__dirname, '..', '..', 'reverse-engine', 'TraceMiner.py');
      
      // Validate script exists
      if (!fs.existsSync(scriptPath)) {
        console.error(`❌ Error: TraceMiner.py not found at: ${scriptPath}`);
        process.exit(1);
      }
      
      const pythonCmd = `python3 "${scriptPath}" "${traceFsPath}" "${traceOpsPath}"`;
      
      const { stdout, stderr } = await exec(pythonCmd);
      
      if (stdout) console.log(stdout);
      if (stderr) console.error(stderr);
      
      console.log('✅ Analysis complete');
      console.log('📄 Rules exported to', options.output);
    } catch (error: any) {
      console.error('❌ Error during reverse mining:', error.message);
      process.exit(1);
    }
  });

program.parse();
