export type FamiliarityLevel = 'unknown' | 'unfamiliar' | 'familiar' | 'known';

export interface WordProgress {
  wordId: string;
  level: FamiliarityLevel;
  lastReviewed: string;
  reviewCount: number;
}

interface HeatmapProps {
  progress: Map<string, WordProgress>;
  totalWords: number;
}

const getLevelColor = (level: FamiliarityLevel): number => {
  switch (level) {
    case 'known':
      return 4;
    case 'familiar':
      return 3;
    case 'unfamiliar':
      return 2;
    default:
      return 0;
  }
};

export const Heatmap = ({ progress, totalWords }: HeatmapProps) => {
  const GRID_SIZE = 100;
  const cells = Array(GRID_SIZE).fill(null);

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
              const colorLevel = wordProgress ? getLevelColor(wordProgress.level) : 0;

              return (
                <div
                  key={idx}
                  className={`w-3 h-3 rounded-sm transition-all duration-200 ${
                    colorLevel === 0
                      ? 'bg-gray-100'
                      : colorLevel === 2
                      ? 'bg-green-300'
                      : colorLevel === 3
                      ? 'bg-green-500'
                      : 'bg-green-700'
                  }`}
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
            { level: 0, label: 'Not reviewed', color: 'bg-gray-100' },
            { level: 2, label: 'Unfamiliar', color: 'bg-green-300' },
            { level: 3, label: 'Familiar', color: 'bg-green-500' },
            { level: 4, label: 'Known', color: 'bg-green-700' },
          ].map((item) => (
            <div key={item.level} className="flex items-center gap-2">
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
};