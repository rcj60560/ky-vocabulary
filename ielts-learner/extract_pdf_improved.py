import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "src" / "data" / "words.json"
STATS_PATH = Path(__file__).parent / "pdf_stats.md"

# 章节名称
CHAPTER_NAMES = {
    1: "自然地理", 2: "植物研究", 3: "动物保护", 4: "太空探索",
    5: "学校教育", 6: "科技发明", 7: "文化历史", 8: "语言演化",
    9: "娱乐运动", 10: "物品材料", 11: "时尚潮流", 12: "饮食健康",
    13: "建筑场所", 14: "交通旅行", 15: "国家政府", 16: "社会经济",
    17: "法律法规", 18: "沙场争锋", 19: "社会角色", 20: "行为动作",
    21: "身心健康", 22: "时间日期",
}


def extract_words_improved(pdf_path: Path, start_page: int = 12):
    """
    改进的 PDF 提取方法：
    1. 正确处理双列排版
    2. 精确提取单词的完整信息
    3. 统计每页的单词数量
    """
    words = []
    chapters = []

    current_chapter = 1
    word_id = 1
    page_stats = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        print(f"总页数: {total_pages}")

        for page_num in range(start_page, total_pages):
            page = pdf.pages[page_num]

            # 获取页面尺寸
            bbox = page.bbox
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            mid_x = bbox[0] + width / 2

            # 获取完整的文本
            full_text = page.extract_text()

            if not full_text:
                continue

            lines = full_text.split('\n')

            # 检测新章节标题
            chapter_match = None
            for line in lines:
                chapter_match = re.search(r'Chapter\s+(\d+)', line, re.IGNORECASE)
                if chapter_match:
                    chapter_num = int(chapter_match.group(1))
                    current_chapter = chapter_num

                    if chapter_num not in [c['id'] for c in chapters]:
                        full_name = CHAPTER_NAMES.get(chapter_num, f'Chapter {chapter_num}')
                        chapters.append({
                            'id': chapter_num,
                            'name': f'Chapter {chapter_num}: {full_name}',
                            'startIndex': len(words),
                            'wordCount': 0,
                        })
                    print(f"\n发现章节: Chapter {chapter_num} - {full_name}")
                    break

            # 尝试使用 crop 提取左右列（如果支持）
            try:
                # 左列：左侧到中线
                left_bbox = (bbox[0], bbox[1], mid_x - 20, bbox[3])
                left_page = page.crop(left_bbox)
                left_text = left_page.extract_text() or ""

                # 右列：中线到右侧
                right_bbox = (mid_x + 20, bbox[1], bbox[2], bbox[3])
                right_page = page.crop(right_bbox)
                right_text = right_page.extract_text() or ""

                # 处理左列
                if left_text:
                    page_words = parse_text_block(left_text, current_chapter, word_id)
                    words.extend(page_words)
                    word_id += len(page_words)

                # 处理右列
                if right_text:
                    page_words = parse_text_block(right_text, current_chapter, word_id)
                    words.extend(page_words)
                    word_id += len(page_words)

            except Exception as e:
                # 如果 crop 失败，使用全文解析
                print(f"  警告: 第 {page_num + 1} 页 crop 失败，使用全文解析: {e}")
                page_words = parse_text_block(full_text, current_chapter, word_id)
                words.extend(page_words)
                word_id += len(page_words)

            # 统计本页单词数（属于当前章节）
            page_word_count = len([w for w in words if w.get('chapter') == current_chapter])
            page_stats.append({
                'page': page_num + 1,
                'chapter': current_chapter,
                'word_count': page_word_count,
            })

            if (page_num + 1) % 10 == 0:
                print(f"  处理进度: {page_num + 1}/{total_pages} 页")

    # 更新章节信息
    for chapter in chapters:
        chapter_words = [w for w in words if w['chapter'] == chapter['id']]
        if chapter_words:
            chapter['endIndex'] = chapter_words[-1]['index']
            chapter['wordCount'] = len(chapter_words)

    return words, chapters, page_stats


def parse_text_block(text: str, chapter: int, start_id: int) -> List[Dict]:
    """
    解析文本块，提取单词的完整信息
    """
    words = []
    current_word = None
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue

        # 跳过页码
        if re.match(r'^\d{3}$', line):
            continue
        if '雅思词汇' in line or 'IELTS' in line:
            continue
        if 'Chapter' in line and re.search(r'Chapter\s+\d+', line, re.IGNORECASE):
            continue

        # 检测单词行（格式：word /phonetic/）
        word_phonetic_match = re.match(r'^([a-zA-Z][a-zA-Z\'\-]+)\s*/([^/]+)/', line)
        if word_phonetic_match:
            # 保存前一个单词
            if current_word:
                words.append(current_word)

            # 开始新单词
            word = word_phonetic_match.group(1)
            phonetic = '/' + word_phonetic_match.group(2)

            # 确保音标以 / 结尾
            if not phonetic.endswith('/'):
                phonetic += '/'

            current_word = {
                'id': str(start_id + len(words)),
                'word': word,
                'phonetic': phonetic,
                'partOfSpeech': None,
                'chapter': chapter,
                'index': 0,
                'definitions': [],
                'examples': [],
                'collocations': [],
                'word_root': [],
            }

        # 处理词性
        elif current_word and re.match(r'^[a-z]+\.$', line.strip(), re.IGNORECASE):
            current_word['partOfSpeech'] = line.strip()

        # 处理释义（中文为主）
        elif current_word and re.search(r'[一-鿯]', line):
            # 提取中文释义
            meaning = re.sub(r'[a-zA-Z0-9]', '', line).strip()
            meaning = re.sub(r'\s+', ' ', meaning)
            # 移除多余的标点
            meaning = re.sub(r'[^一-鿿　-〿＀-￯\s;；，、。：！？""''（）【】]', '', meaning)
            if meaning and len(meaning) > 1:
                current_word['definitions'].append({
                    'part': current_word['partOfSpeech'] or '',
                    'meaning': meaning,
                })

        # 处理例句（英文句子）
        elif current_word and re.search(r'[A-Z][a-z]{8,}', line):
            # 提取英文句子
            sentences = re.findall(r'[A-Z][^.!?]*[.!?]', line)
            for sentence in sentences:
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 15:
                    current_word['examples'].append(clean_sentence)

        # 处理搭配
        elif current_word and re.search(r'[a-z]{3,}(?: [a-z]{3,})+', line, re.IGNORECASE):
            collocations = re.findall(r'[a-z]{3,}(?: [a-z]{3,})+', line, re.IGNORECASE)
            for col in collocations:
                clean_col = col.strip()
                if len(clean_col) < 30 and '.' not in clean_col and ',' not in clean_col:
                    if not current_word['examples'] or clean_col not in ' '.join(current_word['examples']):
                        current_word['collocations'].append(clean_col)

        # 处理词根词源（包含"+"或"—"或"（）"等）
        elif current_word and (re.search(r'[+—（）\(\)]', line) or re.search(r'词根|词源|起源', line)):
            word_root = line.strip()
            if word_root and len(word_root) > 3:
                current_word['word_root'].append(word_root)

    # 保存最后一个单词
    if current_word:
        words.append(current_word)

    # 设置索引
    for i, word in enumerate(words):
        word['index'] = start_id + i - 1

    return words


def generate_stats_report(words: List, chapters: List, page_stats: List, output_path: Path):
    """生成统计报告"""
    from datetime import datetime

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 雅思词汇真经 PDF 提取统计报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 总体统计\n\n")
        f.write(f"- **总单词数**: {len(words)}\n")
        f.write(f"- **总章节数**: {len(chapters)}\n")
        f.write(f"- **总页数**: {len(page_stats)}\n")
        f.write(f"- **平均每页单词数**: {len(words) / len(page_stats) if page_stats else 0:.1f}\n\n")

        f.write("## 章节统计\n\n")
        f.write("| 章节 | 名称 | 单词数 | 占比 |\n")
        f.write("|------|------|--------|------|\n")
        for chapter in chapters:
            percentage = (chapter['wordCount'] / len(words) * 100) if words else 0
            f.write(f"| Chapter {chapter['id']} | {chapter['name']} | {chapter['wordCount']} | {percentage:.1f}% |\n")

        f.write("\n## 页面统计（前20页）\n\n")
        f.write("| 页码 | 章节 | 单词数 |\n")
        f.write("|------|------|--------|\n")
        for stat in page_stats[:20]:
            f.write(f"| {stat['page']} | Chapter {stat['chapter']} | {stat['word_count']} |\n")

        f.write("\n## 问题与改进\n\n")
        f.write("### 已识别的问题\n\n")
        f.write("1. 部分单词的释义可能包含其他单词的内容（由于双列排版问题）\n")
        f.write("2. 某些页码可能被误识别为单词\n")
        f.write("3. 词根词源提取可能不完整\n")
        f.write("4. 部分章节可能单词数量偏少，需要进一步优化解析逻辑\n\n")

        f.write("### 改进建议\n\n")
        f.write("1. 使用更精确的页面裁切来分离左右列\n")
        f.write("2. 增加对页码、页眉页脚的过滤\n")
        f.write("3. 改进词根词源的识别模式\n")
        f.write("4. 考虑使用 PDF 表格提取功能来获取结构化数据\n\n")


def main():
    if not PDF_PATH.exists():
        print(f"错误: 找不到 PDF 文件: {PDF_PATH}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"开始提取词库: {PDF_PATH}\n")

    words, chapters, page_stats = extract_words_improved(PDF_PATH, start_page=12)

    # 保存为 JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({'words': words, 'chapters': chapters}, f, ensure_ascii=False, indent=2)

    # 复制到 public/data/
    public_path = Path(__file__).parent / "public" / "data"
    public_path.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(OUTPUT_PATH, public_path / "words.json")

    # 生成统计报告
    generate_stats_report(words, chapters, page_stats, STATS_PATH)

    print(f"\n{'='*60}")
    print(f"提取完成！")
    print(f"{'='*60}")
    print(f"总单词数: {len(words)}")
    print(f"总章节数: {len(chapters)}")
    print(f"输出文件:")
    print(f"  - {OUTPUT_PATH}")
    print(f"  - {public_path / 'words.json'}")
    print(f"  - {STATS_PATH}")

    print(f"\n章节统计:")
    for chapter in chapters:
        print(f"  Chapter {chapter['id']}: {chapter['wordCount']} 个单词")


if __name__ == '__main__':
    main()