"""
多词典集成管理
支持 ECDICT、StarDict、自定义词典
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

class DictionaryManager:
    """词典管理器"""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.dict_dir = self.project_root / 'dictionaries'
        self.dict_dir.mkdir(exist_ok=True)
        
    def list_available_dicts(self):
        """列出可用的词典"""
        print("="*60)
        print("可用的词典方案")
        print("="*60)
        
        # 当前使用的词典
        current_dict = self.project_root / 'dictionary.json'
        if current_dict.exists():
            size_mb = current_dict.stat().st_size / (1024*1024)
            with open(current_dict, encoding='utf-8') as f:
                entries = json.load(f)
            print(f"\n✓ 当前词典: ECDICT")
            print(f"  文件: dictionary.json")
            print(f"  词条数: {len(entries):,}")
            print(f"  大小: {size_mb:.1f} MB")
        
        # 其他词典
        print(f"\n📚 其他可用词典:")
        dicts = list(self.dict_dir.glob('*.json'))
        if dicts:
            for d in dicts:
                size_mb = d.stat().st_size / (1024*1024)
                print(f"  - {d.name} ({size_mb:.1f} MB)")
        else:
            print("  无（需要下载）")
        
        print(f"\n💡 如何添加新词典:")
        print(f"  1. 下载 StarDict 词典（.ifo + .idx + .dict）")
        print(f"  2. 放到 {self.dict_dir}/ 目录")
        print(f"  3. 运行: python dict_manager.py convert <dict_name>")
    
    def convert_stardict(self, dict_name: str) -> bool:
        """转换 StarDict 词典"""
        print(f"\n正在转换 StarDict 词典: {dict_name}")
        
        # 查找文件
        ifo_file = self.dict_dir / f"{dict_name}.ifo"
        idx_file = self.dict_dir / f"{dict_name}.idx"
        dict_file = self.dict_dir / f"{dict_name}.dict"
        
        if not ifo_file.exists():
            print(f"❌ 找不到 .ifo 文件: {ifo_file}")
            return False
        
        if not idx_file.exists():
            print(f"❌ 找不到 .idx 文件: {idx_file}")
            return False
        
        if not dict_file.exists():
            print(f"❌ 找不到 .dict 文件: {dict_file}")
            return False
        
        try:
            from stardict_converter import StarDictParser
            parser = StarDictParser(str(self.dict_dir / dict_name))
            entries = parser.parse_dict()
            
            output_file = self.dict_dir / f"{dict_name}.json"
            parser.to_json(str(output_file))
            
            print(f"✓ 转换成功: {output_file}")
            return True
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def merge_dicts(self, primary: str, secondary: str, output: str = 'dictionary_merged.json'):
        """合并两个词典（优先用 primary，缺失的用 secondary 补充）"""
        print(f"正在合并词典...")
        print(f"  主词典: {primary}")
        print(f"  备选词典: {secondary}")
        
        # 加载词典
        with open(self.project_root / primary, encoding='utf-8') as f:
            dict1 = json.load(f)
        
        dict2 = {}
        secondary_path = self.dict_dir / secondary if not (self.project_root / secondary).exists() else self.project_root / secondary
        if secondary_path.exists():
            with open(secondary_path, encoding='utf-8') as f:
                dict2 = json.load(f)
        
        # 合并
        merged = dict(dict1)
        for word, entry in dict2.items():
            if word not in merged:
                merged[word] = entry
        
        # 保存
        output_path = self.project_root / output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 合并完成: {output_path}")
        print(f"  词条数: {len(merged):,}")
        return str(output_path)
    
    def get_dict_stats(self, dict_file: str = 'dictionary.json') -> Dict:
        """获取词典统计信息"""
        dict_path = self.project_root / dict_file
        
        if not dict_path.exists():
            return {}
        
        with open(dict_path, encoding='utf-8') as f:
            entries = json.load(f)
        
        stats = {
            'total_entries': len(entries),
            'file_size_mb': dict_path.stat().st_size / (1024*1024),
            'has_examples': sum(1 for e in entries.values() if e.get('examples')),
            'has_phonetic': sum(1 for e in entries.values() if e.get('phonetic')),
            'tags_distribution': {}
        }
        
        # 统计标签
        for entry in entries.values():
            if entry.get('tags'):
                tags = entry['tags'] if isinstance(entry['tags'], list) else [entry['tags']]
                for tag in tags:
                    stats['tags_distribution'][tag] = stats['tags_distribution'].get(tag, 0) + 1
        
        return stats


def main():
    import sys
    
    manager = DictionaryManager()
    
    if len(sys.argv) < 2:
        manager.list_available_dicts()
        print(f"\n使用方法:")
        print(f"  python dict_manager.py list              # 列出词典")
        print(f"  python dict_manager.py convert <name>    # 转换 StarDict 词典")
        print(f"  python dict_manager.py merge <a> <b>     # 合并词典")
        print(f"  python dict_manager.py stats             # 统计信息")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'list':
        manager.list_available_dicts()
    
    elif cmd == 'convert' and len(sys.argv) > 2:
        manager.convert_stardict(sys.argv[2])
    
    elif cmd == 'merge' and len(sys.argv) > 3:
        manager.merge_dicts(sys.argv[2], sys.argv[3])
    
    elif cmd == 'stats':
        stats = manager.get_dict_stats()
        if stats:
            print("词典统计:")
            print(f"  词条数: {stats['total_entries']:,}")
            print(f"  文件大小: {stats['file_size_mb']:.1f} MB")
            print(f"  有例句的词: {stats['has_examples']:,}")
            print(f"  有发音的词: {stats['has_phonetic']:,}")
            if stats['tags_distribution']:
                print(f"  标签分布:")
                for tag, count in sorted(stats['tags_distribution'].items(), key=lambda x: -x[1])[:10]:
                    print(f"    {tag}: {count:,}")


if __name__ == '__main__':
    main()
