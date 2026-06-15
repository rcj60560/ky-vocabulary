import pdfplumber
from pathlib import Path

PDF_PATH = Path.home() / "Desktop" / "雅思词汇真经PDF高清彩色版.pdf"
OUTPUT_PATH = Path(__file__).parent / "pdf_structure.txt"

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write("正在分析PDF结构...\n\n")

    with pdfplumber.open(PDF_PATH) as pdf:
        f.write(f"总页数: {len(pdf.pages)}\n\n")

        # 显示前15页的内容（每页前25行）
        for i, page in enumerate(pdf.pages[:15], 1):
            text = page.extract_text()
            if text:
                lines = text.split('\n')[:25]
                f.write(f"{'='*60}\n")
                f.write(f"第 {i} 页:\n")
                f.write(f"{'='*60}\n")
                for line in lines:
                    f.write(f"{line}\n")
                f.write("\n")

print(f"分析完成，结果已保存到: {OUTPUT_PATH}")