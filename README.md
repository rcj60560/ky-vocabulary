# 考研英语二真题单词频率统计

基于 2010-2023 年考研英语二真题的单词频率统计与学习工具。

## 功能特性

- 📊 单词频率统计（8122 个高频词）
- 🔍 实时搜索与过滤
- 📅 按年份分类统计
- ⭐ 收藏单词功能
- 📚 离线英英词典（多方案支持）
- 🎯 考研高频词标记

## 项目结构

```
ky-vocabulary/
├── app.py                    # Flask 后端服务
├── build_exe.py             # PyInstaller 打包脚本
├── generate_dictionary.py   # 词典数据生成
├── extract_pdf.py           # PDF 提取工具
├── templates/
│   └── report_v2.html      # 前端 UI
├── data.json               # 单词频率数据
├── dictionary.json         # 离线词典（ECDICT）
└── requirements.txt        # Python 依赖
```

## 安装与使用

### 1. 环境配置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/Scripts/activate  # Windows
# 或
source .venv/bin/activate      # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行开发服务

```bash
python app.py
# 浏览器访问: http://localhost:5000
```

### 3. 打包 EXE

```bash
python build_exe.py
# 输出在 dist/ 目录
```

## 词典方案

目前支持：

- **ECDICT**: 77万+词条（质量参差不齐）
- **StarDict**: 支持高质量词典（待集成）

## 开发计划

- [ ] 集成高质量 StarDict 词典（朗文/OALD）
- [ ] 添加发音播放
- [ ] 云端同步收藏
- [ ] 移动端适配
- [ ] 词根词缀详解

## 技术栈

- **后端**: Flask 3.1.3, Python 3.12
- **前端**: HTML5 + Vanilla JS + CSS3
- **打包**: PyInstaller 6.20
- **词典**: ECDICT, StarDict

## 许可证

MIT

---

**开发者**: 
**最后更新**: 2026-05-25
