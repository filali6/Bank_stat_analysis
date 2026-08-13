import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { DecisionChoice, StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

@Component({
  selector: 'app-decision-page',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe],
  templateUrl: './decision-page.component.html',
  styleUrl: './decision-page.component.css',
})
export class DecisionPageComponent {
  loanAmount = 5000;
  durationMonths = 12;
  selectedChoice: DecisionChoice | null = null;
  comment = '';

  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  onCompute(): void {
    this.session.computeDecision();
  }

  onCheckAffordability(): void {
    this.session.checkAffordability(this.loanAmount, this.durationMonths);
  }

  pickChoice(choice: DecisionChoice): void {
    this.selectedChoice = choice;
  }

  confirmDecision(): void {
    if (!this.selectedChoice) return;
    this.session.saveDecision(this.selectedChoice, this.comment);
  }

  goBack(): void {
    this.router.navigate(['/studies/new/lifestyle-intelligence']);
  }

  backToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }
}