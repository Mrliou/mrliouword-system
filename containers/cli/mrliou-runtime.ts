#!/usr/bin/env node

import { Command } from 'commander';
import { UniversalRuntime } from '../runtime/UniversalRuntime';
import { MetaEnvController } from '../metaenv/MetaEnvController';

const program = new Command();

program
  .name('mrliou-runtime')
  .description('MrLiouWord Universal Container Runtime')
  .version('1.0.0');

program
  .command('init')
  .description('Initialize runtime')
  .action(async () => {
    const runtime = new UniversalRuntime();
    await runtime.init();
  });

program
  .command('load <container>')
  .description('Load a container')
  .option('-l, --layer <layer>', 'Target layer', 'L3')
  .action(async (container, options) => {
    const runtime = new UniversalRuntime();
    await runtime.init();
    await runtime.load(container, options.layer);
  });

program
  .command('spawn')
  .description('Spawn MetaEnv')
  .option('--cpu <cpu>', 'CPU cores', '4')
  .option('--ram <ram>', 'RAM size', '8G')
  .option('--gpu <gpu>', 'GPU count', '0')
  .action(async (options) => {
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

program.parse();
