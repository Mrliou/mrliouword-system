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
import { spawn } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

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
    console.log('🚀 Initializing MrLiouWord Runtime...');
    const runtime = new UniversalRuntime();
    await runtime.init();
    console.log('✅ Runtime initialized');
    console.log('Origin Signature: MrLiouWord');
  });

// load 命令
program
  .command('load <container>')
  .description('載入 .flpkg 容器')
  .option('-l, --layer <layer>', 'Target layer', 'L3')
  .action(async (container, options) => {
    console.log(`📦 Loading container: ${container}`);
    const runtime = new UniversalRuntime();
    await runtime.init();
    await runtime.load(container, options.layer);
  });

// spawn 命令
program
  .command('spawn')
  .description('啟動 MetaEnv 沙盒')
  .option('--cpu <cpu>', 'CPU cores', '4')
  .option('--ram <ram>', 'RAM size', '8G')
  .option('--gpu <gpu>', 'GPU count', '0')
  .action(async (options) => {
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
  });

// health 命令
program
  .command('health')
  .description('檢查系統健康狀態')
  .option('--env-id <id>', 'Environment ID to check')
  .action(async (options) => {
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
  });

// reverse-mine 命令
program
  .command('reverse-mine')
  .description('執行反推分析，從 trace 檔案產生規則')
  .option('--trace-fs <file>', 'trace_fs.csv 檔案路徑', 'trace_fs.csv')
  .option('--trace-ops <file>', 'trace_ops.csv 檔案路徑', 'trace_ops.csv')
  .option('--output <file>', '輸出檔案路徑', 'rules.yaml')
  .action(async (options) => {
    console.log('🔍 Running reverse analysis...');
    
    if (!options.traceFs || !options.traceOps) {
      console.error('❌ Error: --trace-fs and --trace-ops are required');
      process.exit(1);
    }
    
    console.log(`Input: ${options.traceFs}, ${options.traceOps}`);
    console.log(`Output: ${options.output}`);
    
    try {
      // 調用 Python TraceMiner
      // From dist/cli/mrliou-runtime.js, go back to containers/reverse-engine
      const scriptPath = path.join(__dirname, '..', '..', 'reverse-engine', 'TraceMiner.py');
      const pythonCmd = `python3 "${scriptPath}" "${options.traceFs}" "${options.traceOps}"`;
      
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
