import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { StudySessionService } from '../../core/services/study-session.service';
import { TranslatePipe } from '../../core/pipes/translate.pipe';
import { EnrichmentTableComponent } from './enrichment-table.component';
import { UploadZoneComponent } from '../upload/upload-zone.component';

@Component({
  selector: 'app-enrichment-page',
  standalone: true,
  imports: [UploadZoneComponent, EnrichmentTableComponent, TranslatePipe],
  templateUrl: './enrichment-page.component.html',
  styleUrl: './enrichment-page.component.css',
})
export class EnrichmentPageComponent {
  constructor(readonly session: StudySessionService, private readonly router: Router) {}

  onFileSelected(file: File): void {
    this.session.uploadFile(file);
  }

  goNext(): void {
    this.router.navigate(['/studies/new/categorization']);
  }
}
