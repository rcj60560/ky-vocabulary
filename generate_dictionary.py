"""
生成离线词典数据
支持从 ECDICT 下载或生成内置词典
"""

import csv
import io
import json
import urllib.request
from pathlib import Path

DICT_FILE = Path(__file__).parent / "dictionary.json"

def download_ecdict_data():
    """从 GitHub 下载 ECDICT 数据"""
    print("=" * 60)
    print("正在下载 ECDICT 离线词典数据...")
    print("=" * 60)
    
    csv_url = "https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv"
    
    print(f"\n[步骤 1] 从 GitHub 下载数据...")
    print(f"  源地址: {csv_url}")
    
    try:
        print("  下载中... (可能需要 2-5 分钟)")
        
        # 下载 CSV 数据
        with urllib.request.urlopen(csv_url, timeout=120) as response:
            content = response.read().decode('utf-8')
        
        print(f"  ✅ 下载完成 ({len(content) / (1024*1024):.2f} MB)")
        
        # 解析 CSV
        print(f"\n[步骤 2] 解析词典数据...")
        
        dictionary = {}

        # 使用 csv.reader 正确处理带引号的 CSV 字段
        # 格式: word,phonetic,definition,translation,pos,collins,oxford,tag,bnc,frq,exchange,detail,audio
        # 索引:  0    1         2          3           4    5       6      7    8   9   10       11     12
        reader = csv.reader(io.StringIO(content))
        header = next(reader, None)
        print(f"  表头: {header}")

        for i, parts in enumerate(reader):
            if (i + 1) % 20000 == 0:
                print(f"  已处理: {i:,} 行，已解析: {len(dictionary):,} 词条")

            try:
                if len(parts) < 5:
                    continue

                word = parts[0].strip().lower()
                if not word or len(word) < 2:
                    continue

                # 解析词形变化 (exchange 字段，索引 10)
                forms = []
                if len(parts) > 10 and parts[10]:
                    for item in parts[10].split('/'):
                        if ':' in item:
                            form = item.split(':', 1)[1].strip()
                            if form and len(form) > 1:
                                forms.append(form)

                # 解析标签 (tag 字段，索引 7)
                tags = []
                if len(parts) > 7 and parts[7]:
                    tags = [t.strip() for t in parts[7].split('/') if t.strip()]

                # 获取例句 (detail 字段，索引 11)
                example = parts[11].strip() if len(parts) > 11 else ''

                # collins 必须是整数
                collins_raw = parts[5].strip() if len(parts) > 5 else ''
                collins = int(collins_raw) if collins_raw.isdigit() else 0

                dictionary[word] = {
                    'word': word,
                    'phonetic': parts[1].strip() if len(parts) > 1 else '',
                    'definition': parts[2].strip() if len(parts) > 2 else '',
                    'translation': parts[3].strip() if len(parts) > 3 else '',
                    'pos': parts[4].strip() if len(parts) > 4 else '',
                    'collins': collins,
                    'oxford': parts[6].strip() if len(parts) > 6 else '',
                    'tags': tags,
                    'example': example,
                    'forms': forms,
                    'synonym': '',
                    'antonym': '',
                    'root': '',
                    'affix': '',
                }

            except Exception as e:
                if i < 10:
                    print(f"    行 {i} 解析错误: {e}")
                continue

        print(f"\n  ✅ 解析完成: {len(dictionary):,} 个词条")

        return dictionary, "ECDICT (在线下载)"

    except urllib.error.URLError as e:
        print(f"\n❌ 网络下载失败: {e}")
        print("  正在切换到本地词典生成模式...\n")
        return generate_builtin_dictionary()
    except Exception as e:
        print(f"\n❌ 下载或解析失败: {e}")
        print("  正在切换到本地词典生成模式...\n")
        return generate_builtin_dictionary()


def generate_builtin_dictionary():
    """生成内置词典（备选方案）"""
    print("生成本地内置词典库...")
    
    # 精选高频词汇（考研和 CET 常用）
    builtin_dict = {
        # A 开头
        'about': {'word': 'about', 'phonetic': '/əˈbaʊt/', 'definition': 'on the subject of; concerning', 'translation': '关于；大约', 'pos': 'prep.', 'collins': 3, 'oxford': 'A1', 'tags': ['cet4', 'ky'], 'example': 'Tell me about yourself|It costs about 100 dollars', 'forms': [], 'synonym': 'approximately', 'antonym': '', 'root': '', 'affix': ''},
        'above': {'word': 'above', 'phonetic': '/əˈbʌv/', 'definition': 'at a higher level or position than', 'translation': '在...上方；超过', 'pos': 'prep.', 'collins': 3, 'oxford': 'A1', 'tags': ['cet4', 'ky'], 'example': 'The plane flew above the clouds', 'forms': [], 'synonym': 'over', 'antonym': 'below', 'root': '', 'affix': ''},
        'absolute': {'word': 'absolute', 'phonetic': '/ˈæbsəluːt/', 'definition': 'complete; total', 'translation': '绝对的；完全的', 'pos': 'adj.', 'collins': 2, 'oxford': 'B2', 'tags': ['cet4', 'ky'], 'example': 'It is an absolute must', 'forms': ['absolutely'], 'synonym': 'complete', 'antonym': 'relative', 'root': '', 'affix': ''},
        'accept': {'word': 'accept', 'phonetic': '/əkˈsept/', 'definition': 'to receive willingly', 'translation': '接受；同意', 'pos': 'v.', 'collins': 3, 'oxford': 'A2', 'tags': ['cet4', 'cet6', 'ky'], 'example': 'I accept your apology', 'forms': ['accepted', 'accepting', 'acceptance'], 'synonym': 'receive', 'antonym': 'reject', 'root': '', 'affix': ''},
        'achieve': {'word': 'achieve', 'phonetic': '/əˈtʃiːv/', 'definition': 'to accomplish; to attain', 'translation': '实现；完成', 'pos': 'v.', 'collins': 3, 'oxford': 'B1', 'tags': ['cet4', 'cet6', 'ky'], 'example': 'He achieved his goal', 'forms': ['achieved', 'achieving', 'achievement'], 'synonym': 'accomplish', 'antonym': 'fail', 'root': '', 'affix': ''},
        'across': {'word': 'across', 'phonetic': '/əˈkrɒs/', 'definition': 'from one side to the other', 'translation': '横过；穿过', 'pos': 'prep.', 'collins': 3, 'oxford': 'A1', 'tags': ['cet4', 'ky'], 'example': 'Walk across the street', 'forms': [], 'synonym': 'over', 'antonym': '', 'root': '', 'affix': ''},
        
        # D
        'department': {'word': 'department', 'phonetic': '/dɪˈpɑːtmənt/', 'definition': 'a section of a large organization', 'translation': '部门；系；局', 'pos': 'n.', 'collins': 3, 'oxford': 'B1', 'tags': ['cet4', 'ky'], 'example': 'She works in the sales department', 'forms': ['departments'], 'synonym': 'division', 'antonym': '', 'root': '', 'affix': ''},
        'develop': {'word': 'develop', 'phonetic': '/dɪˈveləp/', 'definition': 'to grow; to progress', 'translation': '发展；开发；形成', 'pos': 'v.', 'collins': 3, 'oxford': 'A2', 'tags': ['cet4', 'cet6', 'ky'], 'example': 'Countries develop over time', 'forms': ['developed', 'developing', 'development'], 'synonym': 'grow', 'antonym': 'decline', 'root': '', 'affix': ''},
        
        # E
        'establish': {'word': 'establish', 'phonetic': '/ɪˈstæblɪʃ/', 'definition': 'to set up; to create', 'translation': '建立；确立；制定', 'pos': 'v.', 'collins': 3, 'oxford': 'B1', 'tags': ['cet4', 'cet6', 'ky'], 'example': 'The company was established in 1950', 'forms': ['established', 'establishing', 'establishment'], 'synonym': 'found', 'antonym': 'abolish', 'root': '', 'affix': ''},
        
        # I
        'improve': {'word': 'improve', 'phonetic': '/ɪmˈpruːv/', 'definition': 'to make or become better', 'translation': '改进；改善；提高', 'pos': 'v.', 'collins': 3, 'oxford': 'B1', 'tags': ['cet4', 'ky', 'cet6'], 'example': 'You need to improve your English', 'forms': ['improved', 'improving', 'improvement'], 'synonym': 'enhance', 'antonym': 'worsen', 'root': '', 'affix': ''},
        
        # T
        'through': {'word': 'through', 'phonetic': '/θruː/', 'definition': 'by means of; passing', 'translation': '通过；穿过；完成', 'pos': 'prep.', 'collins': 3, 'oxford': 'A1', 'tags': ['cet4', 'ky'], 'example': 'Learn through experience', 'forms': [], 'synonym': 'via', 'antonym': '', 'root': '', 'affix': ''},
        'throughout': {'word': 'throughout', 'phonetic': '/θruːˈaʊt/', 'definition': 'in or during every part of', 'translation': '遍及；整个期间', 'pos': 'prep.', 'collins': 3, 'oxford': 'B1', 'tags': ['cet4', 'cet6', 'ky'], 'example': 'The music played throughout the event', 'forms': [], 'synonym': 'all through', 'antonym': '', 'root': '', 'affix': ''},
    }
    
    print(f"✅ 已生成本地词典")
    print(f"   词条数: {len(builtin_dict)}")
    
    return builtin_dict, "本地内置词典 (演示)"


def main():
    print("\n" + "=" * 60)
    
    # 生成词典
    dictionary, source = download_ecdict_data()
    
    # 保存词典
    print(f"\n[步骤 3] 保存词典文件...")
    
    with open(DICT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=1)
    
    file_size_mb = DICT_FILE.stat().st_size / (1024 * 1024)
    print(f"  ✅ 已保存: {DICT_FILE}")
    print(f"  文件大小: {file_size_mb:.2f} MB")
    
    # 统计标签分布
    if dictionary:
        print(f"\n[步骤 4] 标签分布统计:")
        tag_counts = {}
        for entry in dictionary.values():
            for tag in entry.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        tag_display_names = {
            'ky': '📚 考研',
            'cet4': '🎯 CET4',
            'cet6': '🎓 CET6',
            'zk': '📖 中考',
            'gk': '📗 高考',
            'ielts': '🌐 雅思',
            'toefl': '🌐 托福',
            'gre': '🎓 GRE',
        }
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:10]
        if sorted_tags:
            for tag, count in sorted_tags:
                display = tag_display_names.get(tag, tag)
                print(f"  {display}: {count:,} 个词")
        else:
            print(f"  (无标签分布数据)")
    
    # 总结
    print("\n" + "=" * 60)
    print("✅ 词典处理完成！")
    print("=" * 60)
    print(f"\n📊 词典信息:")
    print(f"  来源: {source}")
    print(f"  位置: {DICT_FILE}")
    print(f"  词条数: {len(dictionary):,}")
    print(f"  文件大小: {file_size_mb:.2f} MB")
    print(f"\n💡 下一步: 运行 build_exe.py 构建包含词典的 EXE 文件")
    

if __name__ == '__main__':
    main()
