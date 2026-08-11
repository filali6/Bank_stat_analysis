import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface Step {
  label: string;
  enabled: boolean;
}

@Component({
  selector: 'app-stepper',
  standalone: true,
  templateUrl: './stepper.component.html',
  styleUrl: './stepper.component.css',
})
export class StepperComponent {
  @Input() steps: Step[] = [];
  @Input() currentStep = 1;
  @Input() orientation: 'horizontal' | 'vertical' = 'horizontal';

  @Output() stepClick = new EventEmitter<number>();

  isCompleted(stepIndex: number): boolean {
    return stepIndex + 1 < this.currentStep;
  }

  isActive(stepIndex: number): boolean {
    return stepIndex + 1 === this.currentStep;
  }

  onStepClick(stepIndex: number): void {
    if (this.steps[stepIndex]?.enabled) {
      this.stepClick.emit(stepIndex + 1);
    }
  }
}
