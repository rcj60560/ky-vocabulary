import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "src" / "data" / "words.json"

# 章节起始页码（根据目录）
CHAPTER_START_PAGES = {
    1: 12,    # 自然地理
    2: 0,     # 植物研究 - 待确定
    3: 0,     # 动物保护
    4: 0,     # 太空探索
    5: 0,     # 学校教育
    6: 0,     # 科技发明
    7: 0,     # 文化历史
    8: 0,     # 语言演化
    9: 0,     # 娱乐运动
    10: 0,    # 物品材料
    11: 0,    # 时尚潮流
    12: 0,    # 饮食健康
    13: 0,    # 建筑场所
    14: 0,    # 交通旅行
    15: 0,    # 国家政府
    16: 0,    # 社会经济
    17: 0,    # 法律法规
    18: 0,    # 沙场争锋
    19: 0,    # 社会角色
    20: 0,    # 行为动作
    21: 0,    # 身心健康
    22: 0,    # 时间日期
}

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
    pattern = r'(\w+(?:-\w+)*)\s*/([^/]+)/'

    matches = re.finditer(pattern, line)

    for match in matches:
        word, phonetic = match.groups()

        # 获取音标后面的部分作为可能的词性或释义
        after_phonetic = line[match.end():].strip()
        part = None
        meaning = None

        # 检查是否有词性 (n., vt., vi., adj., adv.等)
        part_match = re.match(r'^([nva]+\.)\s*(.+)?', after_phonetic)
        if part_match:
            part = part_match.group(1)
            meaning = part_match.group(2).strip() if part_match.group(2) else None
        elif after_phonetic and len(after_phonetic) < 100:
            meaning = after_phonetic

        words.append({
            'word': word,
            'phonetic': f'/{phonetic}/',
            'partOfSpeech': part,
            'definitions': [{'part': part or '', 'meaning': meaning or ''}] if meaning else [],
        })

    return words


def extract_words_from_pdf(pdf_path: Path, start_page: int = 12, max_pages: int = 300) -> tuple[List[Dict], List[Dict]]:
    """从 PDF 提取单词"""
    words = []
    chapters = []

    current_chapter = 1
    word_id = 1
    pending_words = []  # 等待解析释义的单词
    pending_examples = []  # 待处理的例句

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
                chapter_match = re.match(r'^Chapter\s+(\d+).*?\s+(.+)$', line, re.IGNORECASE)
                if chapter_match:
                    chapter_num = int(chapter_match.group(1))
                    chapter_name = chapter_match.group(2).strip()

                    # 保存上一个单词（如果有）
                    if pending_words:
                        for pw in pending_words:
                            if pw:
                                words.append(pw)
                                word_id += 1
                        pending_words = []

                    current_chapter = chapter_num

                    # 添加章节信息
                    if chapter_num not in [c['id'] for c in chapters]:
                        chapters.append({
                            'id': chapter_num,
                            'name': f'Chapter {chapter_num}: {chapter_name}',
                            'startIndex': len(words),
                            'endIndex': len(words) - 1,
                            'wordCount': 0,
                        })

                    print(f"发现章节 {chapter_num}: {chapter_name}")
                    continue

                # 检测单词行（包含音标）
                if '/' in line and re.search(r'\w+\s*/[^/]+/', line):
                    # 保存之前待处理的单词
                    if pending_words:
                        for pw in pending_words:
                            if pw:
                                words.append(pw)
                                word_id += 1
                        pending_words = []

                    # 解析新单词
                    parsed_words = parse_word_line(line)

                    for pw in parsed_words:
                        pending_words.append({
                            'id': str(word_id + len(pending_words)),
                            'word': pw['word'],
                            'phonetic': pw['phonetic'],
                            'partOfSpeech': pw['partOfSpeech'],
                            'chapter': current_chapter,
                            'index': len(words) + len(pending_words),
                            'definitions': pw['definitions'],
                            'examples': [],
                            'collocations': [],
                        })

                # 处理释义行（中文字符多）
                elif pending_words and re.search(r'[一-鿿]', line) and not re.search(r'\w{10,}', line):
                    # 这可能是释义行
                    # 根据待处理单词数量分配释义
                    meanings = re.split(r'\s{2,}', line)  # 按多个空格分割

                    for i, meaning in enumerate(meanings):
                        if i < len(pending_words) and meaning.strip():
                            if not pending_words[i]['definitions']:
                                pending_words[i]['definitions'] = []
                            pending_words[i]['definitions'].append({
                                'part': '',
                                'meaning': meaning.strip(),
                            })

                # 处理例句（包含英文句子）
                elif pending_words and re.search(r'[a-zA-Z]{20,}', line):
                    # 这可能是例句
                    # 简单分配给第一个待处理单词
                    if pending_words and line.strip():
                        example = line.strip()
                        # 移除中文翻译（如果有）
                        example = re.sub(r'[一-鿿].*$', '', example).strip()
                        if example:
                            pending_words[0]['examples'].append(example)

        # 保存最后待处理的单词
        for pw in pending_words:
            if pw:
                words.append(pw)

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
        print(f"\n{i}. {word.get('word')} ({word.get('phonetic', '')})")
        if word.get('chapter'):
            print(f"   章节: Chapter {word['chapter']}")


if __name__ == '__main__':
    main()