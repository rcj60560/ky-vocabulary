# 快速开始指南 - ky-vocabulary 项目

## ✅ 已完成

### 1️⃣ 项目迁移
- ✓ 复制所有源代码到 `D:\Users\luocj\pyProject\ky\ky-vocabulary`
- ✓ 保留 8122 个单词的频率数据（data.json）
- ✓ 保留当前 ECDICT 词典（dictionary.json，247 MB）

### 2️⃣ 词典集成方案（方案一 - StarDict）
- ✓ `stardict_converter.py` - StarDict 格式解析工具
- ✓ `dict_manager.py` - 词典管理和转换工具
- ✓ `DICTIONARY_GUIDE.md` - 详细集成指南

### 3️⃣ Git 管理
- ✓ 初始化 git 仓库
- ✓ 配置 .gitignore（排除大文件和构建产物）
- ✓ 两次提交：
  1. 初始化项目：复制原项目代码
  2. 添加 StarDict 词典集成方案

---

## 📋 下一步操作

### 快速验证项目
```bash
cd D:\Users\luocj\pyProject\ky\ky-vocabulary

# 1. 查看项目结构
git log --oneline

# 2. 查看当前词典统计
python dict_manager.py stats

# 3. 测试应用
python app.py
# 浏览器访问: http://localhost:5000
```

### 集成高质量词典（推荐）

**第一步：下载 StarDict 词典**
1. 访问 https://downloads.freemdict.com/ 或 https://www.mdict.cn/
2. 下载 **朗文当代英英词典 (LDOCE)** 或 **OALD**
3. 解压获得 `.ifo + .idx + .dict` 文件

**第二步：转换词典**
```bash
# 假设下载的词典名为 "ldoce"
python dict_manager.py convert ldoce

# 检查转换结果
python dict_manager.py stats
```

**第三步：修改应用使用新词典**
编辑 `app.py` 第 31-33 行：
```python
# 改为
DICTIONARY_FILE = OUTPUT_DIR / "dictionaries" / "ldoce.json"
```

**第四步：重新打包 EXE**
```bash
python build_exe.py
```

### 上传到远端

**创建新的 Git 远程仓库**
```bash
# 1. 在 GitHub/GitLab/Gitee 上创建新仓库 "ky-vocabulary"

# 2. 添加远程
git remote add origin https://github.com/your-username/ky-vocabulary.git

# 3. 推送（注意：不要推送 dictionary.json，太大！）
git push -u origin master
```

**或者使用 .gitignore 排除大文件**
```bash
# 编辑 .gitignore，确保有：
# dictionary.json
# dictionaries/*.json

# 然后提交和推送
git add .gitignore
git commit -m "chore: 更新 .gitignore，排除大词典文件"
git push
```

---

## 📊 项目状态

| 项 | 状态 | 详情 |
|----|------|------|
| 源代码 | ✓ | 所有 .py、.html、.json 已复制 |
| 数据文件 | ✓ | data.json (1.9 MB) |
| 词典文件 | ✓ | ECDICT (247 MB) |
| 词典方案 | ✓ | StarDict 集成工具已创建 |
| Git 管理 | ✓ | 已初始化，2 次提交 |
| 远端同步 | ⏳ | 等待你推送 |

---

## 🎯 后续开发计划

- [ ] 测试 StarDict 词典集成（LDOCE/OALD）
- [ ] 比较词典质量和加载性能
- [ ] 选择最优词典方案
- [ ] 更新打包 EXE（使用新词典）
- [ ] 推送到远端仓库
- [ ] 添加发音播放功能（可选）
- [ ] 云端收藏同步（可选）

---

## 📁 项目文件结构

```
ky-vocabulary/
├── .git/                   # Git 仓库
├── .gitignore             # Git 配置
├── README.md              # 项目说明
├── requirements.txt       # Python 依赖
├── DICTIONARY_GUIDE.md    # 词典集成指南
├── QUICKSTART.md          # 本文件
│
├── 核心代码
├── app.py                 # Flask 后端
├── build_exe.py           # PyInstaller 打包
├── generate_dictionary.py # 词典生成（ECDICT）
├── extract_pdf.py         # PDF 提取工具
├── templates/
│   ├── report_v2.html    # 主 UI（改进版）
│   └── report.html       # 旧 UI
│
├── 数据文件
├── data.json             # 8122 个单词频率
├── dictionary.json       # ECDICT 词典 (247 MB)
│
├── 词典工具
├── stardict_converter.py # StarDict 解析工具
├── dict_manager.py       # 词典管理工具
└── dictionaries/         # 词典存放目录
    └── （待添加 LDOCE/OALD）
```

---

## 💡 常见问题

**Q: 词典文件太大，怎么推送到 Git?**
A: 用 .gitignore 排除 dictionary.json，或用 Git LFS

**Q: 如何测试新词典效果？**
A: 修改 app.py 的 DICTIONARY_FILE 路径，重启 Flask

**Q: LDOCE 和 OALD 哪个更好？**
A: OALD 更详细权威，LDOCE 更简洁实用，建议都试试

**Q: 能合并多个词典吗？**
A: 可以！用 `dict_manager.py merge` 命令

---

**准备好了吗？现在可以：**
1. ✅ 下载高质量 StarDict 词典
2. ✅ 集成并测试
3. ✅ 推送到远端！
