import { Injectable, signal } from '@angular/core';

import { EnrichmentApiService } from './enrichment-api.service';
import { TranslationService } from './translation.service';
import {
  CategorizationResponse,
  EnrichmentResponse,
  ClientFeatures,
  LifestyleFeatures,
  DecisionResult,
  AffordabilityResult,
  Client,
  SaveStudyRequest,
  StudyOut,
} from '../models/enriched-transaction.model';

export type OutputKey = 'credit' | 'risk' | 'kyc' | 'opportunities';
export type DecisionChoice = 'accept' | 'reject' | 'request_info';

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
  readonly decisionResult = signal<DecisionResult | null>(null);
  readonly isLoadingDecision = signal(false);
  readonly affordabilityResult = signal<AffordabilityResult | null>(null);
  readonly isCheckingAffordability = signal(false);

  // --- Client picker (FR-A2) ------------------------------------------------
  readonly clients = signal<Client[]>([]);
  readonly isLoadingClients = signal(false);
  readonly selectedClientId = signal<number | null>(null);
  readonly newClientLabel = signal('');

  // --- Persisted study (FR-A16, FR-A17) --------------------------------------
  readonly savedStudy = signal<StudyOut | null>(null);
  readonly isSavingStudy = signal(false);

  constructor(
    private readonly api: EnrichmentApiService,
    private readonly translation: TranslationService
  ) {}

  selectOutput(key: OutputKey): void {
    this.selectedOutput.set(key);
  }

  loadClients(): void {
    this.isLoadingClients.set(true);
    this.api.getClients().subscribe({
      next: (clients) => {
        this.clients.set(clients);
        this.isLoadingClients.set(false);
      },
      error: () => this.isLoadingClients.set(false),
    });
  }

  selectExistingClient(id: number | null): void {
    this.selectedClientId.set(id);
    if (id !== null) {
      this.newClientLabel.set('');
    }
  }

  setNewClientLabel(label: string): void {
    this.newClientLabel.set(label);
    if (label.trim().length > 0) {
      this.selectedClientId.set(null);
    }
  }

  hasClientChosen(): boolean {
    return this.selectedClientId() !== null || this.newClientLabel().trim().length > 0;
  }

  uploadFile(file: File): void {
    this.selectedFile.set(file);
    this.categorizationResult.set(null);
    this.clientFeatures.set(null);
    this.lifestyleFeatures.set(null);
    this.decisionResult.set(null);
    this.affordabilityResult.set(null);
    this.savedStudy.set(null);
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
    this.lifestyleFeatures.set(null);
    this.decisionResult.set(null);
    this.affordabilityResult.set(null);
    this.savedStudy.set(null);
    this.selectedClientId.set(null);
    this.newClientLabel.set('');
    this.errorMessage.set(null);
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

  computeDecision(): void {
    const outputType = this.selectedOutput();
    const features = this.clientFeatures();
    const lifestyle = this.lifestyleFeatures();
    if (!outputType || !features || !lifestyle) return;

    this.isLoadingDecision.set(true);
    this.errorMessage.set(null);

    this.api.computeDecision(outputType, features, lifestyle).subscribe({
      next: (decision) => {
        this.decisionResult.set(decision);
        this.isLoadingDecision.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isLoadingDecision.set(false);
      },
    });
  }

  checkAffordability(loanAmount: number, durationMonths: number): void {
    const features = this.clientFeatures();
    if (!features) return;

    this.isCheckingAffordability.set(true);

    this.api.checkAffordability(features, loanAmount, durationMonths).subscribe({
      next: (result) => {
        this.affordabilityResult.set(result);
        this.isCheckingAffordability.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isCheckingAffordability.set(false);
      },
    });
  }

  /** Persists the completed study, at the moment the analyst confirms
   * a decision (FR-A16, FR-A17). Real backend save now — no longer
   * just kept in memory. */
  saveDecision(choice: DecisionChoice, comment: string): void {
    const outputType = this.selectedOutput();
    const enrichment = this.enrichmentResult();
    const categorization = this.categorizationResult();
    const features = this.clientFeatures();
    const lifestyle = this.lifestyleFeatures();
    const decision = this.decisionResult();

    if (!outputType || !enrichment || !categorization || !features || !lifestyle || !decision) {
      return;
    }
    if (!this.hasClientChosen()) {
      this.errorMessage.set(this.translation.t('decision.needClient'));
      return;
    }

    this.isSavingStudy.set(true);
    this.errorMessage.set(null);

    const payload: SaveStudyRequest = {
      client_id: this.selectedClientId(),
      new_client_label: this.selectedClientId() === null ? this.newClientLabel().trim() || null : null,
      output_type: outputType,
      enrichment_result: enrichment,
      categorization_result: categorization,
      client_features: features,
      lifestyle_features: lifestyle,
      decision_result: decision,
      decision_choice: choice,
      decision_comment: comment || null,
    };

    this.api.saveStudy(payload).subscribe({
      next: (saved) => {
        this.savedStudy.set(saved);
        this.isSavingStudy.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isSavingStudy.set(false);
      },
    });
  }
}