"""
PDF提取与数据清洗模块
从PDF文件中提取英文文本，清洗特殊字符，提取年份信息
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 尝试使用不同的PDF库
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'pypdf2'
    except ImportError:
        PDF_LIBRARY = None


def extract_year_from_filename(filename: str) -> Tuple[int, str]:
    """
    从文件名中提取年份
    例如: "2013年考研英语二真题.pdf" -> (2013, "2013年")
    """
    match = re.search(r'(\d{4})年', filename)
    if match:
        year = int(match.group(1))
        return year, f"{year}年"
    # 处理"10-22考研英语二真题无解析.pdf"这样的格式
    match = re.search(r'(\d{2})-(\d{2})', filename)
    if match:
        start_year = 2000 + int(match.group(1))
        end_year = 2000 + int(match.group(2))
        return start_year, f"{start_year}-{end_year}年"
    return None, None


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    从PDF文件中提取所有文本
    尝试使用不同的库以提高兼容性
    """
    text = ""
    
    # 尝试pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue
        if text:
            return text
    except Exception as e:
        pass
    
    # 回退到PyPDF2
    try:
        from PyPDF2 import PdfReader
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text:
            return text
    except Exception as e:
        pass
    
    # 最后尝试fitz (pymupdf)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        pass
    
    return text


def clean_text(text: str) -> str:
    """
    清洗文本，移除特殊字符、数字等
    保留英文单词和基本的标点符号
    """
    # 移除多余的空格和换行符
    text = re.sub(r'\s+', ' ', text)
    # 保留只有字母的单词
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return text.strip()


def extract_english_words(text: str) -> List[str]:
    """
    从清洗后的文本中提取所有英文单词
    """
    # 使用正则表达式提取单词
    words = re.findall(r'[a-zA-Z]+', text)
    # 转为小写
    words = [word.lower() for word in words]
    return words


def process_pdf_file(pdf_path: str) -> Dict:
    """
    处理单个PDF文件，返回包含年份和单词列表的字典
    """
    filename = os.path.basename(pdf_path)
    year, year_label = extract_year_from_filename(filename)
    
    if year is None:
        print(f"⚠️  跳过: 无法从文件名提取年份: {filename}")
        return None
    
    try:
        print(f"  📄 处理: {filename} (年份: {year})  ", end=" ")
        
        # 提取文本
        raw_text = extract_text_from_pdf(pdf_path)
        
        if not raw_text:
            print(f"⚠️  警告: 无法提取文本")
            return None
        
        # 清洗文本
        cleaned_text = clean_text(raw_text)
        
        # 提取单词
        words = extract_english_words(cleaned_text)
        
        print(f"✅ 提取 {len(words):,} 个词")
        
        return {
            'year': year,
            'year_label': year_label,
            'filename': filename,
            'words': words,
            'word_count': len(words)
        }
    except KeyboardInterrupt:
        print(f"\n❌ 被中断")
        raise
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {str(e)[:100]}")
        return None


def batch_process_pdfs(pdf_directory: str) -> List[Dict]:
    """
    批量处理PDF文件夹中的所有PDF文件
    """
    pdf_files = sorted([f for f in os.listdir(pdf_directory) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"❌ 在 {pdf_directory} 中未找到PDF文件")
        return []
    
    print(f"📁 发现 {len(pdf_files)} 个PDF文件\n")
    
    results = []
    for idx, pdf_file in enumerate(pdf_files, 1):
        print(f"[{idx}/{len(pdf_files)}]", end=" ")
        pdf_path = os.path.join(pdf_directory, pdf_file)
        try:
            result = process_pdf_file(pdf_path)
            if result:
                results.append(result)
        except KeyboardInterrupt:
            print("\n⏹️  用户中止了处理")
            break
        except Exception as e:
            print(f"❌ 处理失败: {type(e).__name__}")
            continue
    
    return results


if __name__ == "__main__":
    # 测试用
    pdf_dir = r"D:\Users\luocj\ky\公共课\英语真题\英语二"
    results = batch_process_pdfs(pdf_dir)
    
    print(f"\n\nProcessed {len(results)} files")
    for result in results:
        print(f"{result['year_label']}: {result['word_count']} words extracted")
