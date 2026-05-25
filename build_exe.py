"""
PyInstaller 打包脚本
生成可执行的 exe 文件
"""

import os
import sys
import shutil
from pathlib import Path

# 配置
PROJECT_DIR = Path(__file__).parent
APP_FILE = PROJECT_DIR / "app.py"
OUTPUT_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"

def build_exe():
    """使用 PyInstaller 打包"""
    print("=" * 60)
    print("开始打包 exe 文件")
    print("=" * 60)
    
    # 检查 app.py
    if not APP_FILE.exists():
        print(f"❌ 文件不存在: {APP_FILE}")
        return False
    
    # 检查数据文件
    if not (PROJECT_DIR / "data.json").exists():
        print(f"❌ 数据文件不存在: {PROJECT_DIR / 'data.json'}")
        print("请先运行 main.py 生成数据文件")
        return False
    
    # 检查 templates 目录和 report_v2.html
    templates_dir = PROJECT_DIR / "templates"
    if not templates_dir.exists():
        print(f"❌ templates 目录不存在: {templates_dir}")
        return False
    
    if not (templates_dir / "report_v2.html").exists():
        print(f"❌ HTML 文件不存在: {templates_dir / 'report_v2.html'}")
        return False
    
    # 检查词典文件
    dict_file = PROJECT_DIR / "dictionary.json"
    if not dict_file.exists():
        print(f"❌ 词典文件不存在: {dict_file}")
        print("请先运行 generate_dictionary.py 生成词典文件")
        return False
    
    print(f"\n✅ 文件检查完成")
    print(f"   项目目录: {PROJECT_DIR}")
    print(f"   应用文件: {APP_FILE.name}")
    print(f"   数据文件: data.json")
    print(f"   模板目录: templates/report_v2.html")
    print(f"   词典文件: dictionary.json")
    
    # 构建 PyInstaller 命令
    print(f"\n[步骤 1] 正在打包...")
    print("-" * 60)
    
    # 清理旧的构建文件
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    
    # PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # 生成目录结构（支持大文件）
        "--windowed",  # 隐藏控制台窗口
        "--name=考研英语单词频率统计",  # exe 名称
        "--add-data", f"{PROJECT_DIR / 'data.json'};.",  # 包含 data.json
        "--add-data", f"{PROJECT_DIR / 'dictionary.json'};.",  # 包含 dictionary.json
        "--add-data", f"{PROJECT_DIR / 'templates'};templates",  # 包含 templates 目录
        "--collect-all=flask",  # 收集 Flask 所有文件
        "--hidden-import=flask",
        "--hidden-import=werkzeug",
        "--hidden-import=jinja2",
        "--hidden-import=click",
        "--hidden-import=itsdangerous",
        "--hidden-import=markupsafe",
        "--hidden-import=requests",
        str(APP_FILE)
    ]
    
    # 执行命令
    import subprocess
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    
    if result.returncode != 0:
        print(f"\n❌ 打包失败")
        return False
    
    # --onedir 模式下 exe 在子目录中
    exe_file = OUTPUT_DIR / "考研英语单词频率统计" / "考研英语单词频率统计.exe"
    
    if exe_file.exists():
        exe_size_mb = exe_file.stat().st_size / (1024 * 1024)
        dict_file = OUTPUT_DIR / "考研英语单词频率统计" / "_internal" / "dictionary.json"
        data_file = OUTPUT_DIR / "考研英语单词频率统计" / "_internal" / "data.json"
        
        print(f"\n✅ 打包成功！")
        print(f"   exe 文件: {exe_file}")
        print(f"   大小: {exe_size_mb:.1f} MB")
        print(f"   词典文件: {'✓ 存在' if dict_file.exists() else '✗ 缺失'}")
        print(f"   数据文件: {'✓ 存在' if data_file.exists() else '✗ 缺失'}")
        
        print(f"\n{'=' * 60}")
        print("✅ 打包完成！运行方式：")
        print(f"   双击 {exe_file}")
        print(f"{'=' * 60}")
        return True
    else:
        print(f"\n❌ exe 文件生成失败，期望路径: {exe_file}")
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
