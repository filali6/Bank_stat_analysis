import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { StudySession } from '../../core/services/study-session';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { Step, StepperComponent } from '../../shared/stepper/stepper.component';
import { UploadZoneComponent } from '../upload/upload-zone.component';
import { EnrichmentTableComponent } from '../enrichment/enrichment-table.component';
import { CategorizationTableComponent } from '../categorization/categorization-table.component';

const ENGINE_STEP_LABELS = ['stepper.step1', 'stepper.step2', 'stepper.step3', 'stepper.step4'];
const ENGINE_STEP_TITLES = [
  { title: 'engineSteps.uploadTitle', subtitle: 'engineSteps.uploadSubtitle' },
  { title: 'engineSteps.categorizationTitle', subtitle: 'engineSteps.categorizationSubtitle' },
  { title: 'engineSteps.featureEngineeringTitle', subtitle: 'engineSteps.featureEngineeringSubtitle' },
  { title: 'engineSteps.lifestyleTitle', subtitle: 'engineSteps.lifestyleSubtitle' },
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