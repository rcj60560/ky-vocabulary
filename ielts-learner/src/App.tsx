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

    const chapters: Chapter[] = data.chapters.map((c: any) => ({
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

// 组件
function ChapterSelector({
  chapters,
  currentChapter,
  onSelectChapter,
  onSelectWord,
  chapterWordCount,
}: {
  chapters: Chapter[];
  currentChapter: number | null;
  onSelectChapter: (id: number) => void;
  onSelectWord: (index: number) => void;
  chapterWordCount?: number;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedWordIndex, setSelectedWordIndex] = useState('');

  const handleSelectChapter = (chapterId: number) => {
    onSelectChapter(chapterId);
    setIsOpen(false);
  };

  const handleJumpToWord = () => {
    const index = parseInt(selectedWordIndex);
    if (!isNaN(index) && index >= 1) {
      onSelectWord(index - 1);
    }
    setSelectedWordIndex('');
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <span className="text-gray-600">
          {currentChapter
            ? chapters.find(c => c.id === currentChapter)?.name || `Chapter ${currentChapter}`
            : 'Select Chapter'}
        </span>
        <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800 mb-3">Jump to Word</h3>
            <div className="flex gap-2">
              <input
                type="number"
                min="1"
                placeholder="Word #"
                value={selectedWordIndex}
                onChange={(e) => setSelectedWordIndex(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleJumpToWord}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Go
              </button>
            </div>
          </div>

          <div className="max-h-64 overflow-y-auto">
            {chapters.map((chapter) => (
              <button
                key={chapter.id}
                onClick={() => handleSelectChapter(chapter.id)}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                  currentChapter === chapter.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium">{chapter.name}</span>
                  {chapter.wordCount > 0 && (
                    <span className="text-xs text-gray-500">{chapter.wordCount} words</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Navigation({ onPrev, onNext, currentIndex, total }: { onPrev: () => void; onNext: () => void; currentIndex: number; total: number }) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') {
        onPrev();
      } else if (e.key === 'ArrowRight') {
        onNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onPrev, onNext]);

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
      <div className="max-w-3xl mx-auto flex items-center justify-between">
        <button
          onClick={onPrev}
          disabled={currentIndex === 0}
          className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
            currentIndex === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          ← Previous
        </button>

        <div className="text-sm text-gray-600">
          {currentIndex + 1} / {total}
        </div>

        <button
          onClick={onNext}
          disabled={currentIndex === total - 1}
          className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
            currentIndex === total - 1
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          Next →
        </button>
      </div>
    </div>
  );
}

function Heatmap({ progress, totalWords }: { progress: Map<string, WordProgress>; totalWords: number }) {
  const GRID_SIZE = 100;
  const cells = Array(GRID_SIZE).fill(null);

  const getLevelColor = (level: FamiliarityLevel): string => {
    switch (level) {
      case 'known': return 'bg-green-700';
      case 'familiar': return 'bg-green-500';
      case 'unfamiliar': return 'bg-green-300';
      default: return 'bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Learning Progress</h3>

      <div className="flex items-start gap-8">
        <div className="flex-1">
          <div
            className="grid gap-1"
            style={{ gridTemplateColumns: `repeat(20, minmax(0, 1fr))` }}
          >
            {cells.map((_, idx) => {
              const wordProgress = Array.from(progress.values())[idx];
              const colorClass = wordProgress ? getLevelColor(wordProgress.level) : 'bg-gray-100';

              return (
                <div
                  key={idx}
                  className={`w-3 h-3 rounded-sm transition-all duration-200 ${colorClass}`}
                  title={wordProgress ? `${wordProgress.level} - reviewed ${wordProgress.reviewCount} times` : 'Not reviewed'}
                />
              );
            })}
          </div>
          <p className="text-xs text-gray-500 mt-3 text-center">
            {progress.size} of {totalWords} words reviewed
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-xs font-medium text-gray-600">Legend:</span>
          {[
            { label: 'Not reviewed', color: 'bg-gray-100' },
            { label: 'Unfamiliar', color: 'bg-green-300' },
            { label: 'Familiar', color: 'bg-green-500' },
            { label: 'Known', color: 'bg-green-700' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded-sm ${item.color}`} />
              <span className="text-xs text-gray-600">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
        {[
          { label: 'Total', value: totalWords, color: 'text-gray-600' },
          { label: 'Known', value: Array.from(progress.values()).filter(p => p.level === 'known').length, color: 'text-blue-600' },
          { label: 'Familiar', value: Array.from(progress.values()).filter(p => p.level === 'familiar').length, color: 'text-yellow-600' },
          { label: 'Unfamiliar', value: Array.from(progress.values()).filter(p => p.level === 'unfamiliar').length, color: 'text-red-600' },
        ].map((stat) => (
          <div key={stat.label} className="text-center">
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function WordCard({ word, familiarity, onFamiliarityChange }: { word: Word; familiarity: FamiliarityLevel; onFamiliarityChange: (level: FamiliarityLevel) => void }) {
  const LEVEL_LABELS: Record<FamiliarityLevel, { label: string; icon: string }> = {
    unknown: { label: '未学', icon: '○' },
    unfamiliar: { label: '不认识', icon: '✗' },
    familiar: { label: '熟悉', icon: '◐' },
    known: { label: '认识', icon: '✓' },
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 p-8 max-w-3xl mx-auto transition-all duration-300">
      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">{word.word}</h1>
        {word.phonetic && (
          <p className="text-lg text-gray-500 font-mono">{word.phonetic}</p>
        )}
      </div>

      {word.partOfSpeech && (
        <div className="mb-4">
          <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-md text-xs font-medium">
            {word.partOfSpeech}
          </span>
        </div>
      )}

      {word.definitions && word.definitions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Definition
          </h3>
          <div className="space-y-2">
            {word.definitions.map((def, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-gray-400">{def.part}</span>
                <span className="text-gray-800">{def.meaning}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {word.collocations && word.collocations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Collocations
          </h3>
          <div className="flex flex-wrap gap-2">
            {word.collocations.map((col, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md text-sm"
              >
                {col}
              </span>
            ))}
          </div>
        </div>
      )}

      {word.examples && word.examples.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Examples
          </h3>
          <div className="space-y-3">
            {word.examples.map((ex, idx) => (
              <div key={idx} className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                <p className="text-gray-700">{ex}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          How well do you know this word?
        </h3>
        <div className="flex gap-2">
          {(Object.keys(LEVEL_LABELS) as FamiliarityLevel[]).map((level) => (
            <button
              key={level}
              onClick={() => onFamiliarityChange(level)}
              className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
                familiarity === level
                  ? `bg-blue-100 text-blue-700 ring-2 ring-offset-2 ring-blue-500`
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <div className="text-lg">{LEVEL_LABELS[level].icon}</div>
              <div className="text-xs mt-1">{LEVEL_LABELS[level].label}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function App() {
  const [words, setWords] = useState<Word[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentChapter, setCurrentChapter] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [progress, setProgress] = useState<Map<string, WordProgress>>(new Map());
  const [showHeatmap, setShowHeatmap] = useState(false);

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
        setCurrentChapter(lastSession.chapter);
        setCurrentIndex(lastSession.index);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading IELTS vocabulary...</p>
        </div>
      </div>
    );
  }

  if (!currentWord) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">No words loaded. Please check the data file.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-800">IELTS Learner</h1>
            <ChapterSelector
              chapters={chapters}
              currentChapter={currentChapter}
              onSelectChapter={goToChapter}
              onSelectWord={goToWord}
              chapterWordCount={words.length}
            />
          </div>
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            {showHeatmap ? 'Back to Cards' : 'Progress'}
          </button>
        </div>
      </header>

      <main className="pb-24">
        {showHeatmap ? (
          <div className="max-w-4xl mx-auto p-6">
            <Heatmap progress={progress} totalWords={words.length} />
          </div>
        ) : (
          <div className="py-8 px-4">
            <WordCard
              word={currentWord}
              familiarity={getWordProgress(currentWord.id)}
              onFamiliarityChange={(level) => setWordFamiliarity(currentWord.id, level)}
            />
          </div>
        )}
      </main>

      {!showHeatmap && (
        <Navigation
          onPrev={prevWord}
          onNext={nextWord}
          currentIndex={currentIndex}
          total={words.length}
        />
      )}

      {!showHeatmap && (
        <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 text-xs text-gray-400">
          Press ← → to navigate
        </div>
      )}
    </div>
  );
}

export default App;