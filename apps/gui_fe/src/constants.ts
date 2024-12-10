export const DANNCE_MODES = ['COM', 'DANNCE', 'SDANNCE'] as const;

export type DannceMode = (typeof DANNCE_MODES)[number];
