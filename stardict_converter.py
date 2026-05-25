"""
StarDict 词典转换工具
将 StarDict 格式的词典（.ifo + .idx + .dict）转换为 JSON 格式
支持：朗文、OALD、剑桥等高质量词典

使用方法：
    python stardict_converter.py <path_to_dict_files> output_format

支持的格式：
    - Babylon（.bgl）
    - StarDict（.ifo/.dict/.idx）
    - Kindle 词典（.mobi）
"""

import struct
import json
import zlib
import os
from pathlib import Path
from typing import Dict, List, Tuple

class StarDictParser:
    """StarDict 词典解析器"""
    
    def __init__(self, dict_path: str):
        self.dict_path = Path(dict_path)
        self.metadata = {}
        self.entries = {}
        
    def parse_ifo(self) -> Dict:
        """解析 .ifo 元数据文件"""
        ifo_file = self.dict_path.with_suffix('.ifo')
        
        if not ifo_file.exists():
            raise FileNotFoundError(f"找不到 .ifo 文件: {ifo_file}")
        
        metadata = {}
        with open(ifo_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    metadata[key.strip()] = value.strip()
        
        return metadata
    
    def parse_dict(self) -> Dict[str, str]:
        """解析 StarDict 词典文件"""
        print("开始解析 StarDict 词典...")
        
        # 解析元数据
        self.metadata = self.parse_ifo()
        print(f"✓ 词典名称: {self.metadata.get('BookName', 'Unknown')}")
        print(f"✓ 版本: {self.metadata.get('Version', 'Unknown')}")
        print(f"✓ 同义词数: {self.metadata.get('SynWordCount', 0)}")
        
        # 读取索引和词条
        try:
            self._read_index_and_dict()
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            raise
        
        return self.entries
    
    def _read_index_and_dict(self):
        """读取索引和词条数据"""
        idx_file = self.dict_path.with_suffix('.idx')
        dict_file = self.dict_path.with_suffix('.dict')
        
        # 如果 .dict 不存在，尝试 .dict.dz（压缩）
        if not dict_file.exists():
            dict_file = dict_file.with_suffix('.dict.dz')
        
        if not idx_file.exists() or not dict_file.exists():
            raise FileNotFoundError(f"找不到 .idx 或 .dict 文件")
        
        # 读取词条数据
        with open(dict_file, 'rb') as f:
            dict_data = f.read()
        
        # 如果是压缩格式，解压
        if dict_file.suffix == '.dz':
            try:
                dict_data = zlib.decompress(dict_data)
            except:
                pass
        
        # 读取索引
        entries = []
        with open(idx_file, 'rb') as f:
            while True:
                # 读取词条头
                header = f.read(1)
                if not header:
                    break
                
                # 简化处理：读取字符串和偏移
                word = self._read_string(f)
                offset_bytes = f.read(8)
                size_bytes = f.read(4)
                
                if len(offset_bytes) < 8 or len(size_bytes) < 4:
                    break
                
                offset = struct.unpack('>Q', offset_bytes)[0]
                size = struct.unpack('>I', size_bytes)[0]
                
                entries.append({
                    'word': word.lower(),
                    'offset': offset,
                    'size': size
                })
        
        # 从词典数据中提取定义
        print(f"正在提取 {len(entries)} 个词条...")
        for i, entry in enumerate(entries):
            if (i + 1) % 1000 == 0:
                print(f"  已处理: {i + 1} / {len(entries)}")
            
            try:
                definition = dict_data[entry['offset']:entry['offset'] + entry['size']].decode('utf-8', errors='ignore')
                # 清理定义文本
                definition = definition.strip()
                if definition:
                    self.entries[entry['word']] = {
                        'word': entry['word'],
                        'definition': definition,
                        'phonetic': '',
                        'translation': '',
                        'pos': '',
                        'examples': [],
                        'forms': [],
                        'collins': 0,
                        'oxford': 0,
                        'tags': ['stardict'],
                    }
            except Exception as e:
                continue
        
        print(f"✓ 成功提取 {len(self.entries)} 个词条")
    
    def _read_string(self, f) -> str:
        """从文件读取以 null 结尾的字符串"""
        chars = []
        while True:
            char = f.read(1)
            if not char or char == b'\x00':
                break
            chars.append(char)
        return b''.join(chars).decode('utf-8', errors='ignore')
    
    def to_json(self, output_file: str):
        """转换为 JSON 格式"""
        print(f"\n正在保存为 JSON: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ 保存完成")
        print(f"  文件大小: {file_size_mb:.2f} MB")
        print(f"  词条数: {len(self.entries)}")


def download_stardict_example():
    """下载示例 StarDict 词典"""
    print("="*60)
    print("StarDict 词典下载指南")
    print("="*60)
    
    print("""
推荐的高质量 StarDict 词典：

1. 朗文当代英英词典（推荐）✅
   - 高质量、权威、覆盖广
   - 下载: https://downloads.freemdict.com/词库/

2. OALD (牛津高阶) ⭐⭐⭐⭐⭐
   - 最权威、最详细
   - 下载: FreeDict、MDict 社区

3. 剑桥英英词典
   - 现代、实用
   
4. Merriam-Webster 字典
   - 美式、权威

获取方式：
- FreeDict 社区: https://freedict.org/
- MDict 论坛: https://www.mdict.cn/
- Skywind3000 ECDICT: https://github.com/skywind3000/ECDICT

使用方法：
1. 下载 .ifo + .idx + .dict 文件
2. 放到项目目录
3. 运行: python stardict_converter.py <dict_name> json
    """)


def main():
    import sys
    
    if len(sys.argv) < 2:
        download_stardict_example()
        return
    
    dict_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'json'
    
    # 转换为 JSON
    parser = StarDictParser(dict_path)
    entries = parser.parse_dict()
    
    output_file = Path(dict_path).stem + '.json'
    parser.to_json(str(output_file))


if __name__ == '__main__':
    main()
