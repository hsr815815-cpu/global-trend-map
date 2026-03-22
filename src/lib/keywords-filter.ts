// ============================================================
// KEYWORD CONTENT FILTER
// Based on Google AdSense Policies
// Blocks: adult, violence, hate, gambling, drugs, terrorism,
//         extremism, weapons, and other restricted content
// ============================================================

// Blocked term categories
const ADULT_TERMS = [
  'porn', 'pornography', 'xxx', 'nude', 'naked', 'sex tape', 'onlyfans leak',
  'escort', 'prostitute', 'camgirl', 'nsfw', 'erotic', 'hentai', 'adult content',
  'strip club', 'hookup', 'casual sex', 'fetish', 'bdsm',
];

const VIOLENCE_TERMS = [
  'murder tutorial', 'how to kill', 'assassination guide', 'bomb making',
  'mass shooting', 'torture video', 'gore video', 'snuff film',
  'violent extremism', 'school shooting', 'how to attack',
];

const HATE_SPEECH_TERMS = [
  'white supremacy', 'neo nazi', 'racial slur', 'ethnic cleansing',
  'antisemitic', 'islamophobia hate', 'homophobic slur', 'hate group',
  'white power', 'kkk rally', 'genocide support',
];

const GAMBLING_TERMS = [
  'illegal casino', 'unlicensed gambling', 'betting fraud', 'rigged slots',
  'underground poker', 'illegal sports betting',
];

const DRUGS_TERMS = [
  'buy cocaine', 'buy heroin', 'meth recipe', 'drug synthesis',
  'buy fentanyl', 'dark web drugs', 'buy mdma online', 'ketamine buy',
  'buy crack', 'drug trafficking',
];

const TERRORISM_TERMS = [
  'isis recruitment', 'al qaeda', 'terror attack plan', 'jihad recruitment',
  'extremist manifesto', 'how to radicalize', 'bomb vest tutorial',
  'terrorist financing',
];

const WEAPONS_TERMS = [
  'ghost gun instructions', '3d printed gun illegal', 'illegal weapons buy',
  'unregistered firearm buy', 'silencer illegal', 'automatic weapon illegal',
  'explosives tutorial',
];

const MISINFORMATION_TERMS = [
  'covid vaccine microchip', 'flat earth proof', 'election stolen proof',
  'qanon drops', 'crisis actor proof', '5g cause covid',
  'chemtrail conspiracy instructions',
];

// All blocked patterns combined
const ALL_BLOCKED_TERMS = [
  ...ADULT_TERMS,
  ...VIOLENCE_TERMS,
  ...HATE_SPEECH_TERMS,
  ...GAMBLING_TERMS,
  ...DRUGS_TERMS,
  ...TERRORISM_TERMS,
  ...WEAPONS_TERMS,
  ...MISINFORMATION_TERMS,
];

// Build a regex for efficient matching
// We use word boundaries where possible
function buildBlockedRegex(): RegExp {
  const escaped = ALL_BLOCKED_TERMS.map((term) =>
    term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  );
  return new RegExp(`(?:${escaped.join('|')})`, 'i');
}

const BLOCKED_REGEX = buildBlockedRegex();

// ============================================================
// FILTER FUNCTIONS
// ============================================================

/**
 * Check if a single keyword passes the content filter.
 * Returns true if the keyword is SAFE (should be shown).
 */
export function isKeywordSafe(keyword: string): boolean {
  if (!keyword || typeof keyword !== 'string') return false;
  return !BLOCKED_REGEX.test(keyword.toLowerCase());
}

/**
 * Filter an array of keyword strings, returning only safe ones.
 * Also returns a count of how many were blocked.
 */
export function filterKeywords(keywords: string[]): {
  safe: string[];
  blocked: number;
} {
  const safe: string[] = [];
  let blocked = 0;

  for (const kw of keywords) {
    if (isKeywordSafe(kw)) {
      safe.push(kw);
    } else {
      blocked++;
    }
  }

  return { safe, blocked };
}

/**
 * Filter an array of trend objects by their keyword field.
 * Generic version that works with any object having a `keyword` property.
 */
export function filterTrendObjects<T extends { keyword: string }>(
  trends: T[]
): { safe: T[]; blocked: number } {
  const safe: T[] = [];
  let blocked = 0;

  for (const trend of trends) {
    if (isKeywordSafe(trend.keyword)) {
      safe.push(trend);
    } else {
      blocked++;
      // Log blocked keywords server-side only (never expose to client)
      if (typeof process !== 'undefined') {
        console.warn(`[ContentFilter] Blocked keyword: "${trend.keyword}"`);
      }
    }
  }

  return { safe, blocked };
}

/**
 * Get a redacted version of a keyword for logging purposes.
 * Replaces middle characters with asterisks.
 */
export function redactKeyword(keyword: string): string {
  if (keyword.length <= 4) return '****';
  const visible = Math.floor(keyword.length * 0.3);
  return (
    keyword.slice(0, visible) +
    '*'.repeat(keyword.length - visible * 2) +
    keyword.slice(-visible)
  );
}

/**
 * Content category classification helper.
 * Returns whether a keyword is in a "sensitive but allowed" category
 * that may require additional review (not blocked, but flagged).
 */
export function isSensitiveCategory(keyword: string): boolean {
  const sensitiveTerms = [
    'death', 'funeral', 'suicide prevention', 'mental health crisis',
    'accident', 'disaster', 'flood', 'earthquake', 'war news',
    'protest', 'riot',
  ];
  const lower = keyword.toLowerCase();
  return sensitiveTerms.some((term) => lower.includes(term));
}

/**
 * Full pipeline: filter + flag sensitive content.
 * Returns safe trends and metadata about what was filtered.
 */
export function runContentPipeline<T extends { keyword: string }>(
  trends: T[]
): {
  safe: T[];
  sensitive: T[];
  blockedCount: number;
  totalInput: number;
} {
  const totalInput = trends.length;
  const { safe: afterBlock, blocked: blockedCount } = filterTrendObjects(trends);

  const safe: T[] = [];
  const sensitive: T[] = [];

  for (const trend of afterBlock) {
    if (isSensitiveCategory(trend.keyword)) {
      sensitive.push(trend);
    } else {
      safe.push(trend);
    }
  }

  return { safe, sensitive, blockedCount, totalInput };
}
