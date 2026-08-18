import { Component } from '@angular/core';

import { TopHeaderComponent } from './shared/top-header/top-header.component';
import { TabBarComponent } from './shared/tab-bar/tab-bar.component';
import { WorkspaceTabsService } from './core/services/workspace-tabs.service';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { StudyWorkspaceComponent } from './features/study-workspace/study-workspace.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [TopHeaderComponent, TabBarComponent, DashboardComponent, StudyWorkspaceComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  constructor(readonly workspace: WorkspaceTabsService) {}
}