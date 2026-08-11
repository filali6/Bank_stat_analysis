import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { Lang, TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, TranslatePipe],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
})
export class SidebarComponent {
  constructor(readonly translation: TranslationService) {}

  setLang(lang: Lang): void {
    this.translation.setLang(lang);
  }
}