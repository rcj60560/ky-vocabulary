"""
HTML报告生成模块
使用Jinja2生成交互式HTML报告
"""

import json
import os
from jinja2 import Template
from typing import Dict, List


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考研英语二真题单词频率统计</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .stats-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .stat-card {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            font-size: 14px;
            color: #6c757d;
        }
        
        .controls {
            padding: 20px;
            background: #f8f9fa;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
            border-bottom: 1px solid #e9ecef;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .control-group label {
            font-weight: 500;
            color: #333;
            font-size: 14px;
        }
        
        input[type="number"],
        input[type="text"],
        select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        input[type="number"] {
            width: 100px;
        }
        
        input[type="text"] {
            width: 200px;
        }
        
        button {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        .content {
            padding: 30px 20px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .tab-button {
            padding: 10px 20px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            transition: all 0.3s;
        }
        
        .tab-button.active {
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: 500;
        }
        
        .tab-button:hover {
            background: none;
            color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #ddd;
            cursor: pointer;
            user-select: none;
        }
        
        th:hover {
            background: #e9ecef;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .rank-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            min-width: 30px;
            text-align: center;
        }
        
        .frequency-bar {
            display: inline-block;
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .forms-badge {
            display: inline-block;
            background: #e9ecef;
            color: #333;
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #6c757d;
        }
        
        .empty-state svg {
            width: 64px;
            height: 64px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 5px;
            margin-top: 30px;
        }
        
        .pagination button {
            padding: 6px 12px;
            min-width: 40px;
        }
        
        .pagination button.active {
            background: #333;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            border-top: 1px solid #e9ecef;
        }
        
        .year-tabs {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .year-tab-button {
            padding: 10px;
            text-align: center;
            background: white;
            border: 2px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .year-tab-button:hover {
            border-color: #667eea;
        }
        
        .year-tab-button.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        @media (max-width: 768px) {
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .control-group {
                flex-direction: column;
            }
            
            input[type="text"] {
                width: 100%;
            }
            
            table {
                font-size: 12px;
            }
            
            th, td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 考研英语二真题单词频率统计</h1>
            <p>基于2010-2023年考研英语二真题的单词频率分析报告</p>
        </div>
        
        <div class="stats-summary">
            <div class="stat-card">
                <div class="value">{{ unique_words }}</div>
                <div class="label">不同单词数</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ total_words }}</div>
                <div class="label">总单词数</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ pdf_count }}</div>
                <div class="label">真题年份</div>
            </div>
            <div class="stat-card">
                <div class="value">2010-2023</div>
                <div class="label">时间范围</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>🔍 搜索单词:</label>
                <input type="text" id="searchInput" placeholder="输入单词或词干...">
            </div>
            <div class="control-group">
                <label>📊 最小频率:</label>
                <input type="number" id="minFrequency" value="0" min="0" max="100">
            </div>
            <button onclick="applyFilters()">应用筛选</button>
            <button onclick="resetFilters()">重置</button>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('overall')">📈 总体统计</button>
                <button class="tab-button" onclick="switchTab('yearly')">📅 按年份统计</button>
            </div>
            
            <!-- 总体统计标签页 -->
            <div id="overall" class="tab-content active">
                <div style="color: #666; margin-bottom: 10px;">
                    显示 <span id="overallRowCount">0</span> 个单词 / 总共 {{ unique_words }} 个
                </div>
                <table id="overallTable">
                    <thead>
                        <tr>
                            <th style="width: 60px;">排名</th>
                            <th style="cursor: pointer;" onclick="sortTable('overall', 'word')">单词 ▲▼</th>
                            <th style="cursor: pointer;" onclick="sortTable('overall', 'freq')">频率 ▲▼</th>
                            <th>相关词形</th>
                        </tr>
                    </thead>
                    <tbody id="overallTableBody">
                    </tbody>
                </table>
            </div>
            
            <!-- 按年份统计标签页 -->
            <div id="yearly" class="tab-content">
                <div class="year-tabs" id="yearTabs">
                </div>
                <div style="color: #666; margin-bottom: 10px;">
                    显示 <span id="yearlyRowCount">0</span> 个单词
                </div>
                <table id="yearlyTable">
                    <thead>
                        <tr>
                            <th style="width: 60px;">排名</th>
                            <th>单词</th>
                            <th>年份频率</th>
                            <th>总频率</th>
                            <th>相关词形</th>
                        </tr>
                    </thead>
                    <tbody id="yearlyTableBody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>📝 数据说明：已过滤基础停用词，仅保留对学习有价值的词汇</p>
            <p>本报告自动生成，如有问题请联系开发者</p>
        </div>
    </div>
    
    <script>
        // 初始数据
        const totalStats = {{ total_stats_json }};
        const yearlyStats = {{ yearly_stats_json }};
        const stemToWords = {{ stem_to_words_json }};
        const allYears = {{ all_years_json }};
        
        let currentTab = 'overall';
        let currentYear = null;
        let sortField = 'freq';
        let sortDesc = true;
        
        // 初始化
        function init() {
            initializeYearTabs();
            renderOverallTable();
        }
        
        // 初始化年份标签页
        function initializeYearTabs() {
            const yearTabsContainer = document.getElementById('yearTabs');
            allYears.forEach(year => {
                const button = document.createElement('button');
                button.className = 'year-tab-button' + (year === allYears[0] ? ' active' : '');
                button.textContent = year + '年';
                button.onclick = () => selectYear(year);
                yearTabsContainer.appendChild(button);
            });
            currentYear = allYears[0];
        }
        
        // 切换标签页
        function switchTab(tab) {
            currentTab = tab;
            
            // 更新按钮状态
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // 显示/隐藏内容
            document.getElementById('overall').classList.remove('active');
            document.getElementById('yearly').classList.remove('active');
            document.getElementById(tab).classList.add('active');
            
            if (tab === 'yearly') {
                renderYearlyTable();
            }
        }
        
        // 选择年份
        function selectYear(year) {
            currentYear = year;
            
            // 更新按钮状态
            document.querySelectorAll('.year-tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            renderYearlyTable();
        }
        
        // 渲染总体表格
        function renderOverallTable() {
            const tbody = document.getElementById('overallTableBody');
            tbody.innerHTML = '';
            
            let data = Object.entries(totalStats).map(([word, freq]) => {
                // 找到该单词所属的词根及相关词形
                let relatedWords = [word];
                for (const [stem, words] of Object.entries(stemToWords)) {
                    if (words.includes(word)) {
                        relatedWords = words;
                        break;
                    }
                }
                return {
                    word,
                    freq,
                    relatedWords
                };
            });
            
            // 应用过滤
            data = applySearchAndMinFreq(data);
            
            // 排序
            if (sortField === 'freq') {
                data.sort((a, b) => sortDesc ? b.freq - a.freq : a.freq - b.freq);
            } else {
                data.sort((a, b) => sortDesc ? b.word.localeCompare(a.word) : a.word.localeCompare(b.word));
            }
            
            document.getElementById('overallRowCount').textContent = data.length;
            
            data.forEach((item, index) => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><span class="rank-badge">${index + 1}</span></td>
                    <td style="font-weight: 600; color: #667eea;">${item.word}</td>
                    <td><span class="frequency-bar">总计: ${item.freq}</span></td>
                    <td><span class="forms-badge">${item.relatedWords.join(', ')}</span></td>
                `;
            });
        }
        
        // 渲染按年份表格
        function renderYearlyTable() {
            const tbody = document.getElementById('yearlyTableBody');
            tbody.innerHTML = '';
            
            if (!(currentYear in yearlyStats)) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">暂无数据</td></tr>';
                return;
            }
            
            let data = Object.entries(yearlyStats[currentYear]).map(([word, yearFreq]) => {
                // 找到该单词所属的词根及相关词形
                let relatedWords = [word];
                for (const [stem, words] of Object.entries(stemToWords)) {
                    if (words.includes(word)) {
                        relatedWords = words;
                        break;
                    }
                }
                const totalFreq = totalStats[word] || 0;
                return {
                    word,
                    yearFreq,
                    totalFreq,
                    relatedWords
                };
            });
            
            // 应用过滤
            data = applySearchAndMinFreq(data);
            
            // 排序
            if (sortField === 'freq') {
                data.sort((a, b) => sortDesc ? b.yearFreq - a.yearFreq : a.yearFreq - b.yearFreq);
            } else {
                data.sort((a, b) => sortDesc ? b.word.localeCompare(a.word) : a.word.localeCompare(b.word));
            }
            
            document.getElementById('yearlyRowCount').textContent = data.length;
            
            data.forEach((item, index) => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><span class="rank-badge">${index + 1}</span></td>
                    <td style="font-weight: 600; color: #667eea;">${item.word}</td>
                    <td><span class="frequency-bar">${currentYear}年: ${item.yearFreq}</span></td>
                    <td><span class="frequency-bar">总计: ${item.totalFreq}</span></td>
                    <td><span class="forms-badge">${item.relatedWords.join(', ')}</span></td>
                `;
            });
        }
        
        // 应用搜索和最小频率过滤
        function applySearchAndMinFreq(data) {
            const searchText = document.getElementById('searchInput').value.toLowerCase();
            const minFreq = parseInt(document.getElementById('minFrequency').value) || 0;
            
            return data.filter(item => {
                // 获取要对比的频率（总体表是freq，年份表是yearFreq）
                const freq = item.freq || item.yearFreq;
                
                // 搜索匹配：单词或相关词形
                const matchSearch = !searchText || 
                    item.word.includes(searchText) ||
                    item.relatedWords.some(w => w.includes(searchText));
                
                const matchFreq = freq >= minFreq;
                return matchSearch && matchFreq;
            });
        }
        
        // 应用筛选
        function applyFilters() {
            if (currentTab === 'overall') {
                renderOverallTable();
            } else {
                renderYearlyTable();
            }
        }
        
        // 重置筛选
        function resetFilters() {
            document.getElementById('searchInput').value = '';
            document.getElementById('minFrequency').value = '0';
            applyFilters();
        }
        
        // 排序表格
        function sortTable(table, field) {
            if (sortField === field) {
                sortDesc = !sortDesc;
            } else {
                sortField = field;
                sortDesc = true;
            }
            
            if (table === 'overall') {
                renderOverallTable();
            } else {
                renderYearlyTable();
            }
        }
        
        // 页面加载完成后初始化
        window.addEventListener('load', init);
    </script>
</body>
</html>
"""


class HTMLGenerator:
    """HTML报告生成器"""
    
    def __init__(self, word_processor, pdf_results):
        self.word_processor = word_processor
        self.pdf_results = pdf_results
        
    def generate_report(self, output_path: str) -> str:
        """
        生成HTML报告
        """
        # 准备数据
        total_stats = dict(self.word_processor.total_stats)
        yearly_stats = {
            year: dict(self.word_processor.yearly_stats[year])
            for year in self.word_processor.yearly_stats
        }
        stem_to_words = {
            stem: list(words)
            for stem, words in self.word_processor.stem_to_words.items()
        }
        all_years = sorted([result['year'] for result in self.pdf_results])
        
        # 渲染模板
        template = Template(HTML_TEMPLATE)
        html_content = template.render(
            unique_words=len(total_stats),
            total_words=sum(total_stats.values()),
            pdf_count=len(set(result['year'] for result in self.pdf_results)),
            total_stats_json=json.dumps(total_stats),
            yearly_stats_json=json.dumps(yearly_stats),
            stem_to_words_json=json.dumps(stem_to_words),
            all_years_json=json.dumps(all_years)
        )
        
        # 保存文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path


if __name__ == "__main__":
    # 测试用
    from extract_pdf import batch_process_pdfs
    from word_processor import WordProcessor
    
    pdf_dir = r"D:\Users\luocj\ky\公共课\英语真题\英语二"
    pdf_results = batch_process_pdfs(pdf_dir)
    
    processor = WordProcessor()
    processor.process_words(pdf_results)
    
    generator = HTMLGenerator(processor, pdf_results)
    output_path = r"D:\Users\luocj\pyProject\tools\kaoyan_english_analyzer\report.html"
    generator.generate_report(output_path)
    
    print(f"Report generated: {output_path}")
