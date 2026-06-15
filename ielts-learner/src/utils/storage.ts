const STORAGE_KEYS = {
  PROGRESS: 'ielts-learner-progress',
  HEATMAP: 'ielts-learner-heatmap',
  LAST_SESSION: 'ielts-learner-last-session',
};

export const storage = {
  getProgress: (): Map<string, any> => {
    const data = localStorage.getItem(STORAGE_KEYS.PROGRESS);
    return data ? new Map(JSON.parse(data)) : new Map();
  },

  saveProgress: (progress: Map<string, any>) => {
    localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify([...progress]));
  },

  getHeatmap: (): any[] => {
    const data = localStorage.getItem(STORAGE_KEYS.HEATMAP);
    return data ? JSON.parse(data) : [];
  },

  saveHeatmap: (heatmap: any[]) => {
    localStorage.setItem(STORAGE_KEYS.HEATMAP, JSON.stringify(heatmap));
  },

  getLastSession: (): { chapter: number; index: number } | null => {
    const data = localStorage.getItem(STORAGE_KEYS.LAST_SESSION);
    return data ? JSON.parse(data) : null;
  },

  saveLastSession: (chapter: number, index: number) => {
    localStorage.setItem(STORAGE_KEYS.LAST_SESSION, JSON.stringify({ chapter, index }));
  },

  clearAll: () => {
    Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
  },
};

export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const getTodayDate = (): string => {
  return new Date().toISOString().split('T')[0];
};

export const formatDate = (date: string): string => {
  const d = new Date(date);
  return d.toLocaleDateString('zh-CN');
};