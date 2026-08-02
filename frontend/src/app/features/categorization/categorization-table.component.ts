import { Component, Input } from '@angular/core';

import { CategorizationResponse, CategorizedTransaction } from '../../core/models/enriched-transaction.model';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { PaginationComponent } from '../../shared/pagination/pagination.component';
import { PaginatedListController } from '../../shared/paginated-list/paginated-list.controller';

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

  private _result: CategorizationResponse | null = null;

  @Input() set result(value: CategorizationResponse | null) {
    this._result = value;
    this.list.setItems(value?.transactions ?? []);
  }
  get result(): CategorizationResponse | null {
    return this._result;
  }
}