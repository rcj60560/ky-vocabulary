export type FamiliarityLevel = 'unknown' | 'unfamiliar' | 'familiar' | 'known';

export interface Word {
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

export interface Definition {
  part: string;
  meaning: string;
}

interface WordCardProps {
  word: Word;
  familiarity: FamiliarityLevel;
  onFamiliarityChange: (level: FamiliarityLevel) => void;
}

const LEVEL_LABELS: Record<FamiliarityLevel, { label: string; icon: string }> = {
  unknown: { label: '未学', icon: '○' },
  unfamiliar: { label: '不认识', icon: '✗' },
  familiar: { label: '熟悉', icon: '◐' },
  known: { label: '认识', icon: '✓' },
};

export const WordCard = ({ word, familiarity, onFamiliarityChange }: WordCardProps) => {
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
};