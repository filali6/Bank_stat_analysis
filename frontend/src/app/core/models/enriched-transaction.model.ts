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
