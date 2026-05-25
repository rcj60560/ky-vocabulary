# 词典集成指南

## 目前可用方案

### 方案 1: ECDICT（当前使用）✅
- **词条数**: 770,000+
- **质量**: ⭐⭐（参差不齐，部分定义准确性差）
- **大小**: 247 MB
- **优点**: 词条最多、开源
- **缺点**: 质量不均，缺少例句、发音

### 方案 2: StarDict 高质量词典（推荐） ⭐⭐⭐⭐⭐

#### 推荐词典

**朗文当代英英词典 (LDOCE)**
- 质量: ⭐⭐⭐⭐⭐
- 词条: ~80,000
- 特点: 简洁、实用、权威

**OALD 牛津高阶词典**
- 质量: ⭐⭐⭐⭐⭐
- 词条: ~90,000
- 特点: 详细、权威、覆盖广

**剑桥英英词典**
- 质量: ⭐⭐⭐⭐
- 词条: ~100,000
- 特点: 现代、贴近实际

#### 如何获取 StarDict 词典

**方法 1: 从 FreeDict 下载**
1. 访问 https://freedict.org/
2. 搜索 "English" 或具体词典名
3. 下载 `.tar.gz` 或 `.zip` 文件
4. 解压获得 `.ifo + .idx + .dict` 文件

**方法 2: 从 MDict 社区下载**
1. 访问 https://www.mdict.cn/
2. 搜索英英词典
3. 下载 StarDict 格式

**方法 3: 自己转换**
- 从 Kindle、MDict 等格式转换
- 使用在线转换工具

#### 集成步骤

**第一步：放置词典文件**
```bash
# 将 .ifo, .idx, .dict 文件放到这个目录
D:\Users\luocj\pyProject\ky\ky-vocabulary\dictionaries\

# 例如：
# - dictionaries/ldoce.ifo
# - dictionaries/ldoce.idx
# - dictionaries/ldoce.dict
```

**第二步：转换为 JSON**
```bash
cd D:\Users\luocj\pyProject\ky\ky-vocabulary

# 转换为 JSON
python dict_manager.py convert ldoce

# 检查结果
python dict_manager.py stats
```

**第三步：在应用中使用**
编辑 `app.py`，修改字典加载路径：
```python
# 从 ECDICT 切换到新词典
DICTIONARY_FILE = "dictionaries/ldoce.json"  # 改为这个
```

**第四步：重新打包 EXE**
```bash
python build_exe.py
```

### 方案 3: 合并多个词典

将高质量词典作为主要来源，用 ECDICT 作为备选补充：

```bash
# 合并 StarDict 词典和 ECDICT
python dict_manager.py merge dictionaries/ldoce.json dictionary.json
```

## 词典文件格式

### JSON 词典格式
```json
{
  "word": {
    "word": "word",
    "phonetic": "/wɜːd/",
    "definition": "英文定义",
    "translation": "中文释义",
    "pos": "n.",
    "collins": 5,
    "oxford": "1",
    "tags": ["cet4", "ky"],
    "examples": ["例句1", "例句2"],
    "forms": ["words", "worded"],
    "synonym": "词",
    "antonym": "反义词",
    "root": "词根",
    "affix": "词缀"
  }
}
```

## 性能对比

| 词典 | 词条数 | 文件大小 | 质量 | 加载时间 |
|------|--------|---------|------|---------|
| ECDICT | 770K | 247 MB | ⭐⭐ | ~3s |
| LDOCE | 80K | ~50 MB | ⭐⭐⭐⭐⭐ | ~1s |
| OALD | 90K | ~60 MB | ⭐⭐⭐⭐⭐ | ~1s |
| 合并 | 850K+ | ~300 MB | ⭐⭐⭐⭐ | ~4s |

## 建议方案

- **快速上手**: 使用当前的 ECDICT
- **质量优先**: 集成 LDOCE 或 OALD
- **平衡方案**: 合并 StarDict + ECDICT（LDOCE 优先，补充罕见词）

## 故障排除

### 转换失败
- 确保 .ifo, .idx, .dict 都存在
- 检查文件编码（应为 UTF-8）
- 查看错误日志

### 加载缓慢
- 减少词条数（只保留考研高频词）
- 压缩 JSON 文件（移除缩进）
- 分模块加载

### 定义不准确
- 使用不同的 StarDict 词典试试
- 报告给词典维护者
- 手工修正常用词

---

**下一步**: 下载 LDOCE 或 OALD，按上面步骤集成，测试效果！
