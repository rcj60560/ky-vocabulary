"""
考研英语二真题单词频率统计 - Flask Web 应用
可打包成 exe，双击运行自动打开浏览器
"""

import os
import sys
import json
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, send_file, jsonify, make_response

# 配置 - 支持 PyInstaller exe 和直接运行两种方式
if getattr(sys, 'frozen', False):
    # 在 PyInstaller exe 中运行 (--onedir 模式)
    # 在 --onedir 模式下，sys._MEIPASS 指向 _internal 目录
    if hasattr(sys, '_MEIPASS'):
        BASE_DIR = Path(sys._MEIPASS)
    else:
        BASE_DIR = Path(sys.executable).parent
else:
    # 直接运行 python 脚本
    BASE_DIR = Path(__file__).parent

CURRENT_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR
JSON_FILE = OUTPUT_DIR / "data.json"
HTML_FILE = OUTPUT_DIR / "templates" / "report_v2.html"
DICT_FILE = OUTPUT_DIR / "dictionary.json"
PORT = 5000

# 日志文件（用于 --windowed 模式下诊断）
LOG_FILE = Path(sys.executable).parent / "app_debug.log"  # 写到 exe 同一目录

def log_msg(msg):
    """写入日志文件"""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception as e:
        print(f"[日志写入失败] {e}")

# 记录初始化信息
log_msg("=" * 60)
log_msg(f"运行模式: {'PyInstaller exe (--onedir)' if getattr(sys, 'frozen', False) else 'Python 脚本'}")
log_msg(f"sys.frozen: {getattr(sys, 'frozen', False)}")
log_msg(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
log_msg(f"sys.executable: {sys.executable}")
log_msg(f"BASE_DIR: {BASE_DIR}")
log_msg(f"JSON_FILE: {JSON_FILE} (存在: {JSON_FILE.exists()})")
log_msg(f"DICT_FILE: {DICT_FILE} (存在: {DICT_FILE.exists()})")
log_msg(f"HTML_FILE: {HTML_FILE} (存在: {HTML_FILE.exists()})")
log_msg(f"LOG_FILE: {LOG_FILE}")

print(f"[配置] 运行模式: {'PyInstaller exe' if getattr(sys, 'frozen', False) else 'Python 脚本'}")
print(f"[配置] BASE_DIR: {BASE_DIR}")
print(f"[配置] 数据文件: {JSON_FILE} (存在: {JSON_FILE.exists()})")
print(f"[配置] 词典文件: {DICT_FILE} (存在: {DICT_FILE.exists()})")
print(f"[配置] 日志文件: {LOG_FILE}")

# Flask 应用
app = Flask(__name__, static_folder=str(OUTPUT_DIR), static_url_path='')

# 全局数据缓存
app_data = None
definition_cache = {}  # 缓存定义以减少 API 调用


@app.route('/')
def index():
    """主页 - 返回 report_v2.html"""
    log_msg(f"[GET /] HTML_FILE: {HTML_FILE}, 存在: {HTML_FILE.exists()}")
    if HTML_FILE.exists():
        response = make_response(send_file(str(HTML_FILE)))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    log_msg("[ERROR] report_v2.html not found")
    return "report.html not found", 404


@app.route('/api/data')
def get_data():
    """API 端点 - 返回 data.json"""
    log_msg(f"[GET /api/data] JSON_FILE: {JSON_FILE}, 存在: {JSON_FILE.exists()}")
    if JSON_FILE.exists():
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            log_msg(f"[GET /api/data] 成功返回数据，包含 {len(data.get('words', []))} 个词条")
            return jsonify(data)
    log_msg("[ERROR] data.json not found")
    return jsonify({'error': '数据文件未找到'}), 404


@app.route('/api/definition/<word>')
def get_definition(word):
    """获取单词定义（从离线词典）"""
    word_lower = word.lower()
    
    # 检查缓存
    if word_lower in definition_cache:
        return jsonify(definition_cache[word_lower])
    
    try:
        # 从离线词典加载（第一次初始化）
        if not hasattr(app, '_dictionary'):
            dict_file = OUTPUT_DIR / "dictionary.json"
            log_msg(f"[首次查询] 加载词典: {dict_file}")
            if dict_file.exists():
                log_msg(f"[首次查询] 开始加载词典（可能需要几秒钟）...")
                with open(dict_file, 'r', encoding='utf-8') as f:
                    app._dictionary = json.load(f)
                log_msg(f"[首次查询] 词典已加载，包含 {len(app._dictionary)} 个词条")
            else:
                log_msg(f"[错误] 词典文件不存在: {dict_file}")
                app._dictionary = {}
        
        # 查询离线词典
        if word_lower in app._dictionary:
            entry = app._dictionary[word_lower]
            
            # 解析例句（用 | 分隔）
            examples = []
            if entry.get('example'):
                example_list = entry['example'].split('|')
                examples = [ex.strip() for ex in example_list[:2] if ex.strip()]
            
            definition = {
                'word': entry.get('word', word_lower),
                'phonetic': entry.get('phonetic', ''),
                'partOfSpeech': entry.get('pos', ''),
                'meaning': entry.get('translation', ''),
                'definition': entry.get('definition', ''),
                'examples': examples,
                'wordRoot': entry.get('root', ''),
                'affixes': entry.get('affix', ''),
                'synonyms': entry.get('synonym', ''),
                'antonyms': entry.get('antonym', ''),
                'tags': entry.get('tags', []),
                'forms': entry.get('forms', []),
                'collins': entry.get('collins', 0),
                'oxford': entry.get('oxford', 0),
            }
            
            definition_cache[word_lower] = definition
            log_msg(f"[定义查询] 找到 '{word_lower}' -> {entry.get('translation', '')}")
            return jsonify(definition)
        else:
            # 词典中没有，返回"未找到"
            log_msg(f"[定义查询] 未找到 '{word_lower}'")
            definition = {
                'word': word_lower,
                'phonetic': '',
                'partOfSpeech': '',
                'meaning': '',
                'definition': '词典中未找到此单词',
                'examples': [],
                'wordRoot': '',
                'affixes': '',
                'synonyms': '',
                'antonyms': '',
                'tags': [],
                'forms': [],
                'collins': 0,
                'oxford': 0,
            }
            definition_cache[word_lower] = definition
            return jsonify(definition)
        
    except Exception as e:
        log_msg(f"[错误] 词典查询异常: {e}")
        print(f"[错误] 词典查询错误: {e}")
        return jsonify({
            'word': word_lower,
            'error': '查询失败',
            'definition': '暂无定义'
        }), 500


def run_server():
    """启动 Flask 服务器"""
    app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False, threaded=True)


def main():
    """主函数"""
    print("=" * 60)
    print("考研英语二真题单词频率统计 - 本地应用")
    print("=" * 60)
    
    log_msg("[主程序] 应用启动")
    
    # 检查必要文件
    if not JSON_FILE.exists():
        msg = f"数据文件未找到: {JSON_FILE}"
        print(f"\n❌ {msg}")
        log_msg(f"[错误] {msg}")
        print("请先运行 main.py 生成数据文件")
        input("\n按 Enter 键退出...")
        sys.exit(1)
    
    if not HTML_FILE.exists():
        msg = f"HTML 文件未找到: {HTML_FILE}"
        print(f"\n❌ {msg}")
        log_msg(f"[错误] {msg}")
        print("请确保 templates/report_v2.html 存在")
        input("\n按 Enter 键退出...")
        sys.exit(1)
    
    log_msg("[主程序] 文件检查完成")
    print("\n✅ 文件检查完成")
    print(f"   数据文件: {JSON_FILE.name}")
    print(f"   页面文件: templates/report_v2.html")
    
    # 启动服务器线程
    print("\n[启动中...] 正在启动本地服务器")
    log_msg("[主程序] 启动 Flask 服务器")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    log_msg("[主程序] 服务器已启动，打开浏览器")
    
    # 打开浏览器
    url = f'http://127.0.0.1:{PORT}'
    print(f"✅ 服务器已启动")
    print(f"🌐 正在打开浏览器: {url}\n")
    log_msg(f"[主程序] 打开浏览器: {url}")
    
    try:
        webbrowser.open(url)
        log_msg("[主程序] 浏览器已打开")
    except Exception as e:
        msg = f"无法自动打开浏览器: {e}"
        print(f"⚠️  {msg}")
        log_msg(f"[警告] {msg}")
        print(f"请手动打开: {url}\n")
    
    print("=" * 60)
    print("💡 应用已启动，按 Ctrl+C 关闭")
    print("=" * 60 + "\n")
    
    # 保持应用运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✅ 应用已关闭")
        log_msg("[主程序] 应用已关闭")
        sys.exit(0)


if __name__ == '__main__':
    main()
