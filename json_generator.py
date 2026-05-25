"""
JSON数据生成模块
将单词统计结果导出为高效的JSON格式，前端快速加载搜索
"""

import json
from pathlib import Path
from typing import Dict
from word_processor import WordProcessor


class JsonGenerator:
    """JSON数据生成类"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_json(self, processor: WordProcessor, filename: str = "data.json") -> str:
        """
        从WordProcessor生成JSON文件
        
        Args:
            processor: WordProcessor实例（已处理完成）
            filename: 输出JSON文件名
            
        Returns:
            输出文件的完整路径
        """
        # 获取JSON格式的数据
        json_data = processor.get_json_data()
        
        # 写入JSON文件
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # 打印统计信息
        file_size_kb = output_path.stat().st_size / 1024
        print(f"✅ JSON数据文件生成成功")
        print(f"   输出路径: {output_path}")
        print(f"   文件大小: {file_size_kb:.1f} KB")
        print(f"   单词数: {json_data['uniqueWords']}")
        print(f"   总频数: {json_data['totalWords']}")
        print(f"   年份范围: {json_data['yearRange'][0]}-{json_data['yearRange'][1]}")
        
        return str(output_path)


if __name__ == "__main__":
    # 测试
    from extract_pdf import batch_process_pdfs
    
    pdf_dir = r"D:\Users\luocj\ky\公共课\英语真题\英语二"
    pdf_results = batch_process_pdfs(pdf_dir)
    
    processor = WordProcessor()
    processor.process_words(pdf_results)
    
    generator = JsonGenerator(".")
    generator.generate_json(processor)
