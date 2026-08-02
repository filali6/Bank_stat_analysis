import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CategorizationResponse, EnrichmentResponse } from '../models/enriched-transaction.model';

@Injectable({ providedIn: 'root' })
export class EnrichmentApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  enrich(file: File): Observable<EnrichmentResponse> {
    return this.http.post<EnrichmentResponse>(`${this.baseUrl}/enrichment/enrich`, this.toFormData(file));
  }

  categorize(file: File): Observable<CategorizationResponse> {
    return this.http.post<CategorizationResponse>(`${this.baseUrl}/categorization/categorize`, this.toFormData(file));
  }

  private toFormData(file: File): FormData {
    const formData = new FormData();
    formData.append('file', file);
    return formData;
  }
}