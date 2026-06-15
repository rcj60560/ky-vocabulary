import pdfplumber
from pathlib import Path

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "pdf_detail.txt"

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:

    with pdfplumber.open(PDF_PATH) as pdf:
        # 显示第12-18页的详细内容
        for i in range(11, 18):
            page = pdf.pages[i]
            text = page.extract_text()
            if text:
                f.write(f"{'='*80}\n")
                f.write(f"第 {i+1} 页:\n")
                f.write(f"{'='*80}\n")
                lines = text.split('\n')
                for j, line in enumerate(lines):
                    f.write(f"{j:2d}: {line}\n")
                f.write("\n")

print(f"分析完成，结果已保存到: {OUTPUT_PATH}")