#!/usr/bin/env python3
"""
Notion Sync - MrLiouWord 粒子系統同步工具

同步內容：
- 粒子字典 → Notion 資料庫
- 記憶條目 → Notion 頁面
- 系統狀態 → Notion 儀表板

Author: MR.liou × Claude
"""

import os
import json
import argparse
from typing import Dict, List, Optional
from datetime import datetime

try:
    from notion_client import Client
except ImportError:
    print("請安裝 notion-client: pip install notion-client")
    exit(1)


class NotionSync:
    """Notion 同步器"""
    
    def __init__(self, token: str):
        self.client = Client(auth=token)
        self.workspace_name = "Mrliouword 8♾️Flowagent"
    
    def search_database(self, name: str) -> Optional[str]:
        """搜尋資料庫"""
        results = self.client.search(
            query=name,
            filter={"property": "object", "value": "database"}
        )
        if results['results']:
            return results['results'][0]['id']
        return None
    
    def search_page(self, title: str) -> Optional[str]:
        """搜尋頁面"""
        results = self.client.search(
            query=title,
            filter={"property": "object", "value": "page"}
        )
        if results['results']:
            return results['results'][0]['id']
        return None
    
    def sync_particle_dict(self, particle_dict: Dict) -> Dict:
        """同步粒子字典到 Notion"""
        db_id = self.search_database("粒子字典")
        
        if not db_id:
            print("找不到粒子字典資料庫，跳過同步")
            return {"synced": 0, "skipped": len(particle_dict.get('particles', {}))}
        
        synced = 0
        for fx_code, particle in particle_dict.get('particles', {}).items():
            try:
                self.client.pages.create(
                    parent={"database_id": db_id},
                    properties={
                        "名稱": {"title": [{"text": {"content": particle['hv']}}]},
                        "fx_code": {"rich_text": [{"text": {"content": fx_code}}]},
                        "領域": {"select": {"name": particle['dom']}},
                        "動作": {"rich_text": [{"text": {"content": particle['act']}}]},
                        "能量": {"number": particle['nrg']}
                    }
                )
                synced += 1
            except Exception as e:
                print(f"同步 {fx_code} 失敗: {e}")
        
        return {"synced": synced, "total": len(particle_dict.get('particles', {}))}
    
    def sync_memory_entry(self, entry: Dict) -> bool:
        """同步記憶條目"""
        page_id = self.search_page("記憶日誌")
        
        if not page_id:
            print("找不到記憶日誌頁面")
            return False
        
        try:
            self.client.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "icon": {"emoji": "💭"},
                            "rich_text": [
                                {"text": {"content": f"[{entry.get('layer', 'L7')}] {entry.get('content', '')[:200]}"}}
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"text": {"content": f"SimHash: {entry.get('simhash', '')} | Merkle: {entry.get('merkle', '')[:16]}..."}}
                            ]
                        }
                    }
                ]
            )
            return True
        except Exception as e:
            print(f"同步記憶失敗: {e}")
            return False
    
    def create_status_page(self, status: Dict) -> str:
        """創建狀態頁面"""
        page_id = self.search_page("系統狀態")
        
        if not page_id:
            print("找不到系統狀態頁面，將創建新頁面")
            # 這裡需要指定父頁面 ID
            return ""
        
        try:
            # 更新頁面內容
            self.client.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"text": {"content": f"狀態更新 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]
                        }
                    },
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "language": "json",
                            "rich_text": [{"text": {"content": json.dumps(status, indent=2, ensure_ascii=False)}}]
                        }
                    }
                ]
            )
            return page_id
        except Exception as e:
            print(f"更新狀態失敗: {e}")
            return ""


def main():
    parser = argparse.ArgumentParser(description='MrLiouWord Notion 同步工具')
    parser.add_argument('--token', help='Notion API Token', default=os.getenv('NOTION_TOKEN'))
    parser.add_argument('--workspace', help='工作區名稱', default='Mrliouword')
    parser.add_argument('--sync-dict', action='store_true', help='同步粒子字典')
    parser.add_argument('--dict-file', help='粒子字典 JSON 檔案', default='../core/particle_dict.json')
    
    args = parser.parse_args()
    
    if not args.token:
        print("請提供 Notion API Token (--token 或 NOTION_TOKEN 環境變數)")
        return
    
    sync = NotionSync(args.token)
    
    if args.sync_dict:
        with open(args.dict_file, 'r', encoding='utf-8') as f:
            particle_dict = json.load(f)
        
        result = sync.sync_particle_dict(particle_dict)
        print(f"同步完成: {result}")


if __name__ == '__main__':
    main()
