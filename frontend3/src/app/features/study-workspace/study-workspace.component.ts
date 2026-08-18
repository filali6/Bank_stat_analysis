import { Component, Input } from '@angular/core';

import { WorkspaceTab } from '../../core/services/workspace-tabs.service';
import { ClientStepComponent } from './client-step.component';
import { EngineStepsComponent } from './engine-steps.component';
import { DecisionWorkspaceComponent } from './decision-workspace.component';
import { SavedStudyComponent } from './saved-study.component';

@Component({
  selector: 'app-study-workspace',
  standalone: true,
  imports: [ClientStepComponent, EngineStepsComponent, DecisionWorkspaceComponent, SavedStudyComponent],
  templateUrl: './study-workspace.component.html',
  styleUrl: './study-workspace.component.css',
})
export class StudyWorkspaceComponent {
  @Input({ required: true }) tab!: WorkspaceTab;
}