import { useState } from 'react';
import { Chapter } from '../types';

interface ChapterSelectorProps {
  chapters: Chapter[];
  currentChapter: number | null;
  onSelectChapter: (chapterId: number) => void;
  onSelectWord: (index: number) => void;
  chapterWordCount?: number;
}

export const ChapterSelector = ({
  chapters,
  currentChapter,
  onSelectChapter,
  onSelectWord,
  chapterWordCount = 0,
}: ChapterSelectorProps) => {
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
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={handleJumpToWord}
                className="btn btn-primary"
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
};