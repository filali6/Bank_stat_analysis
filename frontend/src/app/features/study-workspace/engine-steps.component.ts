import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { StudySession } from '../../core/services/study-session';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { Step, StepperComponent } from '../../shared/stepper/stepper.component';
import { UploadZoneComponent } from '../upload/upload-zone.component';
import { EnrichmentTableComponent } from '../enrichment/enrichment-table.component';
import { CategorizationTableComponent } from '../categorization/categorization-table.component';

const ENGINE_STEP_LABELS = ['Enrichment', 'Categorization', 'Feature engineering', 'Lifestyle intelligence'];
const ENGINE_STEP_TITLES = [
  { title: 'Importer le relevé', subtitle: "Dépose un export CSV des transactions du client." },
  { title: 'Catégorisation', subtitle: 'Chaque transaction a été classée automatiquement — vérifie et affine si besoin.' },
  { title: 'Feature engineering', subtitle: 'Les indicateurs financiers calculés à partir des transactions catégorisées.' },
  { title: 'Lifestyle intelligence', subtitle: 'Ce que le relevé révèle sur les habitudes financières du client.' },
];

@Component({
  selector: 'app-engine-steps',
  standalone: true,
  imports: [CommonModule, TranslatePipe, StepperComponent, UploadZoneComponent, EnrichmentTableComponent, CategorizationTableComponent],
  templateUrl: './engine-steps.component.html',
  styleUrl: './engine-steps.component.css',
})
export class EngineStepsComponent {
  @Input({ required: true }) session!: StudySession;

  get steps(): Step[] {
    // Only completed/current steps can be clicked back into — nothing
    // ahead of what's already been computed, since there's nothing to show there yet.
    return ENGINE_STEP_LABELS.map((label, i) => ({ label, enabled: i <= this.session.engineStep() }));
  }
  get currentStepInfo() {
    return ENGINE_STEP_TITLES[this.session.engineStep()];
  }

  onFileSelected(file: File): void {
    this.session.uploadFile(file);
  }

  onStepClick(stepNumber: number): void {
    // stepNumber is 1-based (StepperComponent convention)
    this.session.engineStep.set(stepNumber - 1);
  }

  onNext(): void {
    this.session.goToNextEngineStep();
    this.triggerCurrentStepCompute();
  }

  private triggerCurrentStepCompute(): void {
    switch (this.session.engineStep()) {
      case 1:
        this.session.categorize();
        break;
      case 2:
        this.session.computeFeatures();
        break;
      case 3:
        this.session.computeLifestyle();
        break;
    }
  }

  isStepLoading(): boolean {
    switch (this.session.engineStep()) {
      case 1:
        return this.session.isLoadingCategorization();
      case 2:
        return this.session.isLoadingFeatures();
      case 3:
        return this.session.isLoadingLifestyle();
      default:
        return false;
    }
  }
}