import { Component } from '@angular/core';
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
  imports: [TranslatePipe],
  templateUrl: './choose-output.component.html',
  styleUrl: './choose-output.component.css',
})
export class ChooseOutputComponent {
  readonly outputs: OutputOption[] = [
    { key: 'credit', title: 'Credit underwriting', desc: '' },
    { key: 'risk', title: 'Risk management', desc: ' ' },
    { key: 'kyc', title: 'Customer insight / KYC', desc: ' ' },
    { key: 'opportunities', title: 'Identifying commercial opportunities', desc: '' },
  ];

  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  select(key: OutputKey): void {
    this.session.selectOutput(key);
  }

  continueToStudy(): void {
    this.router.navigate(['/studies/new/enrichment']);
  }
}
