import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export type Lang = 'fr' | 'en';

type TranslationDict = Record<string, unknown>;

@Injectable({ providedIn: 'root' })
export class TranslationService {
  readonly currentLang = signal<Lang>('fr');

  private dictionaries: Record<Lang, TranslationDict> = { fr: {}, en: {} };

  constructor(private readonly http: HttpClient) {}

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

  t(key: string): string {
    const dict = this.dictionaries[this.currentLang()];
    const value = key
      .split('.')
      .reduce<unknown>((acc, part) => (acc as Record<string, unknown> | undefined)?.[part], dict);
    return typeof value === 'string' ? value : key;
  }
}