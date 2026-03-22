'use client';

import { createContext, useContext, useState, useCallback } from 'react';

export type Lang = 'en' | 'ko' | 'ja';

interface LanguageContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  /** Returns the display string for a keyword based on current language */
  kw: (keyword: string, keywordEn?: string) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'en',
  setLang: () => {},
  kw: (_keyword, keywordEn) => keywordEn || _keyword,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>('en');

  const kw = useCallback(
    (keyword: string, keywordEn?: string) => {
      if (lang === 'en') return keywordEn || keyword;
      return keyword; // KO/JA: show original keyword
    },
    [lang]
  );

  return (
    <LanguageContext.Provider value={{ lang, setLang, kw }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
