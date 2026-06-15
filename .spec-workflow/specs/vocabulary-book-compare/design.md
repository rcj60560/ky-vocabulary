# 词汇书对比功能 - 技术设计文档

**版本**: 1.0
**创建日期**: 2026-06-10

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      前端 (Browser)                       │
│  ┌──────────────┐      ┌──────────────┐                 │
│  │  upload.html │─────▶│  results.html │                 │
│  │  (上传界面)   │      │  (结果展示)   │                 │
│  └──────────────┘      └──────────────┘                 │
└─────────────────────────────────────────────────────────┘
                          │ HTTP API
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    后端 (Flask)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ /api/upload  │→ │ OCR Service  │→ │ Word Matcher  │  │
│  │  (文件上传)   │  │  (单词提取)   │  │  (词频对比)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  uploads/    │  │ Tesseract   │  │  data.json   │  │
│  (临时文件)   │  │  (OCR引擎)   │  │  (真题词频)   │  │
└──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构

```
D:\ky\ky-vocabulary\
├── app.py                          # 修改：新增API端点
├── templates\
│   ├── report_v2.html              # 修改：新增词汇书对比Tab
│   └── vocabulary_compare.html     # 新增：词汇书对比页面
├── uploads\                        # 新增：临时上传目录
├── requirements.txt                # 修改：新增依赖
└── services\
    └── word_matcher.py             # 新增：词频对比服务
```

---

## 🔌 API 设计

### POST `/api/vocabulary/compare`

**请求**：Multipart form-data
- `file`: PDF文件

**响应**（成功）：
```json
{
  "success": true,
  "message": "处理完成",
  "data": {
    "totalWords": 1250,
    "matchedWords": 1120,
    "unmatchedWords": 130,
    "results": [
      {
        "word": "abandon",
        "frequency": 127,
        "years": [2013, 2015, 2020],
        "rank": 45,
        "totalRank": 8122
      }
    ]
  }
}
```

**响应**（失败）：
```json
{
  "success": false,
  "error": "文件过大，最大支持50MB"
}
```

---

## 🧩 核心组件设计

### 1. WordMatcher 服务

```python
class WordMatcher:
    def __init__(self, data_json_path: str):
        self.data = self._load_data()
        self.word_map = self._build_word_map()

    def match(self, words: List[str]) -> List[MatchResult]:
        """对比单词列表，返回词频信息"""

    def _build_word_map(self) -> Dict[str, WordData]:
        """构建单词查找映射（O(1)查找）"""
```

### 2. PDF 提取器

```python
class PDFExtractor:
    def extract_words(self, pdf_path: str) -> List[str]:
        """提取PDF中的单词"""
        # 1. 尝试文本提取
        # 2. 失败则使用OCR
```

### 3. 前端组件

```javascript
// upload.js
function handleFileUpload(file) {
  // 验证文件类型和大小
  // 上传到服务器
  // 显示进度
}

// results.js
function displayResults(data) {
  // 渲染表格
  // 添加排序功能
}
```

---

## 🔄 数据流

```
1. 用户选择PDF文件
   ↓
2. 前端验证（类型、大小）
   ↓
3. 上传到 /api/vocabulary/compare
   ↓
4. 保存到 uploads/ 临时目录
   ↓
5. PDFExtractor 提取单词
   ↓
6. WordMatcher 与 data.json 对比
   ↓
7. 返回JSON结果
   ↓
8. 前端渲染表格
```

---

## ⚡ 性能优化

| 优化点 | 方案 |
|--------|------|
| 单词查找 | 预构建哈希映射，O(1)查找 |
| OCR处理 | 逐页处理，返回进度 |
| 结果缓存 | 相同文件名缓存结果 |
| 大文件 | 限制50MB，超时120秒 |

---

## 🛡️ 安全考虑

| 风险 | 防护措施 |
|------|----------|
| 文件上传攻击 | 限制文件类型、大小 |
| 路径遍历 | 使用安全文件名处理 |
| DoS | 设置请求超时 |
| 内存泄漏 | 及时清理临时文件 |

---

## 📊 测试策略

| 测试类型 | 覆盖内容 |
|----------|----------|
| 单元测试 | WordMatcher.match() |
| 集成测试 | API端点完整流程 |
| 端到端测试 | 上传→处理→展示 |
| 性能测试 | 100页PDF处理时间 |

---

## 📦 依赖新增

```txt
# requirements.txt 新增
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==10.0.0
```