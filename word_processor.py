"""
单词处理模块
统计原始单词频率、构建词形映射、数据聚合
"""

import re
from collections import defaultdict, Counter
from typing import Dict, List
from nltk.stem import PorterStemmer


# 考研基础词汇黑名单（太基础，无统计价值）
STOPWORDS = {
    # 代词
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'whose',
    'this', 'that', 'these', 'those',
    # 动词
    'be', 'is', 'am', 'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can',
    'shall', 'get', 'got', 'getting', 'make', 'made', 'making', 'go', 'goes', 'going', 'went', 'gone',
    'come', 'came', 'coming', 'know', 'knew', 'knowing', 'take', 'took', 'taking', 'see', 'saw', 'seen', 'seeing',
    'think', 'thought', 'thinking', 'say', 'said', 'saying', 'tell', 'told', 'telling', 'give', 'gave', 'given', 'giving',
    'find', 'found', 'finding', 'use', 'used', 'using', 'work', 'worked', 'working', 'call', 'called', 'calling',
    'try', 'tried', 'trying', 'ask', 'asked', 'asking', 'need', 'needed', 'needing', 'feel', 'felt', 'feeling',
    'become', 'became', 'becoming', 'leave', 'left', 'leaving', 'put', 'puts', 'putting', 'mean', 'meant', 'meaning',
    'keep', 'kept', 'keeping', 'let', 'lets', 'letting', 'begin', 'began', 'beginning', 'seem', 'seemed', 'seeming',
    'help', 'helped', 'helping', 'talk', 'talked', 'talking', 'turn', 'turned', 'turning', 'start', 'started', 'starting',
    'show', 'showed', 'shown', 'showing', 'hear', 'heard', 'hearing', 'play', 'played', 'playing', 'run', 'ran', 'running',
    'move', 'moved', 'moving', 'like', 'liked', 'liking', 'live', 'lived', 'living', 'believe', 'believed', 'believing',
    'hold', 'held', 'holding', 'bring', 'brought', 'bringing', 'happen', 'happened', 'happening', 'write', 'wrote', 'writing',
    'provide', 'provided', 'providing', 'sit', 'sat', 'sitting', 'stand', 'stood', 'standing', 'lose', 'lost', 'losing',
    'pay', 'paid', 'paying', 'meet', 'met', 'meeting', 'include', 'included', 'including', 'continue', 'continued', 'continuing',
    'set', 'sets', 'setting', 'learn', 'learned', 'learning', 'change', 'changed', 'changing', 'lead', 'led', 'leading',
    'understand', 'understood', 'understanding', 'watch', 'watched', 'watching', 'follow', 'followed', 'following',
    'stop', 'stopped', 'stopping', 'create', 'created', 'creating', 'speak', 'spoke', 'speaking', 'read', 'reads', 'reading',
    'allow', 'allowed', 'allowing', 'add', 'added', 'adding', 'spend', 'spent', 'spending', 'grow', 'grew', 'growing',
    'open', 'opened', 'opening', 'walk', 'walked', 'walking', 'win', 'won', 'winning', 'offer', 'offered', 'offering',
    'remember', 'remembered', 'remembering', 'love', 'loved', 'loving', 'consider', 'considered', 'considering',
    'appear', 'appeared', 'appearing', 'buy', 'bought', 'buying', 'wait', 'waited', 'waiting', 'serve', 'served', 'serving',
    'die', 'died', 'dying', 'send', 'sent', 'sending', 'expect', 'expected', 'expecting', 'build', 'built', 'building',
    'stay', 'stayed', 'staying', 'fall', 'fell', 'falling', 'cut', 'cuts', 'cutting', 'reach', 'reached', 'reaching',
    'kill', 'killed', 'killing', 'remain', 'remained', 'remaining', 'suggest', 'suggested', 'suggesting', 'raise', 'raised', 'raising',
    'pass', 'passed', 'passing', 'sell', 'sold', 'selling', 'require', 'required', 'requiring', 'report', 'reported', 'reporting',
    'decide', 'decided', 'deciding', 'pull', 'pulled', 'pulling', 'explain', 'explained', 'explaining', 'develop', 'developed', 'developing',
    'carry', 'carried', 'carrying', 'break', 'broke', 'breaking', 'spend', 'spent', 'spending', 'eat', 'ate', 'eating',
    'catch', 'caught', 'catching', 'draw', 'drew', 'drawing', 'choose', 'chose', 'chosen', 'choosing',
    # 冠词
    'a', 'an', 'the',
    # 介词
    'of', 'in', 'to', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'is', 'was', 'are', 'into', 'or', 'and',
    'over', 'before', 'between', 'out', 'against', 'during', 'without', 'before', 'under', 'around', 'among', 'through',
    'up', 'off', 'above', 'down', 'through', 'about', 'across', 'along', 'after', 'below', 'beneath', 'beside', 'besides',
    'beyond', 'inside', 'outside', 'toward', 'towards', 'throughout', 'past', 'within',
    # 连词
    'and', 'but', 'or', 'if', 'because', 'when', 'where', 'why', 'how', 'although', 'while', 'than', 'so', 'thus', 'then',
    'therefore', 'however', 'moreover', 'furthermore', 'meanwhile', 'instead', 'rather', 'quite', 'also', 'just', 'only',
    'even', 'still', 'yet', 'else', 'otherwise', 'except', 'unless', 'until', 'since', 'before', 'after', 'once',
    # 其他常见基础词
    'there', 'here', 'now', 'then', 'today', 'yesterday', 'tomorrow', 'all', 'each', 'every', 'both', 'either', 'neither',
    'one', 'two', 'three', 'first', 'second', 'third', 'many', 'much', 'few', 'little', 'some', 'any', 'no', 'not',
    'yes', 'no', 'well', 'ok', 'etc', 'etc',
    # PDF垃圾数据和OCR错误
    'ou', 'ot', 'eht', 'hte', 'teh', 'htat', 'taht', 'whihc', 'liek', 'adn', 'teh', 'etc',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'  # 单字母
}


class WordProcessor:
    """单词处理类 - 统计原始单词（不做词根提取）"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        # {year: Counter({word: count, ...})}
        self.yearly_stats = defaultdict(Counter)
        # {word: count, ...}
        self.total_stats = Counter()
        # 词根映射：用于搜索时找到相关词形 {stem: [word1, word2, ...]}
        self.stem_to_words = defaultdict(set)
        
    def should_filter_word(self, word: str) -> bool:
        """
        检查单词是否应该被过滤
        """
        # 过滤停用词
        if word in STOPWORDS:
            return True
        
        # 过滤长度小于3的单词（更严格地过滤单字母和两字母的垃圾词）
        if len(word) < 3:
            return True
        
        # 过滤纯数字
        if word.isdigit():
            return True
        
        # 过滤看起来像垃圾数据的词（包含多个重复字符）
        if len(set(word)) <= 1:  # 如 'aaa', 'bbb'
            return True
        
        # 过滤不常见的字符组合（可能是OCR错误）
        # 例如只有辅音或特殊的字符模式
        vowels = set('aeiou')
        consonants = set('bcdfghjklmnpqrstvwxyz')
        
        has_vowel = any(c in vowels for c in word)
        has_consonant = any(c in consonants for c in word)
        
        # 完全没有元音或辅音的词很可能是垃圾
        if not has_vowel or not has_consonant:
            return True
        
        # 过滤看起来像格式化字符的模式
        if word in ['ou', 'ot', 'thi', 'tha', 'thi']:
            return True
        
        return False
    
    def process_words(self, pdf_results: List[Dict]) -> Dict:
        """
        处理从PDF中提取的单词，进行频率统计（不做词根提取）
        
        Args:
            pdf_results: 从extract_pdf.batch_process_pdfs返回的结果列表
            
        Returns:
            包含统计结果的字典
        """
        for result in pdf_results:
            year = result['year']
            words = result['words']
            
            # 处理该年份的所有单词
            for word in words:
                if self.should_filter_word(word):
                    continue
                
                # 保留原始单词，不做词根提取
                # 只在搜索时用词根来找相关词形
                stem = self.stemmer.stem(word)
                self.stem_to_words[stem].add(word)
                
                # 更新年份统计（原始单词）
                self.yearly_stats[year][word] += 1
                
                # 更新总体统计（原始单词）
                self.total_stats[word] += 1
        
        return {
            'yearly_stats': dict(self.yearly_stats),
            'total_stats': dict(self.total_stats),
            'stem_to_words': {k: sorted(list(v)) for k, v in self.stem_to_words.items()},
            'unique_words': len(self.total_stats),
            'total_words': sum(self.total_stats.values())
        }
    
    def get_yearly_ranking(self, year: int, limit: int = None) -> List[tuple]:
        """
        获取某一年的单词排序列表（按频率降序）
        """
        if year not in self.yearly_stats:
            return []
        
        rankings = self.yearly_stats[year].most_common(limit)
        return rankings
    
    def get_total_ranking(self, limit: int = None) -> List[tuple]:
        """
        获取总体单词排序列表（按频率降序）
        """
        rankings = self.total_stats.most_common(limit)
        return rankings
    
    def get_word_family(self, word: str) -> List[str]:
        """
        根据输入的单词，找到所有相关词形（同一词根的词）
        """
        stem = self.stemmer.stem(word.lower())
        return sorted(list(self.stem_to_words.get(stem, [word])))
    
    def get_word_details(self, word: str) -> Dict:
        """
        获取某个单词的详细信息
        """
        word_lower = word.lower()
        return {
            'word': word_lower,
            'total_frequency': self.total_stats.get(word_lower, 0),
            'word_family': self.get_word_family(word_lower),
            'yearly_frequency': {
                year: count for year, count in 
                [(y, self.yearly_stats[y][word_lower]) for y in self.yearly_stats if word_lower in self.yearly_stats[y]]
            }
        }
    
    def get_json_data(self) -> Dict:
        """
        返回适合JSON序列化的完整数据结构
        用于前端快速搜索和展示
        
        返回结构:
        {
            "words": [
                {"word": "more", "total": 461, "years": [2010, 2011, ...], "yearly": {2010: 5, 2011: 3, ...}},
                ...
            ],
            "totalWords": 49103,
            "uniqueWords": 8122,
            "yearRange": [2010, 2023],
            "stemToWords": {"mor": ["more"], "time": ["time", "times"], ...}
        }
        """
        # 获取所有年份范围
        years = sorted(self.yearly_stats.keys())
        year_range = [years[0], years[-1]] if years else [0, 0]
        
        # 构建单词列表（按总频率排序）
        words_list = []
        for word, total_count in self.total_stats.most_common():
            # 获取该单词出现的所有年份
            word_years = sorted([year for year in self.yearly_stats if word in self.yearly_stats[year]])
            
            # 构建年份频率字典
            yearly_dict = {year: self.yearly_stats[year][word] for year in word_years}
            
            words_list.append({
                'word': word,
                'total': total_count,
                'years': word_years,  # 这个单词出现在哪些年份
                'yearly': yearly_dict  # 该单词每年的频率
            })
        
        # 构建词根到单词的映射（用于搜索相关词形）
        stem_to_words_dict = {}
        for stem, words_set in self.stem_to_words.items():
            stem_to_words_dict[stem] = sorted(list(words_set))
        
        return {
            'words': words_list,
            'totalWords': sum(self.total_stats.values()),
            'uniqueWords': len(self.total_stats),
            'yearRange': year_range,
            'stemToWords': stem_to_words_dict
        }
