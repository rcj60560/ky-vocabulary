"""
HTML报告生成模块（新版本）
从templates目录复制HTML模板到输出目录
JSON数据由单独的json_generator.py负责生成
"""

import shutil
from pathlib import Path


class HtmlGenerator:
    """HTML生成类 - 复制模板并设置输出目录"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(__file__).parent / "templates"
    
    def generate_html(self, filename: str = "report.html") -> str:
        """
        复制HTML模板到输出目录
        
        Args:
            filename: 输出HTML文件名
            
        Returns:
            输出文件的完整路径
        """
        template_file = self.template_dir / "report.html"
        output_path = self.output_dir / filename
        
        if not template_file.exists():
            raise FileNotFoundError(f"HTML模板文件不存在: {template_file}")
        
        # 复制文件
        shutil.copy2(template_file, output_path)
        
        file_size_kb = output_path.stat().st_size / 1024
        print(f"✅ HTML报告生成成功")
        print(f"   输出路径: {output_path}")
        print(f"   文件大小: {file_size_kb:.1f} KB")
        
        return str(output_path)


if __name__ == "__main__":
    # 测试
    generator = HtmlGenerator(".")
    generator.generate_html()
