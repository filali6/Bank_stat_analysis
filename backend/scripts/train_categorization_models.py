import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flaml import AutoML
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.repositories.business_lifestyle_repository import BusinessLifestyleRepository
from app.repositories.merchant_repository import MerchantRepository
from app.services.merchant_category_lookup import lookup_category_from_label
from app.utils.text_normalization import normalize_text

MIN_SAMPLES_PER_CLASS = 5
TIME_BUDGET_SECONDS = 60

# Séparateur utilisé pour fusionner category+subcategory en une seule
# cible — évite qu'un modèle devine "Food" pendant qu'un autre devine
# "Electronics" indépendamment, ce qui produisait des combinaisons
# impossibles (ex: "Food · Electronics").
COMBO_SEPARATOR = " · "


def build_training_dataframe(csv_path: Path, merchant_repository: MerchantRepository,
                              business_lifestyle_repository: BusinessLifestyleRepository) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["libelle_norm"] = df["libelle_brut"].apply(normalize_text)

    categories, subcategories = [], []
    for label in df["libelle_norm"]:
        found = lookup_category_from_label(merchant_repository, label)
        categories.append(found[0] if found else "Unknown")
        subcategories.append(found[1] if found else "Unknown")

    df["category"] = categories
    df["subcategory"] = subcategories
    df["business_purpose"], df["lifestyle_tag"] = zip(*df.apply(
        lambda row: business_lifestyle_repository.get_labels(row["category"], row["subcategory"]), axis=1
    ))

    # Nouvelle cible combinée : "Food · Coffee", "Housing · Rent"...
    # Un seul modèle choisit parmi des combinaisons qui ont VRAIMENT
    # existé dans les données — il ne peut plus inventer un mélange
    # incohérent qui n'a jamais été observé.
    df["category_subcategory"] = df["category"] + COMBO_SEPARATOR + df["subcategory"]

    return df[df["category"] != "Unknown"].copy()


def build_feature_matrix(df: pd.DataFrame, vectorizer: TfidfVectorizer, feature_columns=None):
    text_features = vectorizer.transform(df["libelle_norm"]) if feature_columns is not None \
        else vectorizer.fit_transform(df["libelle_norm"])

    extra = pd.get_dummies(df[["payment_channel", "transaction_type"]])
    extra["montant_abs"] = df["montant"].abs()
    extra["recurring_flag"] = df["recurring"].astype(int)

    if feature_columns is None:
        feature_columns = list(extra.columns)
    extra = extra.reindex(columns=feature_columns, fill_value=0).astype(float)

    matrix = hstack([text_features, extra.values]).tocsr()
    return matrix, feature_columns


def train_target(df: pd.DataFrame, feature_matrix, target_column: str) -> dict:
    counts = df[target_column].value_counts()
    valid_values = counts[counts >= MIN_SAMPLES_PER_CLASS].index
    mask = df[target_column].isin(valid_values)

    y = df.loc[mask, target_column]
    X = feature_matrix[mask.values]

    if y.nunique() < 2:
        constant_value = y.iloc[0]
        print(f"[{target_column}] Une seule valeur observée ({constant_value!r}) — règle constante utilisée.")
        return {"model": None, "label_encoder": None, "constant_value": constant_value}

    X_train, X_test, y_train_raw, y_test_raw = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)

    automl = AutoML()
    automl.fit(
        X_train=X_train, y_train=y_train,
        task="classification", time_budget=TIME_BUDGET_SECONDS,
        metric="accuracy", verbose=0,
    )
    accuracy = automl.score(X_test, y_test)
    print(f"[{target_column}] Meilleur : {automl.best_estimator} → précision : {accuracy:.1%} (sur {len(y_test)} exemples, {y.nunique()} classes)")

    return {"model": automl, "label_encoder": label_encoder, "constant_value": None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Path to an ENRICHED transactions CSV")
    parser.add_argument("--output", type=Path, default=settings.category_model_bundle_path)
    args = parser.parse_args()

    merchant_repository = MerchantRepository(settings.merchant_db_path)
    business_lifestyle_repository = BusinessLifestyleRepository(settings.business_lifestyle_mapping_path)

    df = build_training_dataframe(args.input, merchant_repository, business_lifestyle_repository)
    print(f"Transactions utilisables pour l'entraînement : {len(df)}")

    vectorizer = TfidfVectorizer(max_features=200)
    feature_matrix, feature_columns = build_feature_matrix(df, vectorizer)

    targets = {}
    # "category_subcategory" remplace "category" + "subcategory" séparés.
    # "business_purpose" est maintenant entraîné, plus codé en dur.
    for target in ["category_subcategory", "business_purpose", "lifestyle_tag"]:
        targets[target] = train_target(df, feature_matrix, target)

    bundle = {
        "vectorizer": vectorizer,
        "feature_columns": feature_columns,
        "targets": targets,
        "combo_separator": COMBO_SEPARATOR,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, args.output)
    print(f"\nModèle sauvegardé : {args.output}")


if __name__ == "__main__":
    main()