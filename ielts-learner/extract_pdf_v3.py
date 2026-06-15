import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "src" / "data" / "words.json"

# 章节名称映射
CHAPTER_NAMES = {
    1: "自然地理",
    2: "植物研究",
    3: "动物保护",
    4: "太空探索",
    5: "学校教育",
    6: "科技发明",
    7: "文化历史",
    8: "语言演化",
    9: "娱乐运动",
    10: "物品材料",
    11: "时尚潮流",
    12: "饮食健康",
    13: "建筑场所",
    14: "交通旅行",
    15: "国家政府",
    16: "社会经济",
    17: "法律法规",
    18: "沙场争锋",
    19: "社会角色",
    20: "行为动作",
    21: "身心健康",
    22: "时间日期",
}


def parse_word_line(line: str) -> List[Dict]:
    """
    解析单行，格式通常是：
    word1 /phonetic1/ word2 /phonetic2/
    """
    words = []

    # 匹配单词和音标: word /phonetic/
    pattern = r'(\w+(?:-\w+)*)\s*/([^/]+/?)'

    matches = re.finditer(pattern, line)

    for match in matches:
        word = match.group(1)

        # 获取音标（包括斜杠）
        phonetic_start = match.start(2)
        phonetic_end = match.end()
        phonetic = line[phonetic_start:phonetic_end]

        # 确保音标以/结尾
        if not phonetic.endswith('/'):
            # 尝试从原始行获取完整音标
            full_phonetic_match = re.search(rf'{re.escape(word)}\s*/([^/]+/)', line)
            if full_phonetic_match:
                phonetic = '/' + full_phonetic_match.group(1)
            else:
                phonetic = '/' + phonetic

        # 检查词性 (n., vt., vi., adj., adv.等)
        after_phonetic = line[match.end():]
        part_match = re.match(r'^([a-z]+\.)\s*', after_phonetic, re.IGNORECASE)

        part = None
        if part_match:
            part = part_match.group(1)

        words.append({
            'word': word,
            'phonetic': phonetic if phonetic else None,
            'partOfSpeech': part,
        })

    return words


def extract_words_from_pdf(pdf_path: Path, start_page: int = 12, max_pages: int = 300) -> Tuple[List[Dict], List[Dict]]:
    """从 PDF 提取单词"""
    words = []
    chapters = []

    current_chapter = 1
    word_id = 1

    # 待处理的单词队列（每行可能有2个单词）
    pending_words: List[Optional[Dict]] = [None, None]

    with pdfplumber.open(PDF_PATH) as pdf:
        total_pages = min(len(pdf.pages), start_page + max_pages)

        for page_num in range(start_page, total_pages):
            page = pdf.pages[page_num]
            text = page.extract_text()

            if not text:
                continue

            lines = text.split('\n')

            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # 检测新章节标题（通常在页面末尾或单独一行）
                chapter_match = re.search(r'Chapter\s+(\d+)\s*(.+)?$', line, re.IGNORECASE)
                if chapter_match:
                    chapter_num = int(chapter_match.group(1))
                    chapter_name_part = chapter_match.group(2) or ''

                    # 保存之前待处理的单词
                    for pw in pending_words:
                        if pw:
                            pw['id'] = str(word_id)
                            pw['index'] = len(words)
                            words.append(pw)
                            word_id += 1
                    pending_words = [None, None]

                    current_chapter = chapter_num

                    # 添加章节信息
                    if chapter_num not in [c['id'] for c in chapters]:
                        full_name = CHAPTER_NAMES.get(chapter_num, f'Chapter {chapter_num}')
                        chapters.append({
                            'id': chapter_num,
                            'name': f'Chapter {chapter_num}: {full_name}',
                            'startIndex': len(words),
                            'endIndex': len(words) - 1,
                            'wordCount': 0,
                        })

                    continue

                # 检测单词行（包含音标）
                word_pattern = r'\w+\s*/[^/]+/'
                if re.search(word_pattern, line):
                    # 保存之前待处理的单词
                    for pw in pending_words:
                        if pw:
                            pw['id'] = str(word_id)
                            pw['index'] = len(words)
                            words.append(pw)
                            word_id += 1
                    pending_words = [None, None]

                    # 解析新单词
                    parsed_words = parse_word_line(line)

                    # 通常每行最多2个单词
                    for i, pw in enumerate(parsed_words[:2]):
                        pending_words[i] = {
                            'word': pw['word'],
                            'phonetic': pw['phonetic'],
                            'partOfSpeech': pw['partOfSpeech'],
                            'chapter': current_chapter,
                            'definitions': [],
                            'examples': [],
                            'collocations': [],
                        }

                # 处理释义行（主要是中文）
                elif any(pw is not None for pw in pending_words):
                    # 检查是否有中文
                    has_chinese = re.search(r'[一-鿿]', line)

                    if has_chinese:
                        # 尝试按空格分割两个单词的释义
                        # 使用正则匹配多个连续空格或制表符作为分隔符
                        meanings = re.split(r'\s{4,}|\t+', line)

                        # 如果只有一个分割结果，尝试其他方式
                        if len(meanings) <= 1:
                            # 尝试按两个以上连续空格分割
                            meanings = re.split(r' {2,}', line)

                        # 分配给待处理的单词
                        for i, meaning in enumerate(meanings):
                            if i < 2 and pending_words[i] and meaning.strip():
                                # 清理释义
                                clean_meaning = meaning.strip()
                                # 移除前面的章节名称等干扰
                                clean_meaning = re.sub(r'^Chapter\s+\d+.*$', '', clean_meaning, flags=re.IGNORECASE)
                                if clean_meaning:
                                    pending_words[i]['definitions'].append({
                                        'part': '',
                                        'meaning': clean_meaning,
                                    })

                    # 处理例句（包含英文句子）
                    if re.search(r'[a-zA-Z]{10,}', line):
                        # 提取英文部分作为例句
                        english_parts = re.findall(r'[A-Z][^.!?]*[.!?]', line)

                        for i, example in enumerate(english_parts):
                            if i < 2 and pending_words[i] and len(example) > 10:
                                pending_words[i]['examples'].append(example)

                    # 处理搭配
                    if re.search(r'(搭配|collocation|phrase)', line, re.IGNORECASE):
                        collocations = re.findall(r'[a-z\s]+(?:搭配|collocation)', line, re.IGNORECASE)
                        for i, col in enumerate(collocations):
                            if i < 2 and pending_words[i]:
                                clean_col = col.strip()
                                if clean_col:
                                    pending_words[i]['collocations'].append(clean_col)

        # 保存最后待处理的单词
        for pw in pending_words:
            if pw:
                pw['id'] = str(word_id)
                pw['index'] = len(words)
                words.append(pw)
                word_id += 1

    # 更新章节的 endIndex 和 wordCount
    for chapter in chapters:
        chapter_words = [w for w in words if w['chapter'] == chapter['id']]
        if chapter_words:
            chapter['endIndex'] = chapter_words[-1]['index']
            chapter['wordCount'] = len(chapter_words)

    return words, chapters


def main():
    if not PDF_PATH.exists():
        print(f"错误: 找不到 PDF 文件: {PDF_PATH}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"开始提取词库: {PDF_PATH}")
    print(f"从第12页开始，提取前300页")

    words, chapters = extract_words_from_pdf(PDF_PATH, start_page=12, max_pages=300)

    # 保存为 JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({'words': words, 'chapters': chapters}, f, ensure_ascii=False, indent=2)

    print(f"\n提取完成！")
    print(f"总单词数: {len(words)}")
    print(f"总章节数: {len(chapters)}")
    print(f"输出文件: {OUTPUT_PATH}")

    # 显示前5个单词作为预览
    print("\n前5个单词预览:")
    for i, word in enumerate(words[:5], 1):
        print(f"\n{i}. {word.get('word')} {word.get('phonetic', '')}")
        if word.get('definitions'):
            print(f"   释义: {word['definitions'][0].get('meaning', '')}")


if __name__ == '__main__':
    main()