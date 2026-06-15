# IELTS Learner 项目文档

> 基于《雅思词汇真经》PDF 的单词学习应用

## 📋 项目概述

**项目名称**: IELTS Learner
**开发时间**: 2026-06
**目标用户**: 雅思备考学习者
**总单词数**: 3389 个（22 个章节）

---

## 🎯 功能特性

### 核心功能

| 功能 | 状态 | 描述 |
|------|------|------|
| 单词卡片 | ✅ | 显示单词、音标、释义、搭配、例句 |
| 键盘导航 | ✅ | 左右键切换单词 |
| 章节选择 | ✅ | 22 个章节，支持跳转 |
| 熟悉度标记 | ✅ | 未学/不认识/熟悉/认识 四级 |
| 热力图统计 | ✅ | 100×100 格子显示学习进度 |
| 进度保存 | ✅ | localStorage 持久化 |
| 章节联动 | ✅ | 切换单词自动更新章节 |

### 待开发功能

- [ ] 发音播放（TTS）
- [ ] 词根词源显示
- [ ] 搜索功能
- [ ] 收藏单词
- [ ] 错词本
- [ ] 学习统计报告
- [ ] 暗黑模式

---

## 📊 词库统计

### 总体统计

- **总单词数**: 3389 个
- **总章节数**: 22 个
- **总页数**: 314 页
- **平均每页**: 10.8 个单词

### 章节分布

| 章节 | 名称 | 单词数 | 占比 |
|------|------|--------|------|
| Chapter 1 | 自然地理 | 224 | 6.6% |
| Chapter 2 | 植物研究 | 135 | 4.0% |
| Chapter 3 | 动物保护 | 152 | 4.5% |
| Chapter 4 | 太空探索 | 66 | 1.9% |
| Chapter 5 | 学校教育 | 387 | 11.4% |
| Chapter 6 | 科技发明 | 114 | 3.4% |
| Chapter 7 | 文化历史 | 137 | 4.0% |
| Chapter 9 | 娱乐运动 | 157 | 4.6% |
| Chapter 10 | 物品材料 | 134 | 4.0% |
| Chapter 11 | 时尚潮流 | 101 | 3.0% |
| Chapter 12 | 饮食健康 | 164 | 4.8% |
| Chapter 13 | 建筑场所 | 115 | 3.4% |
| Chapter 14 | 交通旅行 | 120 | 3.5% |
| Chapter 15 | 国家政府 | 141 | 4.2% |
| Chapter 16 | 社会经济 | 150 | 4.4% |
| Chapter 17 | 法律法规 | 110 | 3.2% |
| Chapter 18 | 沙场争锋 | 201 | 5.9% |
| Chapter 19 | 社会角色 | 113 | 3.3% |
| Chapter 20 | 行为动作 | 239 | 7.1% |
| Chapter 21 | 身心健康 | 399 | 11.8% |
| Chapter 22 | 时间日期 | 30 | 0.9% |

> **注意**: Chapter 8 (语言演化) 缺失，PDF 中未检测到该章节。

---

## 🛠 技术栈

### 前端

- **框架**: React 18 + TypeScript
- **构建工具**: Vite 8
- **样式**: TailwindCSS 3
- **状态管理**: React Hooks

### 后端

- **数据源**: PDF 解析 (Python pdfplumber)
- **数据格式**: JSON

### 工具

- **PDF 解析**: pdfplumber
- **包管理**: npm
- **代码规范**: TypeScript

---

## 📁 项目结构

```
ielts-learner/
├── src/
│   ├── components/        # React 组件
│   │   ├── WordCard.tsx   # 单词卡片
│   │   ├── Navigation.tsx # 底部导航
│   │   └── Heatmap.tsx    # 热力图统计
│   ├── hooks/
│   │   └── useWords.ts    # 词库数据管理
│   ├── data/              # 原始词库数据
│   ├── App.tsx            # 主应用（所有组件整合）
│   ├── main.tsx           # 入口文件
│   └── index.css          # 全局样式
├── public/
│   └── data/
│       └── words.json     # 使用的词库文件
├── docs/                  # 项目文档
│   └── PROJECT.md         # 本文档
├── extract_pdf_improved.py  # PDF 提取脚本
├── pdf_stats.md           # 提取统计报告
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.14+
- npm 或 yarn

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ielts-learner
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

4. **访问应用**
   ```
   http://localhost:5173/
   ```

---

## 📝 数据提取

### 运行提取脚本

```bash
python extract_pdf_improved.py
```

### 输出文件

- `src/data/words.json` - 原始词库
- `public/data/words.json` - 使用的词库
- `pdf_stats.md` - 统计报告

---

## 🐛 已知问题

### PDF 解析问题

1. **双列排版解析**
   - 问题：部分单词的释义可能包含其他单词的内容
   - 原因：pdfplumber 提取文本时，左右列内容可能混合
   - 影响：约 10% 的单词释义可能不准确
   - 状态：待优化

2. **章节检测**
   - 问题：Chapter 8 未被检测到
   - 原因：PDF 中该章节标题格式不同
   - 状态：需要手动检查

3. **页码过滤**
   - 问题：部分页码可能被误识别为单词
   - 状态：已优化过滤规则

### UI 问题

1. **章节联动**
   - 状态：已修复（切换单词自动更新章节）

---

## 🔧 配置说明

### TailwindCSS 配置

文件: `tailwind.config.js`

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#0ea5e9',
          600: '#0284c7',
        },
      },
    },
  },
};
```

### Vite 配置

文件: `vite.config.ts`

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
```

---

## 📦 构建部署

### 开发构建

```bash
npm run dev
```

### 生产构建

```bash
npm run build
npm run preview
```

### 静态部署

构建产物在 `dist/` 目录，可直接部署到：
- GitHub Pages
- Vercel
- Netlify
- 任何静态文件服务器

---

## 🔄 更新词库

当需要更新词库数据时：

1. 确保 PDF 文件在 `~/Desktop/雅思词汇真经PDF高清彩色版.pdf`
2. 运行提取脚本：
   ```bash
   python extract_pdf_improved.py
   ```
3. 刷新浏览器即可使用新词库

---

## 📚 参考资料

- [React 文档](https://react.dev/)
- [Vite 文档](https://vite.dev/)
- [TailwindCSS 文档](https://tailwindcss.com/)
- [pdfplumber 文档](https://github.com/jsvine/pdfplumber)

---

## 👥 贡献指南

### 开发流程

1. 创建新分支：`git checkout -b feature/xxx`
2. 进行开发
3. 提交代码：`git commit -m "xxx"`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

### 代码规范

- 使用 TypeScript
- 组件使用函数式组件 + Hooks
- 遵循 React 最佳实践

---

## 📄 许可证

MIT

---

## 📮 联系方式

- Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

**最后更新**: 2026-06-15