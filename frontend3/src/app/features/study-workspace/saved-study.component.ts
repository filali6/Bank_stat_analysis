import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { StudySession } from '../../core/services/study-session';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { WorkspaceTabsService } from '../../core/services/workspace-tabs.service';

@Component({
  selector: 'app-saved-study',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './saved-study.component.html',
  styleUrl: './saved-study.component.css',
})
export class SavedStudyComponent {
  @Input({ required: true }) session!: StudySession;

  constructor(private readonly workspace: WorkspaceTabsService) {}

  edit(): void {
    this.session.reopenForEditing();
  }

  backToDashboard(): void {
    this.workspace.goToDashboard();
  }
}