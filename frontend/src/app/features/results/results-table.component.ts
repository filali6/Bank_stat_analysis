import { CommonModule } from '@angular/common';
import { Component, Input, computed, signal } from '@angular/core';

import { EnrichmentResponse } from '../../core/models/enriched-transaction.model';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

type StatusFilter = 'all' | 'validated' | 'review' | 'unknown';

@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [CommonModule,TranslatePipe],
  templateUrl: './results-table.component.html',
  styleUrl: './results-table.component.css',
})
export class ResultsTableComponent {
  private readonly _result = signal<EnrichmentResponse | null>(null);

  @Input() set result(value: EnrichmentResponse | null) {
    this._result.set(value);
    //this.statusFilter.set('all');
    this.search.set('');
  }

  //readonly statusFilter = signal<StatusFilter>('all');
  readonly search = signal('');

 readonly filteredTransactions = computed(() => {
    const result = this._result();
    if (!result) return [];

    const query = this.search().toLowerCase().trim();
    if (!query) return result.transactions;

    return result.transactions.filter(
      (txn) =>
        txn.libelle_brut.toLowerCase().includes(query) ||
        txn.merchant.toLowerCase().includes(query)
    );
  });
  get result(): EnrichmentResponse | null {
    return this._result();
  }

 
  

  onSearchChange(value: string): void {
    this.search.set(value);
  }

   
}
