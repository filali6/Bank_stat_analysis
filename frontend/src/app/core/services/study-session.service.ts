import { Injectable, signal } from '@angular/core';

import { EnrichmentApiService } from './enrichment-api.service';
import { TranslationService } from './translation.service';
import { CategorizationResponse, EnrichmentResponse } from '../models/enriched-transaction.model';
import { ClientFeatures,LifestyleFeatures } from '../models/enriched-transaction.model';

export type OutputKey = 'credit' | 'risk' | 'kyc' | 'opportunities';

@Injectable({ providedIn: 'root' })
export class StudySessionService {
  readonly selectedOutput = signal<OutputKey | null>(null);
  readonly selectedFile = signal<File | null>(null);
  readonly enrichmentResult = signal<EnrichmentResponse | null>(null);
  readonly categorizationResult = signal<CategorizationResponse | null>(null);
  readonly isLoadingEnrichment = signal(false);
  readonly isLoadingCategorization = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly clientFeatures = signal<ClientFeatures | null>(null);
  readonly isLoadingFeatures = signal(false);
  readonly lifestyleFeatures = signal<LifestyleFeatures | null>(null);
  readonly isLoadingLifestyle = signal(false);

  constructor(
    private readonly api: EnrichmentApiService,
    private readonly translation: TranslationService
  ) {}

  selectOutput(key: OutputKey): void {
    this.selectedOutput.set(key);
  }

  uploadFile(file: File): void {
    this.selectedFile.set(file);
    this.categorizationResult.set(null);
    this.clientFeatures.set(null);
    this.isLoadingEnrichment.set(true);
    this.errorMessage.set(null);
    this.lifestyleFeatures.set(null);

    this.api.enrich(file).subscribe({
      next: (response) => {
        this.enrichmentResult.set(response);
        this.isLoadingEnrichment.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isLoadingEnrichment.set(false);
      },
    });
  }

  categorize(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.isLoadingCategorization.set(true);
    this.errorMessage.set(null);

    this.api.categorize(file).subscribe({
      next: (response) => {
        this.categorizationResult.set(response);
        this.isLoadingCategorization.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isLoadingCategorization.set(false);
      },
    });
  }

  reset(): void {
    this.selectedOutput.set(null);
    this.selectedFile.set(null);
    this.enrichmentResult.set(null);
    this.categorizationResult.set(null);
    this.clientFeatures.set(null);
    this.errorMessage.set(null);
    this.lifestyleFeatures.set(null);
  }
  computeFeatures(): void {
    const categorized = this.categorizationResult();
    if (!categorized) return;

    this.isLoadingFeatures.set(true);
    this.errorMessage.set(null);

    this.api.computeFeatures(categorized.transactions).subscribe({
      next: (features) => {
        this.clientFeatures.set(features);
        this.isLoadingFeatures.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isLoadingFeatures.set(false);
      },
    });
  }
  computeLifestyle(): void {
    const features = this.clientFeatures();
    if (!features) return;

    this.isLoadingLifestyle.set(true);
    this.errorMessage.set(null);

    this.api.computeLifestyle(features).subscribe({
      next: (lifestyle) => {
        this.lifestyleFeatures.set(lifestyle);
        this.isLoadingLifestyle.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isLoadingLifestyle.set(false);
      },
    });
  }
}
