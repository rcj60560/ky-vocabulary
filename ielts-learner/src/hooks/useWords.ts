import { useState, useCallback, useEffect } from 'react';

// 类型定义
type FamiliarityLevel = 'unknown' | 'unfamiliar' | 'familiar' | 'known';

interface Word {
  id: string;
  word: string;
  phonetic?: string;
  partOfSpeech?: string;
  definitions?: Definition[];
  collocations?: string[];
  examples?: string[];
  chapter: number;
  index: number;
}

interface Definition {
  part: string;
  meaning: string;
}

interface Chapter {
  id: number;
  name: string;
  wordCount: number;
  startIndex: number;
  endIndex: number;
}

interface WordProgress {
  wordId: string;
  level: FamiliarityLevel;
  lastReviewed: string;
  reviewCount: number;
}

// 工具函数
const getTodayDate = (): string => {
  return new Date().toISOString().split('T')[0];
};

const storage = {
  getProgress: (): Map<string, WordProgress> => {
    const data = localStorage.getItem('ielts-learner-progress');
    return data ? new Map(JSON.parse(data)) : new Map();
  },
  saveProgress: (progress: Map<string, WordProgress>) => {
    localStorage.setItem('ielts-learner-progress', JSON.stringify([...progress]));
  },
  getLastSession: (): { chapter: number; index: number } | null => {
    const data = localStorage.getItem('ielts-learner-last-session');
    return data ? JSON.parse(data) : null;
  },
  saveLastSession: (chapter: number, index: number) => {
    localStorage.setItem('ielts-learner-last-session', JSON.stringify({ chapter, index }));
  },
};

const loadWordData = async (): Promise<{ words: Word[]; chapters: Chapter[] }> => {
  try {
    const response = await fetch('/data/words.json');
    const data = await response.json();

    const words: Word[] = data.words.map((w: any, idx: number) => ({
      id: w.id || String(idx + 1),
      word: w.word,
      phonetic: w.phonetic,
      partOfSpeech: w.partOfSpeech,
      chapter: w.chapter,
      index: w.index !== undefined ? w.index : idx,
      definitions: w.definitions || [],
      examples: w.examples || [],
      collocations: w.collocations || [],
    }));

    // 过滤掉无效的章节（如 Chapter 64）
    const validChapters = data.chapters.filter((c: any) => c.id >= 1 && c.id <= 22);

    const chapters: Chapter[] = validChapters.map((c: any) => ({
      id: c.id,
      name: c.name,
      wordCount: c.wordCount || 0,
      startIndex: c.startIndex || 0,
      endIndex: c.endIndex || 0,
    }));

    return { words, chapters };
  } catch (error) {
    console.error('Failed to load word data:', error);
    return { words: [], chapters: [] };
  }
};

export const useWords = () => {
  const [words, setWords] = useState<Word[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentChapter, setCurrentChapter] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [progress, setProgress] = useState<Map<string, WordProgress>>(new Map());

  // 加载数据
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const wordData = await loadWordData();
      setWords(wordData.words);
      setChapters(wordData.chapters);

      const savedProgress = storage.getProgress();
      setProgress(savedProgress);

      const lastSession = storage.getLastSession();
      if (lastSession && lastSession.index < wordData.words.length) {
        setCurrentIndex(lastSession.index);
        // 自动更新章节
        const word = wordData.words[lastSession.index];
        if (word) {
          setCurrentChapter(word.chapter);
        }
      } else if (wordData.chapters.length > 0) {
        setCurrentChapter(wordData.chapters[0].id);
      }

      setLoading(false);
    };

    loadData();
  }, []);

  // 保存进度
  useEffect(() => {
    if (progress.size > 0) {
      storage.saveProgress(progress);
    }
  }, [progress]);

  // 保存最后学习的位置
  useEffect(() => {
    if (currentChapter && words.length > 0) {
      storage.saveLastSession(currentChapter, currentIndex);
    }
  }, [currentChapter, currentIndex, words.length]);

  // 章节联动：当切换单词时自动更新章节
  useEffect(() => {
    if (currentIndex >= 0 && currentIndex < words.length) {
      const word = words[currentIndex];
      if (word && word.chapter !== currentChapter) {
        setCurrentChapter(word.chapter);
      }
    }
  }, [currentIndex, words, currentChapter]);

  const currentWord = words[currentIndex];

  const setWordFamiliarity = useCallback((wordId: string, level: FamiliarityLevel) => {
    setProgress(prev => {
      const newProgress = new Map(prev);
      const existing = newProgress.get(wordId);

      newProgress.set(wordId, {
        wordId,
        level,
        lastReviewed: getTodayDate(),
        reviewCount: (existing?.reviewCount || 0) + 1,
      });

      return newProgress;
    });
  }, []);

  const getWordProgress = useCallback((wordId: string): FamiliarityLevel => {
    return progress.get(wordId)?.level || 'unknown';
  }, [progress]);

  const nextWord = useCallback(() => {
    if (currentIndex < words.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  }, [currentIndex, words.length]);

  const prevWord = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  const goToWord = useCallback((index: number) => {
    if (index >= 0 && index < words.length) {
      setCurrentIndex(index);
    }
  }, [words.length]);

  const goToChapter = useCallback((chapterId: number) => {
    const chapter = chapters.find(c => c.id === chapterId);
    if (chapter && chapter.wordCount > 0) {
      setCurrentChapter(chapterId);
      setCurrentIndex(chapter.startIndex);
    }
  }, [chapters]);

  const getChapterWords = useCallback((chapterId: number): Word[] => {
    const chapter = chapters.find(c => c.id === chapterId);
    if (!chapter) return [];
    return words.slice(chapter.startIndex, chapter.endIndex + 1);
  }, [words, chapters]);

  return {
    words,
    chapters,
    currentChapter,
    currentWord,
    currentIndex,
    progress,
    loading,
    setWordFamiliarity,
    getWordProgress,
    nextWord,
    prevWord,
    goToWord,
    goToChapter,
    getChapterWords,
  };
};

// 导出类型供其他组件使用
export type { Word, Chapter, WordProgress, FamiliarityLevel, Definition };