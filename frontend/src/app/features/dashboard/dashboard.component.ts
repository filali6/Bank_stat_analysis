import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';

import { EnrichmentApiService } from '../../core/services/enrichment-api.service';
import { WorkspaceTabsService } from '../../core/services/workspace-tabs.service';
import { StudySummary } from '../../core/models/enriched-transaction.model';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

const OUTPUT_LABELS: Record<string, string> = {
  credit: 'Credit underwriting',
  risk: 'Risk management',
  kyc: 'Customer insight / KYC',
  opportunities: 'Identifying commercial opportunities',
};

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  readonly studies = signal<StudySummary[]>([]);
  readonly isLoading = signal(false);

  constructor(private readonly workspace: WorkspaceTabsService, private readonly api: EnrichmentApiService) {}

  ngOnInit(): void {
    this.isLoading.set(true);
    this.api.listStudies().subscribe({
      next: (studies) => {
        this.studies.set(studies);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  get totalCount(): number {
    return this.studies().length;
  }

  get pendingCount(): number {
    return this.studies().filter((s) => s.decision_choice === 'request_info').length;
  }

  get validatedCount(): number {
    return this.studies().filter((s) => s.decision_choice === 'accept').length;
  }

  outputLabel(key: string): string {
    return OUTPUT_LABELS[key] ?? key;
  }

  statusClass(choice: string): string {
    if (choice === 'accept') return 'validated';
    if (choice === 'reject') return 'rejected';
    return 'review';
  }

  newStudy(): void {
    this.workspace.openNewStudyTab();
  }

  openRow(row: StudySummary): void {
    this.workspace.openExistingStudyTab(row);
  }
}