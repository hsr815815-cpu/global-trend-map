'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

export type Lang = 'en' | 'ko' | 'ja';

interface LanguageContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  /** Returns the display string for a keyword: English when EN, original otherwise */
  kw: (keyword: string, keywordEn?: string) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'en',
  setLang: () => {},
  kw: (keyword, keywordEn) => keywordEn || keyword,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>('en');
  const router = useRouter();

  const setLang = useCallback((l: Lang) => {
    if (l === 'ko') {
      router.push('/ko');
      return;
    }
    if (l === 'ja') {
      router.push('/ja');
      return;
    }
    setLangState(l);
  }, [router]);

  const kw = useCallback(
    (keyword: string, keywordEn?: string) => {
      if (lang === 'en') return keywordEn || keyword;
      return keyword;
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
