import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { DecisionChoice, OutputKey, StudySession } from '../../core/services/study-session';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { EnrichmentTableComponent } from '../enrichment/enrichment-table.component';
import { CategorizationTableComponent } from '../categorization/categorization-table.component';

interface OutputOption {
  key: OutputKey;
  title: string;
  desc: string;
}

type DetailTab = 'enrichment' | 'categorization' | 'features' | 'lifestyle';

@Component({
  selector: 'app-decision-workspace',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe, EnrichmentTableComponent, CategorizationTableComponent],
  templateUrl: './decision-workspace.component.html',
  styleUrl: './decision-workspace.component.css',
})
export class DecisionWorkspaceComponent {
  @Input({ required: true }) session!: StudySession;

  readonly outputs: OutputOption[] = [
    { key: 'credit', title: 'Credit underwriting', desc: 'Score de crédit et capacité de remboursement.' },
    { key: 'risk', title: 'Risk management', desc: 'Détection des signaux de risque.' },
    { key: 'kyc', title: 'Customer insight / KYC', desc: 'Profil client et vérifications de cohérence.' },
    { key: 'opportunities', title: 'Identifying commercial opportunities', desc: 'Produits à proposer au client.' },
  ];

  loanAmount = 5000;
  durationMonths = 12;
  selectedChoice: DecisionChoice | null = null;
  showConfirmModal = false;
  showDetailModal = false;
  detailTab: DetailTab = 'enrichment';

  selectOutput(key: OutputKey): void {
    this.session.selectOutput(key);
  }

  onCommentChange(value: string): void {
    this.session.comment.set(value);
  }

  onCheckAffordability(): void {
    this.session.checkAffordability(this.loanAmount, this.durationMonths);
  }

  pickChoice(choice: DecisionChoice): void {
    this.selectedChoice = choice;
  }

  openConfirmModal(): void {
    if (this.selectedChoice) this.showConfirmModal = true;
  }

  cancelConfirm(): void {
    this.showConfirmModal = false;
  }

  confirmSave(): void {
    if (!this.selectedChoice) return;
    this.showConfirmModal = false;
    this.session.saveDecision(this.selectedChoice);
  }

  openDetailModal(): void {
    this.detailTab = 'enrichment';
    this.showDetailModal = true;
  }

  closeDetailModal(): void {
    this.showDetailModal = false;
  }

  setDetailTab(tab: DetailTab): void {
    this.detailTab = tab;
  }

  goBack(): void {
    this.session.engineStep.set(3);
    this.session.phase.set('engine');
  }
}