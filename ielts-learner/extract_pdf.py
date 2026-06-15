import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

# PDF 路径
PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "src" / "data" / "words.json"

# 创建输出目录
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def parse_word_from_text(text: str) -> Optional[Dict]:
    """解析单行文本中的单词信息"""
    # 匹配单词模式: word [phonetic] (part)
    word_pattern = r'^(\w+(?:-\w+)*)\s*\[?([^\]\)]*)\]?\s*(?:\(([a-z.]+)\))?\s*(.*)$'
    match = re.match(word_pattern, text.strip())

    if match:
        word, phonetic, part, rest = match.groups()
        return {
            'word': word,
            'phonetic': phonetic if phonetic else None,
            'part': part if part else None,
            'meaning': rest.strip() if rest else None,
        }
    return None


def extract_words_from_pdf(pdf_path: Path) -> List[Dict]:
    """从 PDF 提取单词"""
    words = []
    current_chapter = None
    current_word = None
    current_definitions = []
    current_examples = []
    current_collocations = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"总页数: {total_pages}")

        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检测章节标题
                chapter_match = re.match(r'^[第\s]*(\d+|[一二三四五六七八九十]+)[章节篇]\s*(.+)$', line)
                if chapter_match:
                    # 保存上一个单词
                    if current_word:
                        words.append(current_word)
                        current_word = None
                    current_chapter = line
                    print(f"发现章节: {current_chapter}")
                    continue

                # 检测单词行
                word_info = parse_word_from_text(line)
                if word_info:
                    # 保存上一个单词
                    if current_word:
                        if current_examples:
                            current_word['examples'] = current_examples
                        if current_collocations:
                            current_word['collocations'] = current_collocations
                        if current_definitions:
                            current_word['definitions'] = current_definitions
                        words.append(current_word)

                    # 开始新单词
                    current_word = {
                        'id': f"{len(words) + 1}",
                        'word': word_info['word'],
                        'phonetic': word_info['phonetic'],
                        'partOfSpeech': word_info['part'],
                        'chapter': current_chapter or 'Unknown',
                        'definitions': [],
                        'examples': [],
                        'collocations': [],
                    }
                    if word_info['meaning']:
                        current_word['definitions'].append({
                            'part': word_info['part'] or '',
                            'meaning': word_info['meaning'],
                        })

                    current_definitions = []
                    current_examples = []
                    current_collocations = []

                # 检测例句（通常包含引号或Example等关键词）
                elif current_word:
                    if re.search(r'(?:例句|Example|example)', line) or '"' in line or "'" in line:
                        # 清理例句
                        example = re.sub(r'^(?:例句|Example|example)[:\s]*', '', line).strip()
                        example = re.sub(r'^["\']|["\']$', '', example)
                        if example:
                            current_examples.append(example)

                    # 检测搭配（通常包含关键词）
                    elif re.search(r'(?:搭配|collocation|phrase)', line, re.I):
                        collocation = re.sub(r'^(?:搭配|collocation|phrase)[:\s]*', '', line, flags=re.I).strip()
                        if collocation:
                            current_collocations.append(collocation)

                    # 检测释义行
                    elif line and (line[0].isdigit() or re.match(r'^[a-z.]+', line)):
                        # 可能是额外的释义
                        current_definitions.append({
                            'part': '',
                            'meaning': line,
                        })

        # 保存最后一个单词
        if current_word:
            if current_examples:
                current_word['examples'] = current_examples
            if current_collocations:
                current_word['collocations'] = current_collocations
            if current_definitions:
                current_word['definitions'] = current_definitions
            words.append(current_word)

    return words


def main():
    if not PDF_PATH.exists():
        print(f"错误: 找不到 PDF 文件: {PDF_PATH}")
        return

    print(f"开始提取词库: {PDF_PATH}")
    words = extract_words_from_pdf(PDF_PATH)

    # 保存为 JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"\n提取完成！")
    print(f"总单词数: {len(words)}")
    print(f"输出文件: {OUTPUT_PATH}")

    # 显示前5个单词作为预览
    print("\n前5个单词预览:")
    for i, word in enumerate(words[:5], 1):
        print(f"\n{i}. {word.get('word')}")
        if word.get('phonetic'):
            print(f"   音标: {word['phonetic']}")
        if word.get('definitions'):
            print(f"   释义: {word['definitions'][0].get('meaning', '')}")


if __name__ == '__main__':
    main()