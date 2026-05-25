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
DATA_FILES = [
    (str(PROJECT_DIR / "data.json"), "."),
    (str(PROJECT_DIR / "report.html"), "."),
]

def build_exe():
    """使用 PyInstaller 打包"""
    print("=" * 60)
    print("开始打�?exe 文件")
    print("=" * 60)
    
    # 检�?app.py
    if not APP_FILE.exists():
        print(f"�?文件不存�? {APP_FILE}")
        return False
    
    # 检查数据文�?
    if not (PROJECT_DIR / "data.json").exists():
        print(f"�?数据文件不存�? {PROJECT_DIR / 'data.json'}")
        print("请先运行 main.py 生成数据文件")
        return False
    
    if not (PROJECT_DIR / "report.html").exists():
        print(f"�?HTML 文件不存�? {PROJECT_DIR / 'report.html'}")
        return False
    
    print(f"\n�?文件检查完�?)
    print(f"   项目目录: {PROJECT_DIR}")
    print(f"   应用文件: {APP_FILE.name}")
    print(f"   数据文件: data.json")
    print(f"   页面文件: report.html")
    
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
        "--onefile",  # 生成单个 exe 文件
        "--windowed",  # 隐藏控制台窗�?
        "--name=考研英语单词频率统计",  # exe 名称
        "
        "--add-data", f"{PROJECT_DIR / 'data.json'};.",  # 包含 data.json
        "--add-data", f"{PROJECT_DIR / 'report.html'};.",  # 包含 report.html
        "--collect-all=flask",  # 收集 Flask 所有文�?
        "--hidden-import=flask",
        "--hidden-import=werkzeug",
        "--hidden-import=jinja2",
        "--hidden-import=click",
        "--hidden-import=itsdangerous",
        "--hidden-import=markupsafe",
        str(APP_FILE)
    ]
    
    # 执行命令
    import subprocess
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    
    if result.returncode != 0:
        print(f"\n�?打包失败")
        return False
    
    # 生成�?exe 文件
    exe_file = OUTPUT_DIR / "考研英语单词频率统计.exe"
    
    if exe_file.exists():
        exe_size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n�?打包成功")
        print(f"   输出目录: {OUTPUT_DIR}")
        print(f"   exe 文件: {exe_file.name}")
        print(f"   文件大小: {exe_size_mb:.1f} MB")
        
        print(f"\n" + "=" * 60)
        print("�?打包完成�?)
        print("=" * 60)
        print(f"\n📦 exe 文件位置:")
        print(f"   {exe_file}")
        print(f"\n💡 使用方法:")
        print(f"   1. 双击 exe 文件运行")
        print(f"   2. 应用自动启动服务器并打开浏览�?)
        print(f"   3. 在浏览器中使用单词查询工�?)
        print(f"   4. �?Ctrl+C 在命令行中关闭应�?)
        print("=" * 60)
        
        return True
    else:
        print(f"\n�?exe 文件生成失败")
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
