# IELTS Learner

基于《雅思词汇真经》PDF 的单词学习应用，利用空闲时间高效背单词。

![Word Count](https://img.shields.io/badge/words-3389-blue)
![Chapters](https://img.shields.io/badge/chapters-22-green)

## ✨ 功能特性

- 📄 **单词卡片** - 显示单词、音标、释义、搭配、例句
- ⌨️ **键盘导航** - 左右键快速切换单词
- 📚 **章节选择** - 22 个章节，支持快速跳转
- 🎯 **熟悉度标记** - 未学/不认识/熟悉/认识 四级标记
- 🔥 **热力图统计** - 类似 GitHub 贡献图的学习进度展示
- 💾 **进度保存** - 本地持久化，关闭浏览器不丢失
- 🔄 **章节联动** - 切换单词自动更新所属章节

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.14+（用于提取词库）

### 安装运行

```bash
# 克隆项目
git clone <repository-url>
cd ielts-learner

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173/
```

## 📊 词库统计

| 章节 | 单词数 |
|------|--------|
| 自然地理 | 224 |
| 植物研究 | 135 |
| 动物保护 | 152 |
| 太空探索 | 66 |
| 学校教育 | 387 |
| 科技发明 | 114 |
| 文化历史 | 137 |
| 娱乐运动 | 157 |
| 物品材料 | 134 |
| 时尚潮流 | 101 |
| 饮食健康 | 164 |
| 建筑场所 | 115 |
| 交通旅行 | 120 |
| 国家政府 | 141 |
| 社会经济 | 150 |
| 法律法规 | 110 |
| 沙场争锋 | 201 |
| 社会角色 | 113 |
| 行为动作 | 239 |
| 身心健康 | 399 |
| 时间日期 | 30 |

**总计**: 3389 个单词

## 🛠 技术栈

- React 18 + TypeScript
- Vite
- TailwindCSS
- pdfplumber (Python)

## 📁 项目结构

```
ielts-learner/
├── src/
│   ├── components/    # React 组件
│   ├── hooks/         # 数据管理
│   └── App.tsx        # 主应用
├── docs/              # 项目文档
├── public/data/       # 词库数据
└── extract_pdf_improved.py  # PDF 提取脚本
```

## 📝 更新词库

```bash
python extract_pdf_improved.py
```

## 📖 详细文档

查看 [docs/PROJECT.md](docs/PROJECT.md) 了解完整的项目文档和开发指南。

## 📄 许可证

MIT