import { Component, computed, signal } from '@angular/core';

import { EnrichmentApiService } from './core/services/enrichment-api.service';
import { CategorizationResponse, EnrichmentResponse } from './core/models/enriched-transaction.model';
import { UploadZoneComponent } from './features/upload/upload-zone.component';
import { EnrichmentTableComponent } from './features/enrichement/enrichment-table.component';
import { CategorizationTableComponent } from './features/categorization/categorization-table.component';
import { StepperComponent, Step } from './shared/stepper/stepper.component';
import { TranslationService } from './core/services/translation.service';
import { TranslatePipe } from './core/pipes/translate.pipe';
import { HeaderComponent } from './shared/header/header.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [UploadZoneComponent, EnrichmentTableComponent, CategorizationTableComponent, StepperComponent, TranslatePipe,HeaderComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  readonly selectedFile = signal<File | null>(null);
  readonly enrichmentResult = signal<EnrichmentResponse | null>(null);
  readonly categorizationResult = signal<CategorizationResponse | null>(null);

  readonly isLoadingEnrichment = signal(false);
  readonly isLoadingCategorization = signal(false);
  readonly errorMessage = signal<string | null>(null);

  readonly currentStep = signal(1);

  readonly steps = computed<Step[]>(() => [
    { label: this.translation.t('stepper.step1'), enabled: true },
    { label: this.translation.t('stepper.step2'), enabled: true },
    { label: this.translation.t('stepper.step3'), enabled: false },
    { label: this.translation.t('stepper.step4'), enabled: false },
  ]);

  constructor(
    private readonly api: EnrichmentApiService,
    private readonly translation: TranslationService
  ) {}

  onFileSelected(file: File): void {
    this.selectedFile.set(file);
    this.categorizationResult.set(null); // un nouveau fichier invalide la catégorisation précédente
    this.isLoadingEnrichment.set(true);
    this.errorMessage.set(null);

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

  onCategorize(): void {
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

  goToStep(step: number): void {
    this.currentStep.set(step);
  }
}