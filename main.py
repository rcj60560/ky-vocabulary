"""
考研英语二真题单词频率统计系统 - 主程序
完整的流程：PDF提取 -> 词处理 -> JSON生成 -> HTML生成
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_pdf import batch_process_pdfs
from word_processor import WordProcessor
from json_generator import JsonGenerator
from html_generator_new import HtmlGenerator


def main():
    """主程序"""
    
    # 配置
    PDF_DIR = r"D:\Users\luocj\ky\公共课\英语真题\英语二"
    OUTPUT_DIR = r"D:\Users\luocj\pyProject\tools\kaoyan_english_analyzer"
    
    print("=" * 60)
    print("考研英语二真题单词频率统计系统 (JSON版本)")
    print("=" * 60)
    
    # 第1步：批量提取PDF
    print("\n[步骤 1] 正在提取PDF文件中的文本...")
    print("-" * 60)
    
    if not os.path.exists(PDF_DIR):
        print(f"❌ PDF目录不存在: {PDF_DIR}")
        return
    
    pdf_results = batch_process_pdfs(PDF_DIR)
    
    if not pdf_results:
        print("❌ 未能提取任何PDF文件")
        return
    
    print(f"✅ 成功提取 {len(pdf_results)} 个PDF文件")
    total_raw_words = sum(r['word_count'] for r in pdf_results)
    print(f"   原始单词总数: {total_raw_words:,}")
    
    # 第2步：词处理与统计
    print("\n[步骤 2] 正在处理单词（统计、去重）...")
    print("-" * 60)
    
    processor = WordProcessor()
    stats = processor.process_words(pdf_results)
    
    print(f"✅ 单词处理完成")
    print(f"   不同单词数: {stats['unique_words']:,}")
    print(f"   处理后单词数: {stats['total_words']:,}")
    print(f"   过滤掉的单词: {total_raw_words - stats['total_words']:,}")
    
    print(f"\n📊 Top 10 高频词汇:")
    for word, count in processor.get_total_ranking(10):
        word_family = processor.get_word_family(word)
        print(f"   #{word:12s} → 出现 {count:4d} 次 (词形: {', '.join(word_family)})")
    
    # 第3步：生成JSON数据文件
    print("\n[步骤 3] 正在生成JSON数据文件...")
    print("-" * 60)
    
    json_generator = JsonGenerator(OUTPUT_DIR)
    json_path = json_generator.generate_json(processor)
    
    # 第4步：生成HTML报告（从模板复制）
    print("\n[步骤 4] 正在生成HTML报告...")
    print("-" * 60)
    
    html_generator = HtmlGenerator(OUTPUT_DIR)
    html_path = html_generator.generate_html()
    
    # 完成信息
    print("\n" + "=" * 60)
    print("✅ 所有步骤已完成！")
    print("=" * 60)
    print(f"\n📁 生成的文件:")
    print(f"   1️⃣  数据文件: {Path(json_path).name}")
    print(f"   2️⃣  HTML文件: {Path(html_path).name}")
    print(f"\n🌐 请在浏览器中打开:")
    print(f"   {html_path}")
    print(f"\n💡 优化特点:")
    print(f"   • JSON格式数据，异步加载，避免大文件卡顿")
    print(f"   • 搜索时快速在内存中过滤，极速响应")
    print(f"   • 支持按年份查看单词出现情况")
    print(f"   • 展示每个单词的所有词形变化")
    print("=" * 60)


if __name__ == "__main__":
    main()
