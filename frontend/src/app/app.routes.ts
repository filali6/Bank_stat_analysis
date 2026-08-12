import { Routes } from '@angular/router';

import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ChooseOutputComponent } from './features/choose-output/choose-output.component';
import { StudyLayoutComponent } from './features/study-layout/study-layout.component';
import { EnrichmentPageComponent } from './features/enrichment/enrichment-page.component';
import { CategorizationPageComponent } from './features/categorization/categorization-page.component';
import { PlaceholderComponent } from './features/placeholder/placeholder.component';
import { FeatureEngineeringPageComponent } from './features/feature-engineering/feature-engineering-page.component';
import { LifestyleIntelligencePageComponent } from './features/lifestyle-intelligence/lifestyle-intelligence-page.component';
import { DecisionPageComponent } from './features/decision/decision-page.component';
export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'studies/new', pathMatch: 'full', component: ChooseOutputComponent },
  {
    path: 'studies/new',
    component: StudyLayoutComponent,
    children: [
      { path: 'enrichment', component: EnrichmentPageComponent },
      { path: 'categorization', component: CategorizationPageComponent },
      { path: 'feature-engineering', component: FeatureEngineeringPageComponent },
      { path: 'lifestyle-intelligence', component: LifestyleIntelligencePageComponent },
      { path: 'decision', component: DecisionPageComponent },
      
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];