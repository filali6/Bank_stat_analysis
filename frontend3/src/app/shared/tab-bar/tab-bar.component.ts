import { Component } from '@angular/core';

import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { WorkspaceTabsService } from '../../core/services/workspace-tabs.service';

@Component({
  selector: 'app-tab-bar',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './tab-bar.component.html',
  styleUrl: './tab-bar.component.css',
})
export class TabBarComponent {
  constructor(readonly workspace: WorkspaceTabsService) {}

  close(id: string, event: MouseEvent): void {
    event.stopPropagation();
    this.workspace.closeTab(id);
  }
}