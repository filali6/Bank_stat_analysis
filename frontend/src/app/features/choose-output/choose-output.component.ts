import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { OutputKey, StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

interface OutputOption {
  key: OutputKey;
  title: string;
  desc: string;
}

@Component({
  selector: 'app-choose-output',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe],
  templateUrl: './choose-output.component.html',
  styleUrl: './choose-output.component.css',
})
export class ChooseOutputComponent implements OnInit {
  readonly outputs: OutputOption[] = [
    { key: 'credit', title: 'Credit underwriting', desc: '' },
    { key: 'risk', title: 'Risk management', desc: ' ' },
    { key: 'kyc', title: 'Customer insight / KYC', desc: ' ' },
    { key: 'opportunities', title: 'Identifying commercial opportunities', desc: '' },
  ];

  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  ngOnInit(): void {
    this.session.loadClients();
  }

  select(key: OutputKey): void {
    this.session.selectOutput(key);
  }

  onExistingClientChange(value: string): void {
    this.session.selectExistingClient(value ? Number(value) : null);
  }

  onNewClientLabelChange(value: string): void {
    this.session.setNewClientLabel(value);
  }

  continueToStudy(): void {
    this.router.navigate(['/studies/new/enrichment']);
  }
}