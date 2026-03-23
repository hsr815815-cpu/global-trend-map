'use client';

import { createContext, useContext, useState, useCallback } from 'react';

export type Lang = 'en' | 'ko' | 'ja';

// ============================================================
// UI Translations
// ============================================================
const TRANSLATIONS: Record<string, Record<Lang, string>> = {
  // Header
  'countries':               { en: 'countries',        ko: '개국',              ja: 'カ国' },
  'trends':                  { en: 'trends',            ko: '트렌드',             ja: 'トレンド' },
  'Next update in':          { en: 'Next update in',    ko: '다음 업데이트',      ja: '次回更新まで' },
  'Updated':                 { en: 'Updated',           ko: '업데이트됨',         ja: '更新済み' },
  // TrendList
  'Global Rankings':         { en: 'Global Rankings',   ko: '글로벌 랭킹',        ja: 'グローバルランキング' },
  'Search trends or countries...': { en: 'Search trends or countries...', ko: '트렌드 또는 국가 검색...', ja: 'トレンドや国を検索...' },
  'Spotlight — #1 Global':   { en: 'Spotlight — #1 Global', ko: '스포트라이트 — 글로벌 1위', ja: 'スポットライト — グローバル1位' },
  'searches':                { en: 'searches',          ko: '검색수',             ja: '検索数' },
  'No trends match your search': { en: 'No trends match your search', ko: '검색 결과 없음', ja: '検索結果なし' },
  // Categories
  'All':                     { en: 'All',     ko: '전체',   ja: 'すべて' },
  'Sports':                  { en: 'Sports',  ko: '스포츠', ja: 'スポーツ' },
  'Tech':                    { en: 'Tech',    ko: '기술',   ja: 'テック' },
  'Music':                   { en: 'Music',   ko: '음악',   ja: '音楽' },
  'News':                    { en: 'News',    ko: '뉴스',   ja: 'ニュース' },
  'Movies':                  { en: 'Movies',  ko: '영화',   ja: '映画' },
  'Finance':                 { en: 'Finance', ko: '금융',   ja: '金融' },
  // RightPanel
  'Global Thermometer':      { en: 'Global Thermometer', ko: '글로벌 온도계',      ja: 'グローバル温度計' },
  'Trend Share':             { en: 'Trend Share',        ko: '트렌드 분포',         ja: 'トレンド分布' },
  'Rising Fast':             { en: 'Rising Fast',        ko: '급상승',              ja: '急上昇' },
  'No velocity data yet':    { en: 'No velocity data yet', ko: '급상승 데이터 없음', ja: '急上昇データなし' },
  'Global trend intensity across': { en: 'Global trend intensity across', ko: '글로벌 트렌드 강도', ja: 'グローバルトレンド強度' },
  // CountryPopup
  'avg temp':                { en: 'avg temp',           ko: '평균 온도',           ja: '平均温度' },
  'Top Trends':              { en: 'Top Trends',         ko: '인기 트렌드',          ja: 'トップトレンド' },
  'View All Trends →':       { en: 'View All Trends →',  ko: '전체 트렌드 →',        ja: '全トレンドを見る →' },
  // BottomCards
  'No data':                 { en: 'No data',            ko: '데이터 없음',          ja: 'データなし' },
  'World Temperature':       { en: 'World Temperature',  ko: '세계 온도',            ja: '世界の温度' },
  'Blog':                    { en: 'Blog',               ko: '블로그',               ja: 'ブログ' },
  'About':                   { en: 'About',              ko: '소개',                 ja: '概要' },
};

interface LanguageContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  /** Returns original or English keyword based on current language */
  kw: (keyword: string, keywordEn?: string) => string;
  /** Translates a UI string key */
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'en',
  setLang: () => {},
  kw: (_keyword, keywordEn) => keywordEn || _keyword,
  t: (key) => key,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>('en');

  const kw = useCallback(
    (keyword: string, keywordEn?: string) => {
      if (lang === 'en') return keywordEn || keyword;
      return keyword;
    },
    [lang]
  );

  const t = useCallback(
    (key: string) => TRANSLATIONS[key]?.[lang] ?? key,
    [lang]
  );

  return (
    <LanguageContext.Provider value={{ lang, setLang, kw, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
