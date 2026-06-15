import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "src" / "data" / "words.json"

# 章节名称映射
CHAPTER_NAMES = {
    1: "自然地理", 2: "植物研究", 3: "动物保护", 4: "太空探索",
    5: "学校教育", 6: "科技发明", 7: "文化历史", 8: "语言演化",
    9: "娱乐运动", 10: "物品材料", 11: "时尚潮流", 12: "饮食健康",
    13: "建筑场所", 14: "交通旅行", 15: "国家政府", 16: "社会经济",
    17: "法律法规", 18: "沙场争锋", 19: "社会角色", 20: "行为动作",
    21: "身心健康", 22: "时间日期",
}


def extract_words_from_pdf(pdf_path: Path, start_page: int = 12, max_pages: int = 300):
    """从 PDF 提取单词"""
    words = []
    chapters = []

    current_chapter = 1
    word_id = 1

    # 状态变量
    pending_words = []  # 待处理的单词列表
    current_line_words = []  # 当前行解析出的单词

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = min(len(pdf.pages), start_page + max_pages)

        for page_num in range(start_page, total_pages):
            page = pdf.pages[page_num]
            text = page.extract_text()

            if not text:
                continue

            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检测新章节标题
                chapter_match = re.search(r'Chapter\s+(\d+)', line, re.IGNORECASE)
                if chapter_match:
                    chapter_num = int(chapter_match.group(1))
                    # 保存之前的单词
                    words.extend(pending_words)
                    pending_words = []
                    current_chapter = chapter_num

                    # 添加章节信息
                    if chapter_num not in [c['id'] for c in chapters]:
                        full_name = CHAPTER_NAMES.get(chapter_num, f'Chapter {chapter_num}')
                        chapters.append({
                            'id': chapter_num,
                            'name': f'Chapter {chapter_num}: {full_name}',
                            'startIndex': len(words),
                            'wordCount': 0,
                        })
                    continue

                # 跳过明显不是单词行的内容
                if len(line) < 5 or line.startswith('雅思词汇'):
                    continue

                # 检测单词行（格式：word /phonetic/ word /phonetic/）
                # 使用更精确的正则
                word_pattern = r'([a-z]+(?:[-\']?[a-z]+)*)\s*/([^/]+/?)'

                matches = list(re.finditer(word_pattern, line, re.IGNORECASE))

                if matches and len(matches) >= 1:
                    # 这是单词行，先保存之前的单词
                    words.extend(pending_words)
                    pending_words = []

                    # 解析当前行的单词
                    for match in matches:
                        word = match.group(1)

                        # 跳过太短的"单词"
                        if len(word) < 2:
                            continue

                        # 获取音标
                        phonetic_start = match.start(2)
                        phonetic_end = match.end()

                        # 向前查找完整的音标
                        phonetic_part = match.group(2)

                        # 尝试构建完整的音标
                        # 检查音标部分是否以/开头
                        if phonetic_part.startswith('/'):
                            full_phonetic = phonetic_part
                        else:
                            # 向后查找完整的音标
                            remaining = line[phonetic_end:]
                            end_slash = remaining.find('/')
                            if end_slash != -1:
                                full_phonetic = '/' + phonetic_part + remaining[:end_slash+1]
                            else:
                                full_phonetic = '/' + phonetic_part + '/'

                        # 检查词性
                        after_match = line[match.end():]
                        part = None
                        part_match = re.match(r'^([a-z]+\.)(?:\s|$)', after_match, re.IGNORECASE)
                        if part_match:
                            part = part_match.group(1)

                        pending_words.append({
                            'id': str(word_id + len(pending_words)),
                            'word': word,
                            'phonetic': full_phonetic,
                            'partOfSpeech': part,
                            'chapter': current_chapter,
                            'index': len(words) + len(pending_words),
                            'definitions': [],
                            'examples': [],
                            'collocations': [],
                        })

                # 处理释义行（中文为主）
                elif pending_words:
                    has_chinese = re.search(r'[一-鿿]', line)

                    if has_chinese:
                        # 尝试分割两个单词的释义
                        # 使用多个连续空格或特殊字符作为分隔符
                        meanings = re.split(r'\s{4,}', line)

                        if len(meanings) <= 1:
                            # 尝试其他分割方式
                            meanings = re.split(r'\s{2,}(?=[一-鿯])', line)

                        # 分配给待处理的单词
                        for i, meaning in enumerate(meanings):
                            if i < len(pending_words) and meaning.strip():
                                clean_meaning = meaning.strip()
                                # 移除非中文字符开头的内容
                                clean_meaning = re.sub(r'^[^一-鿯]+', '', clean_meaning)
                                if clean_meaning and len(clean_meaning) > 1:
                                    pending_words[i]['definitions'].append({
                                        'part': '',
                                        'meaning': clean_meaning,
                                    })

                    # 处理例句（英文句子）
                    english_sentence_match = re.search(r'[A-Z][a-z]+[^.!?]*[.!?]', line)
                    if english_sentence_match:
                        example = english_sentence_match.group(0)
                        if len(example) > 15 and len(pending_words) > 0:
                            # 分配给第一个待处理的单词
                            pending_words[0]['examples'].append(example)

                    # 处理搭配
                    collocation_match = re.search(r'[a-z\s]+(?:搭配|collocation)', line, re.IGNORECASE)
                    if collocation_match and len(pending_words) > 0:
                        col = collocation_match.group(0).strip()
                        if col:
                            pending_words[0]['collocations'].append(col)

        # 保存最后待处理的单词
        words.extend(pending_words)

    # 更新章节信息
    for chapter in chapters:
        chapter_words = [w for w in words if w['chapter'] == chapter['id']]
        if chapter_words:
            chapter['endIndex'] = chapter_words[-1]['index']
            chapter['wordCount'] = len(chapter_words)

    return words, chapters


def main():
    if not PDF_PATH.exists():
        print(f"Error: PDF not found: {PDF_PATH}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Extracting from: {PDF_PATH}")
    print(f"Starting from page 12, max 300 pages")

    words, chapters = extract_words_from_pdf(PDF_PATH, start_page=12, max_pages=300)

    # Save to JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({'words': words, 'chapters': chapters}, f, ensure_ascii=False, indent=2)

    print(f"\nDone!")
    print(f"Total words: {len(words)}")
    print(f"Total chapters: {len(chapters)}")
    print(f"Output: {OUTPUT_PATH}")

    # Preview first 5 words
    print("\nFirst 5 words:")
    for i, word in enumerate(words[:5], 1):
        print(f"\n{i}. {word.get('word')} {word.get('phonetic', '')}")
        if word.get('definitions'):
            print(f"   Meaning: {word['definitions'][0].get('meaning', '')[:50]}...")


if __name__ == '__main__':
    main()