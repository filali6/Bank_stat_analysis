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