import { Injectable, computed, signal } from '@angular/core';

import { EnrichmentApiService } from './enrichment-api.service';
import { StudySession } from './study-session';
import { TranslationService } from './translation.service';
import { StudySummary } from '../models/enriched-transaction.model';

export interface WorkspaceTab {
  id: string;
  type: 'dashboard' | 'study';
  closable: boolean;
  session?: StudySession;
}

let nextTabId = 1;

@Injectable({ providedIn: 'root' })
export class WorkspaceTabsService {
  private readonly _tabs = signal<WorkspaceTab[]>([{ id: 'dashboard', type: 'dashboard', closable: false }]);
  private readonly _activeTabId = signal('dashboard');

  readonly tabs = this._tabs.asReadonly();
  readonly activeTabId = this._activeTabId.asReadonly();

  readonly activeTab = computed<WorkspaceTab>(
    () => this._tabs().find((t) => t.id === this._activeTabId()) ?? this._tabs()[0]
  );

  constructor(private readonly api: EnrichmentApiService, private readonly translation: TranslationService) {}

  openNewStudyTab(): void {
    const id = 'study-' + nextTabId++;
    const session = new StudySession(this.api, this.translation);
    session.loadClients();
    this._tabs.update((tabs) => [...tabs, { id, type: 'study', closable: true, session }]);
    this._activeTabId.set(id);
  }

  openExistingStudyTab(row: StudySummary): void {
    const id = 'study-' + nextTabId++;
    const session = new StudySession(this.api, this.translation);
    this._tabs.update((tabs) => [...tabs, { id, type: 'study', closable: true, session }]);
    this._activeTabId.set(id);

    this.api.getStudy(row.id).subscribe({
      next: (study) => session.hydrateFromStudyOut(study),
      error: () => session.errorMessage.set(this.translation.t('error.generic')),
    });
  }

  switchTab(id: string): void {
    this._activeTabId.set(id);
  }

  closeTab(id: string): void {
    this._tabs.update((tabs) => tabs.filter((t) => t.id !== id));
    if (this._activeTabId() === id) {
      this._activeTabId.set('dashboard');
    }
  }

  goToDashboard(): void {
    this._activeTabId.set('dashboard');
  }
}