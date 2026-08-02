import { Signal, computed, signal } from '@angular/core';

const DEFAULT_PAGE_SIZE = 10;

/**
 * Search + pagination behavior shared by every results table in the
 * app. Deliberately NOT an Angular service (no @Injectable) — each
 * table component creates its own instance, so state never leaks
 * between the Enrichment table and the Categorization table.
 */
export class PaginatedListController<T> {
  private readonly items = signal<T[]>([]);

  readonly search = signal('');
  readonly page = signal(1);

  readonly filtered: Signal<T[]>;
  readonly totalPages: Signal<number>;
  readonly pageItems: Signal<T[]>;
  readonly rangeStart: Signal<number>;
  readonly rangeEnd: Signal<number>;

  constructor(
    private readonly matchesSearch: (item: T, query: string) => boolean,
    private readonly pageSize: number = DEFAULT_PAGE_SIZE
  ) {
    this.filtered = computed(() => {
      const query = this.search().toLowerCase().trim();
      const all = this.items();
      return query ? all.filter((item) => this.matchesSearch(item, query)) : all;
    });

    this.totalPages = computed(() => Math.max(1, Math.ceil(this.filtered().length / this.pageSize)));

    this.pageItems = computed(() => {
      const start = (this.page() - 1) * this.pageSize;
      return this.filtered().slice(start, start + this.pageSize);
    });

    this.rangeStart = computed(() => (this.filtered().length === 0 ? 0 : (this.page() - 1) * this.pageSize + 1));
    this.rangeEnd = computed(() => Math.min(this.page() * this.pageSize, this.filtered().length));
  }

  setItems(items: T[]): void {
    this.items.set(items);
    this.search.set('');
    this.page.set(1);
  }

  onSearchChange(value: string): void {
    this.search.set(value);
    this.page.set(1);
  }

  onPageChange(page: number): void {
    this.page.set(page);
  }
}