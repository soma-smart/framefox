declare module 'detect-language' {
  export function detectLanguage(code: string): Promise<string>;
}