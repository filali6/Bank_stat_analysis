import { Component, Input } from '@angular/core';

import { EnrichedTransaction, EnrichmentResponse } from '../../core/models/enriched-transaction.model';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { PaginationComponent } from '../../shared/pagination/pagination.component';
import { PaginatedListController } from '../../shared/paginated-list/paginated-list.controller';

@Component({
  selector: 'app-enrichment-table',
  standalone: true,
  imports: [TranslatePipe, PaginationComponent],
  templateUrl: './enrichment-table.component.html',
  styleUrl: './enrichment-table.component.css',
})
export class EnrichmentTableComponent {
  readonly list = new PaginatedListController<EnrichedTransaction>(
    (txn, query) => txn.libelle_brut.toLowerCase().includes(query) || txn.merchant.toLowerCase().includes(query)
  );

  private _result: EnrichmentResponse | null = null;

  @Input() set result(value: EnrichmentResponse | null) {
    this._result = value;
    this.list.setItems(value?.transactions ?? []);
  }
  get result(): EnrichmentResponse | null {
    return this._result;
  }
}