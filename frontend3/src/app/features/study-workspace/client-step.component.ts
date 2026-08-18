import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { StudySession } from '../../core/services/study-session';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

@Component({
  selector: 'app-client-step',
  standalone: true,
  imports: [FormsModule, TranslatePipe],
  templateUrl: './client-step.component.html',
  styleUrl: './client-step.component.css',
})
export class ClientStepComponent {
  @Input({ required: true }) session!: StudySession;

  onExistingClientChange(value: string): void {
    this.session.selectExistingClient(value ? Number(value) : null);
  }

  onNewClientLabelChange(value: string): void {
    this.session.setNewClientLabel(value);
  }
}