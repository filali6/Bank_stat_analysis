import { Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterOutlet } from '@angular/router';
import { filter, map } from 'rxjs/operators';

import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { TranslationService } from '../../core/services/translation.service';
import { Step, StepperComponent } from '../../shared/stepper/stepper.component';

const STEP_ROUTES = ['enrichment', 'categorization', 'feature-engineering', 'lifestyle-intelligence', 'decision'];

@Component({
  selector: 'app-study-layout',
  standalone: true,
  imports: [RouterLink, RouterOutlet, StepperComponent, TranslatePipe],
  templateUrl: './study-layout.component.html',
  styleUrl: './study-layout.component.css',
})
export class StudyLayoutComponent {
  private readonly router = inject(Router);
  readonly translation = inject(TranslationService);

  private readonly url = toSignal(
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      map((e) => e.urlAfterRedirects)
    ),
    { initialValue: this.router.url }
  );

  readonly steps = computed<Step[]>(() => [
    { label: this.translation.t('stepper.step1'), enabled: true },
    { label: this.translation.t('stepper.step2'), enabled: true },
    { label: this.translation.t('stepper.step3'), enabled: true },
    { label: this.translation.t('stepper.step4'), enabled: true },
    { label: this.translation.t('stepper.step5'), enabled: true },
  ]);

  readonly currentStep = computed(() => {
    const segment = this.url().split('/').pop() ?? '';
    const idx = STEP_ROUTES.indexOf(segment);
    return idx === -1 ? 1 : idx + 1;
  });

  onStepClick(n: number): void {
    this.router.navigate(['/studies/new', STEP_ROUTES[n - 1]]);
  }
}