import pdfplumber
import json
import re
from pathlib import Path

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "src" / "data" / "words.json"

# 章节名称
CHAPTER_NAMES = {
    1: "自然地理", 2: "植物研究", 3: "动物保护", 4: "太空探索",
    5: "学校教育", 6: "科技发明", 7: "文化历史", 8: "语言演化",
    9: "娱乐运动", 10: "物品材料", 11: "时尚潮流", 12: "饮食健康",
    13: "建筑场所", 14: "交通旅行", 15: "国家政府", 16: "社会经济",
    17: "法律法规", 18: "沙场争锋", 19: "社会角色", 20: "行为动作",
    21: "身心健康", 22: "时间日期",
}


def parse_word_phonetics(line: str):
    """
    精确解析单词和音标
    格式：word1 /phonetic1/  word2 /phonetic2/
    使用精确的正则表达式
    """
    result = []

    # 匹配 pattern: 单词(英文) /音标/
    # 单词只包含字母、连字符、撇号
    pattern = r'([a-zA-Z][a-zA-Z\'\-]+)\s*/([^/]+)/'

    for match in re.finditer(pattern, line):
        word = match.group(1)
        phonetic = '/' + match.group(2) + '/'

        # 跳过太短的词（可能是错误匹配）
        if len(word) < 3:
            continue

        # 跳过明显不是单词的（如重复字符）
        if re.match(r'^([a-z])\1+$', word, re.IGNORECASE):
            continue

        result.append({
            'word': word,
            'phonetic': phonetic,
        })

    return result


def extract_words_from_pdf(pdf_path: Path, start_page: int = 12, max_pages: int = 300):
    """从 PDF 提取单词"""
    words = []
    chapters = []

    current_chapter = 1
    word_id = 1

    # 待处理的单词（当前行）
    current_words = []

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
                    # 保存之前的单词
                    for cw in current_words:
                        if cw:
                            cw['id'] = str(word_id)
                            cw['index'] = len(words)
                            words.append(cw)
                            word_id += 1
                    current_words = []

                    chapter_num = int(chapter_match.group(1))
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
                if len(line) < 8 or '雅思词汇' in line or 'IELTS' in line or re.match(r'^[一-鿯]+$', line):
                    continue

                # 检测是否是单词行（包含音标）
                # 使用更精确的检测：是否有 pattern word /phonetic/
                if re.search(r'[a-zA-Z][a-zA-Z\'\-]+\s*/[^/]+/', line):
                    # 保存之前的单词
                    for cw in current_words:
                        if cw:
                            cw['id'] = str(word_id)
                            cw['index'] = len(words)
                            words.append(cw)
                            word_id += 1
                    current_words = []

                    # 解析当前行的单词
                    parsed = parse_word_phonetics(line)

                    for item in parsed:
                        current_words.append({
                            'word': item['word'],
                            'phonetic': item['phonetic'],
                            'partOfSpeech': None,
                            'chapter': current_chapter,
                            'definitions': [],
                            'examples': [],
                            'collocations': [],
                        })

                # 处理释义行（中文为主）
                elif current_words:
                    has_chinese = re.search(r'[一-鿯]', line)

                    if has_chinese:
                        # 尝试分割两个单词的释义
                        # 按多个空格分割
                        parts = re.split(r'\s{3,}', line)

                        # 如果分割失败，尝试按单个空格但只保留中文部分
                        if len(parts) <= 1:
                            parts = [line]

                        # 分配给待处理的单词
                        for i, part in enumerate(parts):
                            if i < len(current_words) and part.strip():
                                clean_part = part.strip()
                                # 清理释义：移除英文，只保留中文和标点
                                clean_part = re.sub(r'[a-zA-Z]', '', clean_part)
                                clean_part = re.sub(r'[^一-鿿;；，、。：！？""''（）《》【】\s]', '', clean_part)
                                clean_part = clean_part.strip()
                                if clean_part and len(clean_part) > 0:
                                    current_words[i]['definitions'].append({
                                        'part': '',
                                        'meaning': clean_part,
                                    })

                    # 处理例句（英文句子）
                    # 匹配以大写字母开头的英文句子
                    examples = re.findall(r'[A-Z][a-z]+(?: [a-z]+)+[^.!?]*[.!?]', line)
                    for example in examples:
                        if len(example) > 10 and current_words:
                            current_words[0]['examples'].append(example)

                    # 处理搭配
                    # 查找英文短语
                    collocations = re.findall(r'[a-z]+ [a-z]+(?: [a-z]+)*', line, re.IGNORECASE)
                    for col in collocations:
                        if len(col) > 5 and len(col.split()) >= 2 and current_words:
                            # 只添加合理的搭配（不是例句的一部分）
                            if len(col) < 30 and '.' not in col and ',' not in col:
                                current_words[0]['collocations'].append(col.strip())

        # 保存最后待处理的单词
        for cw in current_words:
            if cw:
                cw['id'] = str(word_id)
                cw['index'] = len(words)
                words.append(cw)
                word_id += 1

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

    # Preview first 10 words
    print("\nFirst 10 words:")
    for i, word in enumerate(words[:10], 1):
        print(f"\n{i}. {word.get('word')} {word.get('phonetic', '')}")
        if word.get('definitions'):
            print(f"   Meaning: {word['definitions'][0].get('meaning', '')[:60]}...")
        if word.get('examples'):
            print(f"   Example: {word['examples'][0][:60]}...")


if __name__ == '__main__':
    main()