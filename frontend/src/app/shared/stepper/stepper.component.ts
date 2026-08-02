import { Component, Input } from '@angular/core';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

export interface Step {
  label: string;
}

@Component({
  selector: 'app-stepper',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './stepper.component.html',
  styleUrl: './stepper.component.css',
})
export class StepperComponent {
  @Input() steps: Step[] = [];
  /** 1-based: which step is currently active. */
  @Input() currentStep = 1;

  isCompleted(stepIndex: number): boolean {
    return stepIndex + 1 < this.currentStep;
  }

  isActive(stepIndex: number): boolean {
    return stepIndex + 1 === this.currentStep;
  }
}