import { Component } from '@angular/core';

import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { Lang, TranslationService } from '../../core/services/translation.service';
import { WorkspaceTabsService } from '../../core/services/workspace-tabs.service';

@Component({
  selector: 'app-top-header',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './top-header.component.html',
  styleUrl: './top-header.component.css',
})
export class TopHeaderComponent {
  constructor(readonly translation: TranslationService, readonly workspace: WorkspaceTabsService) {}

  setLang(lang: Lang): void {
    this.translation.setLang(lang);
  }
}