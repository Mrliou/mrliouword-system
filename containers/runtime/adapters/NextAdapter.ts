/**
 * Next.js Platform Adapter
 * Origin Signature: MrLiouWord
 */

export class NextAdapter {
  async create(adapterConfig: any): Promise<any> {
    console.log('🔧 Creating Next.js runtime adapter');
    return {
      type: 'next',
      config: adapterConfig
    };
  }
}
