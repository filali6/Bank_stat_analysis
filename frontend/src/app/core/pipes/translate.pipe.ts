import { Pipe, PipeTransform } from '@angular/core';

import { TranslationService } from '../services/translation.service';

@Pipe({ name: 'translate', standalone: true, pure: false })
export class TranslatePipe implements PipeTransform {
  constructor(private readonly translation: TranslationService) {}

  transform(key: string): string {
    return this.translation.t(key);
  }
}