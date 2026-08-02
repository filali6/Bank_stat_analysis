import { Component } from '@angular/core';

import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { Lang, TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css',
})
export class HeaderComponent {
  constructor(readonly translation: TranslationService) {}

  setLang(lang: Lang): void {
    this.translation.setLang(lang);
  }
}