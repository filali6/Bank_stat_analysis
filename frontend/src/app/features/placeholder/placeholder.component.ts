import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { TranslatePipe } from '../../core/pipes/translate.pipe';

@Component({
  selector: 'app-placeholder',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './placeholder.component.html',
  styleUrl: './placeholder.component.css',
})
export class PlaceholderComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly titleKey = this.route.snapshot.data['titleKey'] as string;
  readonly backRoute = this.route.snapshot.data['backRoute'] as string;
  readonly nextRoute = this.route.snapshot.data['nextRoute'] as string | null;

  goBack(): void {
    this.router.navigate([this.backRoute]);
  }

  goNext(): void {
    if (this.nextRoute) this.router.navigate([this.nextRoute]);
  }

  finish(): void {
    this.router.navigate(['/dashboard']);
  }
}
