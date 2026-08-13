export interface EnrichedTransaction {
  transaction_id: string;
  date: string;
  libelle_brut: string;
  montant: number;
  merchant: string;
  payment_channel: string;
  transaction_type: string;
  recurring: boolean;
  income_flag: boolean;
  normalized_description: string;
}

export interface CategorizedTransaction extends EnrichedTransaction {
  category: string;
  subcategory: string;
  business_purpose: string;
  lifestyle_tag: string;
  confidence: number;
}

export interface EnrichmentResponse {
  total: number;
  transactions: EnrichedTransaction[];
}

export interface CategorizationResponse {
  total: number;
  transactions: CategorizedTransaction[];
}
export interface ClientFeatures {
  monthly_income: number;
  savings_rate: number;
  travel_spend_ratio: number;
  grocery_spend_ratio: number;
  recurring_commitments: number;
  atm_withdrawal_ratio: number;
}
export interface LifestyleFeatures {
  lifestyle_segment: string;
  affluence_score: number;
  financial_discipline_score: number;
  travel_activity_index: string;
  family_responsibility_index: string;
  overall_lifestyle_index: number;
  reasons: string[];
}
export interface CreditDecisionDetails {
  credit_score: number;
  recommendation: string;
  repayment_capacity: number;
}

export interface RiskAlert {
  severity: 'low' | 'medium' | 'high';
  message: string;
}

export interface RiskDecisionDetails {
  risk_level: string;
  alerts: RiskAlert[];
}

export interface ConsistencyCheck {
  label: string;
  status: 'consistent' | 'needs_review';
}

export interface KycDecisionDetails {
  consistency_checks: ConsistencyCheck[];
  profile_summary: string;
}

export interface SuggestedProduct {
  name: string;
  reason: string;
}

export interface OpportunitiesDecisionDetails {
  suggested_products: SuggestedProduct[];
}

export interface DecisionResult {
  output_type: string;
  headline: string;
  credit?: CreditDecisionDetails;
  risk?: RiskDecisionDetails;
  kyc?: KycDecisionDetails;
  opportunities?: OpportunitiesDecisionDetails;
}

export interface AffordabilityResult {
  monthly_payment: number;
  disposable_income: number;
  max_affordable_payment: number;
  affordable: boolean;
}
export interface Client {
  id: number;
  label: string;
  created_at: string;
  monitoring_enabled: boolean;
}

export interface SaveStudyRequest {
  client_id?: number | null;
  new_client_label?: string | null;
  output_type: string;
  enrichment_result: unknown;
  categorization_result: unknown;
  client_features: ClientFeatures;
  lifestyle_features: LifestyleFeatures;
  decision_result: DecisionResult;
  decision_choice: string;
  decision_comment?: string | null;
}

export interface StudyOut {
  id: number;
  client_id: number;
  client_label: string;
  created_at: string;
  output_type: string;
  source: string;
  enrichment_result: unknown;
  categorization_result: unknown;
  client_features: ClientFeatures;
  lifestyle_features: LifestyleFeatures;
  decision_result: DecisionResult;
  decision_choice: string;
  decision_comment?: string | null;
}

export interface StudySummary {
  id: number;
  client_label: string;
  created_at: string;
  output_type: string;
  headline: string;
  decision_choice: string;
}