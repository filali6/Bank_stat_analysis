import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

@Component({
  selector: 'app-lifestyle-intelligence-page',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './lifestyle-intelligence-page.component.html',
  styleUrl: './lifestyle-intelligence-page.component.css',
})
export class LifestyleIntelligencePageComponent {
  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  onCompute(): void {
    this.session.computeLifestyle();
  }

  goBack(): void {
    this.router.navigate(['/studies/new/feature-engineering']);
  }

  goNext(): void {
    this.router.navigate(['/studies/new/decision']);
  }
}