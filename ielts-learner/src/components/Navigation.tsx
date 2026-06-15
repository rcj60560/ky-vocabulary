import { useEffect } from 'react';

interface NavigationProps {
  onPrev: () => void;
  onNext: () => void;
  currentIndex: number;
  total: number;
}

export const Navigation = ({ onPrev, onNext, currentIndex, total }: NavigationProps) => {
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
};