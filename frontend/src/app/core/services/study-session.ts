import { signal } from '@angular/core';

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
export type StudyPhase = 'client' | 'engine' | 'decision' | 'saved';

/**
 * One instance = one open study tab. Unlike the old singleton service,
 * this is a plain class: WorkspaceTabsService creates a new one every
 * time a tab is opened, so several studies can be worked on in
 * parallel without their state colliding.
 */
export class StudySession {
  readonly phase = signal<StudyPhase>('client');
  readonly engineStep = signal(0); // 0=Enrichment 1=Categorization 2=Feature engineering 3=Lifestyle

  readonly clients = signal<Client[]>([]);
  readonly isLoadingClients = signal(false);
  readonly selectedClientId = signal<number | null>(null);
  readonly newClientLabel = signal('');

  readonly selectedFile = signal<File | null>(null);
  readonly enrichmentResult = signal<EnrichmentResponse | null>(null);
  readonly categorizationResult = signal<CategorizationResponse | null>(null);
  readonly clientFeatures = signal<ClientFeatures | null>(null);
  readonly lifestyleFeatures = signal<LifestyleFeatures | null>(null);
  readonly isLoadingEnrichment = signal(false);
  readonly isLoadingCategorization = signal(false);
  readonly isLoadingFeatures = signal(false);
  readonly isLoadingLifestyle = signal(false);
  readonly errorMessage = signal<string | null>(null);

  readonly selectedOutput = signal<OutputKey | null>(null);
  readonly decisionResult = signal<DecisionResult | null>(null);
  readonly isLoadingDecision = signal(false);
  readonly affordabilityResult = signal<AffordabilityResult | null>(null);
  readonly isCheckingAffordability = signal(false);
  readonly comment = signal('');

  readonly savedStudy = signal<StudyOut | null>(null);
  readonly isSavingStudy = signal(false);
  readonly editing = signal(false);

  readonly tabTitle = signal('Nouvelle étude');

  constructor(private readonly api: EnrichmentApiService, private readonly translation: TranslationService) {}

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
      const client = this.clients().find((c) => c.id === id);
      if (client) this.tabTitle.set(client.label);
    }
  }

  setNewClientLabel(label: string): void {
    this.newClientLabel.set(label);
    if (label.trim().length > 0) {
      this.selectedClientId.set(null);
      this.tabTitle.set(label.trim());
    }
  }

  hasClientChosen(): boolean {
    return this.selectedClientId() !== null || this.newClientLabel().trim().length > 0;
  }

  continueToEngine(): void {
    if (!this.hasClientChosen()) return;
    this.phase.set('engine');
  }

  uploadFile(file: File): void {
    this.selectedFile.set(file);
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
    if (!file || this.categorizationResult() || this.isLoadingCategorization()) return;

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

  computeFeatures(): void {
    const categorized = this.categorizationResult();
    if (!categorized || this.clientFeatures() || this.isLoadingFeatures()) return;

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
    if (!features || this.lifestyleFeatures() || this.isLoadingLifestyle()) return;

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

  goToNextEngineStep(): void {
    if (this.engineStep() < 3) {
      this.engineStep.set(this.engineStep() + 1);
    } else {
      this.phase.set('decision');
    }
  }

  goBackToClientStep(): void {
    this.phase.set('client');
  }

  selectOutput(key: OutputKey): void {
    this.selectedOutput.set(key);
    this.decisionResult.set(null);
    this.computeDecision();
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

  saveDecision(choice: DecisionChoice): void {
    const outputType = this.selectedOutput();
    const enrichment = this.enrichmentResult();
    const categorization = this.categorizationResult();
    const features = this.clientFeatures();
    const lifestyle = this.lifestyleFeatures();
    const decision = this.decisionResult();

    if (!outputType || !enrichment || !categorization || !features || !lifestyle || !decision) return;

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
      decision_comment: this.comment() || null,
    };

    this.api.saveStudy(payload).subscribe({
      next: (saved) => {
        this.savedStudy.set(saved);
        this.tabTitle.set(`${saved.client_number} — ${saved.client_label}`);
        this.isSavingStudy.set(false);
        this.phase.set('saved');
      },
      error: (err) => {
        this.errorMessage.set(err?.error?.detail ?? this.translation.t('error.generic'));
        this.isSavingStudy.set(false);
      },
    });
  }
reopenForEditing(): void {
    this.savedStudy.set(null);
    this.phase.set('decision');
  }
  hydrateFromStudyOut(study: StudyOut): void {
    this.enrichmentResult.set(study.enrichment_result as EnrichmentResponse);
    this.categorizationResult.set(study.categorization_result as CategorizationResponse);
    this.clientFeatures.set(study.client_features);
    this.lifestyleFeatures.set(study.lifestyle_features);
    this.decisionResult.set(study.decision_result);
    this.selectedOutput.set(study.output_type as OutputKey);
    this.selectedClientId.set(study.client_id);
    this.comment.set(study.decision_comment ?? '');
    this.savedStudy.set(study);
    this.tabTitle.set(`${study.client_number} — ${study.client_label}`);
    this.phase.set('saved');
  }
}