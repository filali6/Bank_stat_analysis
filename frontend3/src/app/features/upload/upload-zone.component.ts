import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TranslatePipe } from '../../core/pipes/translate.pipe';

@Component({
  selector: 'app-upload-zone',
  standalone: true,
  imports: [CommonModule,TranslatePipe],
  templateUrl: './upload-zone.component.html',
  styleUrl: './upload-zone.component.css',
})
export class UploadZoneComponent {
  /** Whether a request is currently in flight — disables the button and shows a spinner state. */
  @Input() isLoading = false;
  /** Surface any error from the parent (network failure, backend rejection, etc.). */
  @Input() errorMessage: string | null = null;

  @Output() fileSelected = new EventEmitter<File>();

  isDragOver = false;

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(): void {
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      this.fileSelected.emit(file);
    }
  }

  onFileInputChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.fileSelected.emit(file);
    }
    input.value = ''; // allows re-selecting the same file twice in a row
  }
}
