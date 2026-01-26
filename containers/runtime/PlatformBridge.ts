/**
 * MrLiouWord Platform Bridge
 * 平台橋接層 - 跨平台運行支援
 * Origin Signature: MrLiouWord
 */

export class PlatformBridge {
  private platform?: string;

  constructor(platform?: string) {
    this.platform = platform;
  }

  async detectPlatform(): Promise<string> {
    if (this.platform) return this.platform;

    // Detect platform
    if (typeof process !== 'undefined') {
      if (process.versions?.node) {
        this.platform = 'node';
      }
    }

    if (typeof globalThis !== 'undefined' && 'window' in globalThis) {
      this.platform = 'browser';
    }

    if (!this.platform) {
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
    }

    return this.platform;
  }

  getPlatform(): string {
    return this.platform || 'unknown';
  }
}
