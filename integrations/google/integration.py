#!/usr/bin/env python3
"""
Google Integration - MrLiouWord 粒子系統 Google 整合

功能：
- Google Drive 檔案同步
- Google Earth KML 輸出
- Google Sheets 資料匯出

Author: MR.liou × Claude
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

# KML 生成器
class KMLGenerator:
    """Google Earth KML 生成器"""
    
    def __init__(self, name: str = "MrLiouWord Particles"):
        self.name = name
        self.particles = []
    
    def add_particle(
        self,
        title: str,
        lat: float,
        lon: float,
        alt: float = 0,
        description: str = "",
        layer: str = "L7",
        timestamp: str = None
    ):
        """添加粒子標記"""
        self.particles.append({
            "title": title,
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "description": description,
            "layer": layer,
            "timestamp": timestamp or datetime.now().isoformat()
        })
    
    def generate(self) -> str:
        """生成 KML 字串"""
        kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>{self.name}</name>
    <description>MrLiouWord 粒子立體地球儀記憶系統</description>
    
    <!-- 層級樣式 -->
    <Style id="L1"><IconStyle><color>ff0000ff</color><scale>0.8</scale></IconStyle></Style>
    <Style id="L2"><IconStyle><color>ff00ff00</color><scale>0.9</scale></IconStyle></Style>
    <Style id="L3"><IconStyle><color>ffff0000</color><scale>1.0</scale></IconStyle></Style>
    <Style id="L4"><IconStyle><color>ff00ffff</color><scale>1.1</scale></IconStyle></Style>
    <Style id="L5"><IconStyle><color>ffff00ff</color><scale>1.2</scale></IconStyle></Style>
    <Style id="L6"><IconStyle><color>ffffff00</color><scale>1.3</scale></IconStyle></Style>
    <Style id="L7"><IconStyle><color>ffffffff</color><scale>1.4</scale></IconStyle></Style>
'''
        
        for p in self.particles:
            kml += f'''
    <Placemark>
        <name>{p["title"]}</name>
        <description><![CDATA[
            層級: {p["layer"]}<br/>
            時間: {p["timestamp"]}<br/>
            {p["description"]}
        ]]></description>
        <styleUrl>#{p["layer"]}</styleUrl>
        <TimeStamp><when>{p["timestamp"]}</when></TimeStamp>
        <Point>
            <coordinates>{p["lon"]},{p["lat"]},{p["alt"]}</coordinates>
        </Point>
    </Placemark>
'''
        
        kml += '''
</Document>
</kml>'''
        return kml
    
    def save(self, filepath: str):
        """保存 KML 檔案"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate())
        print(f"KML 已保存: {filepath}")


# Google Drive 同步器（需要 google-auth 和 google-api-python-client）
class DriveSync:
    """Google Drive 同步器"""
    
    def __init__(self, credentials_file: str = None):
        self.credentials_file = credentials_file
        self.service = None
    
    def connect(self):
        """連接 Google Drive"""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            if self.credentials_file and os.path.exists(self.credentials_file):
                creds = Credentials.from_authorized_user_file(self.credentials_file)
                self.service = build('drive', 'v3', credentials=creds)
                return True
        except ImportError:
            print("請安裝 google-api-python-client: pip install google-api-python-client google-auth")
        except Exception as e:
            print(f"連接失敗: {e}")
        return False
    
    def list_files(self, folder_id: str = None, query: str = None) -> List[Dict]:
        """列出檔案"""
        if not self.service:
            return []
        
        q = query or ""
        if folder_id:
            q = f"'{folder_id}' in parents"
        
        results = self.service.files().list(
            q=q,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        return results.get('files', [])
    
    def upload_file(self, filepath: str, folder_id: str = None) -> Optional[str]:
        """上傳檔案"""
        if not self.service:
            return None
        
        from googleapiclient.http import MediaFileUpload
        
        file_metadata = {'name': os.path.basename(filepath)}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(filepath)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')


def main():
    """測試用"""
    # 建立 KML 範例
    kml = KMLGenerator("MrLiouWord 記憶地球儀")
    
    # 添加範例粒子
    kml.add_particle(
        title="系統誕生",
        lat=24.9823,
        lon=121.2481,
        description="MrLiouWord 粒子系統誕生紀念",
        layer="L7"
    )
    
    kml.add_particle(
        title="對話記錄",
        lat=25.0330,
        lon=121.5654,
        description="Claude 對話記錄",
        layer="L5"
    )
    
    # 保存
    kml.save("./mrliouword_particles.kml")
    print("KML 範例已生成")


if __name__ == '__main__':
    main()
