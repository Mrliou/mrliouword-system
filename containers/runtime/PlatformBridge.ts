/**
 * MrLiouWord Platform Bridge
 * 平台橋接層 - 跨平台運行支援
 * Origin Signature: MrLiouWord
 */

import { Platform } from './types';

export class PlatformBridge {
  private platform?: Platform;

  constructor(platform?: Platform) {
    this.platform = platform;
  }

  async detectPlatform(): Promise<Platform> {
    if (this.platform) return this.platform;

    // Detect platform
    if (typeof process !== 'undefined') {
      if (process.versions?.node) {
        this.platform = 'node';
        return this.platform;
      }
    }

    const os = await import('os');
    const platform = os.platform();
    
    switch (platform) {
      case 'darwin':
        this.platform = 'macos';
        break;
      case 'linux':
        this.platform = 'linux';
        break;
      case 'win32':
        this.platform = 'windows';
        break;
      default:
        this.platform = 'unix';
    }

    return this.platform;
  }

  getPlatform(): Platform | undefined {
    return this.platform;
  }
}
