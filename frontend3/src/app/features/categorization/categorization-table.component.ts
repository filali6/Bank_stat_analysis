import { Component, Input, computed, signal } from '@angular/core';

import { CategorizationResponse, CategorizedTransaction } from '../../core/models/enriched-transaction.model';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { PaginationComponent } from '../../shared/pagination/pagination.component';
import { PaginatedListController } from '../../shared/paginated-list/paginated-list.controller';

type StatusFilter = 'validated' | 'needs_review' | 'unreliable' | null;

@Component({
  selector: 'app-categorization-table',
  standalone: true,
  imports: [TranslatePipe, PaginationComponent],
  templateUrl: './categorization-table.component.html',
  styleUrl: './categorization-table.component.css',
})
export class CategorizationTableComponent {
  readonly list = new PaginatedListController<CategorizedTransaction>(
    (txn, query) =>
      txn.libelle_brut.toLowerCase().includes(query) ||
      txn.merchant.toLowerCase().includes(query) ||
      txn.category.toLowerCase().includes(query)
  );

  readonly selectedStatus = signal<StatusFilter>(null);

  private _result: CategorizationResponse | null = null;

  @Input() set result(value: CategorizationResponse | null) {
    this._result = value;
    this.selectedStatus.set(null);
    this.list.setItems(value?.transactions ?? []);
  }
  get result(): CategorizationResponse | null {
    return this._result;
  }

  readonly validatedCount = computed(
    () => this._result?.transactions.filter((t) => t.status === 'validated').length ?? 0
  );
  readonly needsReviewCount = computed(
    () => this._result?.transactions.filter((t) => t.status === 'needs_review').length ?? 0
  );
  readonly unreliableCount = computed(
    () => this._result?.transactions.filter((t) => t.status === 'unreliable').length ?? 0
  );

  /** Clicking a status card filters the table to only that status —
   * clicking the same one again clears the filter back to "all". */
  filterByStatus(status: StatusFilter): void {
    const next = this.selectedStatus() === status ? null : status;
    this.selectedStatus.set(next);
    this.list.setExtraFilter(next ? (txn) => txn.status === next : null);
  }
}