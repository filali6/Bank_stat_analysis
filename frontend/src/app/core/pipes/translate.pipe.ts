import { Pipe, PipeTransform } from '@angular/core';

import { TranslationService } from '../services/translation.service';

/**
 * Marked `pure: false` on purpose: a normal (pure) pipe only re-runs
 * when its input (the key) changes — but here the OUTPUT must also
 * change when the active language changes, even though the key itself
 * stays the same. Impure pipes re-run on every change detection cycle,
 * which is fine here since translation lookups are cheap.
 */
@Pipe({ name: 'translate', standalone: true, pure: false })
export class TranslatePipe implements PipeTransform {
  constructor(private readonly translation: TranslationService) {}

  transform(key: string): string {
    return this.translation.t(key);
  }
}
