import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CategorizationResponse, EnrichmentResponse, ClientFeatures, CategorizedTransaction, LifestyleFeatures, DecisionResult, AffordabilityResult, Client, SaveStudyRequest, StudyOut, StudySummary } from '../models/enriched-transaction.model';

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
  computeFeatures(transactions: CategorizedTransaction[]): Observable<ClientFeatures> {
    return this.http.post<ClientFeatures>(`${this.baseUrl}/feature-engineering/compute`, { transactions });
  }

  computeLifestyle(features: ClientFeatures): Observable<LifestyleFeatures> {
    return this.http.post<LifestyleFeatures>(`${this.baseUrl}/lifestyle-intelligence/compute`, { features });
  }

  computeDecision(outputType: string, features: ClientFeatures, lifestyle: LifestyleFeatures): Observable<DecisionResult> {
    return this.http.post<DecisionResult>(`${this.baseUrl}/decision/compute`, {
      output_type: outputType,
      features,
      lifestyle,
    });
  }

  checkAffordability(features: ClientFeatures, loanAmount: number, durationMonths: number): Observable<AffordabilityResult> {
    return this.http.post<AffordabilityResult>(`${this.baseUrl}/decision/check-affordability`, {
      features,
      loan_amount: loanAmount,
      duration_months: durationMonths,
    });
  }

  getClients(): Observable<Client[]> {
    return this.http.get<Client[]>(`${this.baseUrl}/clients`);
  }

  saveStudy(payload: SaveStudyRequest): Observable<StudyOut> {
    return this.http.post<StudyOut>(`${this.baseUrl}/studies`, payload);
  }

  listStudies(): Observable<StudySummary[]> {
    return this.http.get<StudySummary[]>(`${this.baseUrl}/studies`);
  }
}