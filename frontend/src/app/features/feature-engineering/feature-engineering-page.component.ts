import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

@Component({
  selector: 'app-feature-engineering-page',
  standalone: true,
  imports: [CommonModule,TranslatePipe],
  templateUrl: './feature-engineering-page.component.html',
  styleUrl: './feature-engineering-page.component.css',
})
export class FeatureEngineeringPageComponent {
  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  onCompute(): void {
    this.session.computeFeatures();
  }

  goBack(): void {
    this.router.navigate(['/studies/new/categorization']);
  }

  goNext(): void {
    this.router.navigate(['/studies/new/lifestyle-intelligence']);
  }
}