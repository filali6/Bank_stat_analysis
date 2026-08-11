import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export type Lang = 'fr' | 'en';

type TranslationDict = Record<string, unknown>;

/**
 * Single source of truth for the active language and for looking up
 * translated strings. Both dictionaries are fetched once, at app
 * startup (see the APP_INITIALIZER in app.config.ts) — not on every
 * lookup — so switching languages is instant and offline-safe.
 */
@Injectable({ providedIn: 'root' })
export class TranslationService {
  readonly currentLang = signal<Lang>('fr');

  private dictionaries: Record<Lang, TranslationDict> = { fr: {}, en: {} };

  constructor(private readonly http: HttpClient) {}

  /** Loads both dictionaries from /i18n/*.json. Call once, before bootstrap. */
  async load(): Promise<void> {
    const [fr, en] = await Promise.all([
      firstValueFrom(this.http.get<TranslationDict>('i18n/fr.json')),
      firstValueFrom(this.http.get<TranslationDict>('i18n/en.json')),
    ]);
    this.dictionaries = { fr, en };
  }

  setLang(lang: Lang): void {
    this.currentLang.set(lang);
  }

  /**
   * Looks up a dot-notation key (e.g. "hero.title") in the active
   * dictionary. Returns the key itself if nothing is found, so a
   * missing translation is visible/debuggable instead of blank.
   */
  t(key: string): string {
    const dict = this.dictionaries[this.currentLang()];
    const value = key
      .split('.')
      .reduce<unknown>((acc, part) => (acc as Record<string, unknown> | undefined)?.[part], dict);
    return typeof value === 'string' ? value : key;
  }
}
