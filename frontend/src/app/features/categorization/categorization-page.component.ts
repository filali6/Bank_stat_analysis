import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { CategorizationTableComponent } from './categorization-table.component';

@Component({
  selector: 'app-categorization-page',
  standalone: true,
  imports: [CategorizationTableComponent, TranslatePipe],
  templateUrl: './categorization-page.component.html',
  styleUrl: './categorization-page.component.css',
})
export class CategorizationPageComponent {
  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  onCategorize(): void {
    this.session.categorize();
  }

  goBack(): void {
    this.router.navigate(['/studies/new/enrichment']);
  }

  goNext(): void {
    this.router.navigate(['/studies/new/feature-engineering']);
  }
}
