import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

interface StudyRow {
  client: string;
  date: string;
  output: string;
  status: 'validated' | 'review' | 'pending';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent {
  readonly studies: StudyRow[] = [
    { client: 'Client #1042', date: '2026-07-28', output: 'Credit underwriting', status: 'validated' },
    { client: 'Client #1041', date: '2026-07-27', output: 'Risk management', status: 'review' },
    { client: 'Client #1039', date: '2026-07-25', output: 'Customer insight / KYC', status: 'pending' },
  ];

  constructor(private readonly router: Router, private readonly session: StudySessionService) {}

  get totalCount(): number {
    return this.studies.length;
  }
  get pendingCount(): number {
    return this.studies.filter((s) => s.status === 'pending' || s.status === 'review').length;
  }
  get validatedCount(): number {
    return this.studies.filter((s) => s.status === 'validated').length;
  }

  newStudy(): void {
    this.session.reset();
    this.router.navigate(['/studies/new']);
  }
}
