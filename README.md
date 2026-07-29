# Transaction Enrichment

Enrichissement automatique de transactions bancaires : reconnaissance du marchand,
catégorisation, canal de paiement, détection de récurrence, et score de confiance.

**Stack** : FastAPI (backend) + Angular (frontend, à venir) + Docker + GitHub Actions (CI).

---

## Démarrer en local (sans Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload    # API disponible sur http://localhost:8000
```

Documentation interactive de l'API (générée automatiquement) : http://localhost:8000/docs

## Démarrer avec Docker

```bash
docker compose up --build
```

## Lancer les tests

```bash
cd backend
pytest -v
```

---

## Architecture du backend

```
backend/app/
├── main.py                       # point d'entrée FastAPI, CORS, routes
├── api/
│   └── enrichment_routes.py      # endpoints REST (POST /enrichment/enrich)
├── schemas/
│   └── transaction.py            # contrat de données (Pydantic) — la "forme"
│                                  # de ce qui circule entre les couches et vers Angular
├── services/
│   ├── enrichment_service.py     # orchestrateur du pipeline complet
│   ├── business_rules.py         # règles métier basées sur le signe du montant
│   ├── recurrence_detector.py    # détection de récurrence via l'historique
│   └── matchers/
│       ├── base_matcher.py       # interface commune à tous les matchers
│       ├── exact_matcher.py      # niveau 1 : mot-clé exact
│       ├── fuzzy_matcher.py      # niveau 2 : similarité tolérante aux fautes
│       └── tfidf_matcher.py      # niveau 3 : similarité statistique (dernier recours)
├── repositories/
│   └── merchant_repository.py    # accès à la base de marchands (aujourd'hui : JSON)
├── core/
│   ├── config.py                 # tous les paramètres ajustables, au même endroit
│   └── dependencies.py           # LE SEUL endroit où les classes concrètes sont
│                                  # assemblées ensemble (composition root)
└── data/
    └── merchant_db.json          # base de référence des marchands connus
```

### Pourquoi c'est organisé comme ça

**Chain of Responsibility** (`services/matchers/`) : chaque matcher (exact, fuzzy,
tfidf) essaie une seule technique et renvoie `None` s'il n'est pas confiant. Le
`MerchantIdentifier` les fait tourner dans l'ordre et s'arrête au premier qui répond.
**Pour ajouter une 4e technique de matching (ex : un modèle ML), il suffit d'écrire
une nouvelle classe qui hérite de `Matcher` et de l'ajouter dans la liste de
`core/dependencies.py`. Aucun fichier existant n'a besoin d'être modifié.**

**Repository** (`repositories/merchant_repository.py`) : le reste du code ne sait pas
que les marchands viennent d'un fichier JSON. Si demain cette donnée doit venir
d'une vraie base de données, seul ce fichier change.

**Composition root** (`core/dependencies.py`) : c'est le seul fichier qui connaît les
classes concrètes (`ExactMatcher`, `FuzzyMatcher`...). Partout ailleurs dans le code,
on manipule des interfaces (`Matcher`) ou des services, jamais des implémentations
précises. C'est ce qui permet à plusieurs personnes de modifier des matchers
différents sans se marcher dessus, et de tester chaque brique isolément.

### Le pipeline, étape par étape (`enrichment_service.py`)

1. Normaliser le texte brut (`utils/text_normalization.py`)
2. Identifier le marchand via la chaîne de matchers
3. Appliquer les règles métier (le signe du montant peut corriger/compléter le résultat)
4. Détecter la récurrence via l'historique du client (fenêtre de 90 jours)
5. Calculer le score de confiance final et le statut (`validated` / `review` / `unknown`)

## API

### `POST /enrichment/enrich`

Envoie un fichier CSV (`multipart/form-data`, champ `file`), reçoit les transactions enrichies.

Colonnes attendues dans le CSV (insensible à la casse, quelques alias tolérés) :
`date`, `libelle_brut` (ou `description`), `montant` (ou `amount`), `mcc_code` (optionnel).

Réponse :

```json
{
  "total": 6,
  "validated": 1,
  "review": 4,
  "unknown": 1,
  "average_confidence": 63.0,
  "transactions": [
    {
      "transaction_id": "TXN000000",
      "date": "2025-11-02",
      "libelle_brut": "AMZN*XAJI0Y 81482 USA",
      "montant": -64.21,
      "merchant": "Amazon",
      "category": "Shopping",
      "subcategory": "E-commerce",
      "payment_channel": "Card Online",
      "transaction_type": "Purchase",
      "recurring": false,
      "income_flag": false,
      "normalized_description": "Amazon E-commerce",
      "confidence": 68,
      "status": "review",
      "matched_by": "exact"
    }
  ]
}
```

## CI

À chaque push/PR sur `main`, GitHub Actions (`.github/workflows/ci.yml`) installe les
dépendances et lance `pytest`. Si un test casse, la PR est bloquée visuellement sur GitHub.

## Prochaines étapes

- [ ] Frontend Angular : upload de fichier + tableau de résultats (consomme `/enrichment/enrich`)
- [ ] `frontend/Dockerfile` + décommenter le service `frontend` dans `docker-compose.yml`
- [ ] Étape "Transaction Categorization" (catégorie fine, business purpose, lifestyle tag — cf. schéma projet) comme service backend additionnel, branché après l'enrichment
- [ ] Authentification / autorisations (volontairement absent pour l'instant)

## Conventions pour contribuer

- Un nouveau matcher = une nouvelle classe dans `services/matchers/`, héritant de `Matcher`,
  ajoutée dans `core/dependencies.py`. Ne pas modifier les matchers existants pour ça.
- Toute nouvelle règle métier va dans `business_rules.py`, jamais dans `enrichment_service.py`.
- Un test par comportement, pas par fonction — voir `tests/` pour le style attendu.
