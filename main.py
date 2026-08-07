from collectors.supplier_collector import load_suppliers
from collectors.logistics_collector import load_logistics

from cleaners.data_cleaner import clean_data

from transformers.transformer import (
    transform_suppliers,
    transform_logistics
)

from validators.data_validator import (
    validate_suppliers,
    validate_logistics
)

from feature_engineering.feature_engineering import (
    engineer_supplier_features,
    engineer_logistics_features
)

from risk_engine.risk_scorer import (
    classify_supplier_risk,
    classify_logistics_risk
)


def main():

    print("=" * 60)
    print("        AEGISFLOW - DATA PIPELINE")
    print("=" * 60)

    # =====================================================
    # STEP 1 : LOAD DATA
    # =====================================================
    suppliers = load_suppliers()
    logistics = load_logistics()

    if suppliers is None or logistics is None:
        print("\n❌ Failed to load data.")
        return

    # =====================================================
    # STEP 2 : CLEAN DATA
    # =====================================================
    suppliers = clean_data(suppliers)
    logistics = clean_data(logistics)

    # =====================================================
    # STEP 3 : TRANSFORM DATA
    # =====================================================
    suppliers = transform_suppliers(suppliers)
    logistics = transform_logistics(logistics)

    # =====================================================
    # STEP 4 : VALIDATE DATA
    # =====================================================
    supplier_errors = validate_suppliers(suppliers)
    logistics_errors = validate_logistics(logistics)

    print("\n========== VALIDATION RESULTS ==========\n")

    if not supplier_errors:
        print("✅ Supplier data is valid.")
    else:
        print("❌ Supplier Validation Errors:")
        for error in supplier_errors:
            print("   -", error)

    if not logistics_errors:
        print("✅ Logistics data is valid.")
    else:
        print("❌ Logistics Validation Errors:")
        for error in logistics_errors:
            print("   -", error)

    # =====================================================
    # STEP 5 : FEATURE ENGINEERING
    # =====================================================
    suppliers = engineer_supplier_features(suppliers)
    logistics = engineer_logistics_features(logistics)

    # =====================================================
    # STEP 6 : RISK SCORING
    # =====================================================
    suppliers = classify_supplier_risk(suppliers)
    logistics = classify_logistics_risk(logistics)

    # =====================================================
    # FINAL OUTPUT
    # =====================================================
    print("\n========== SUPPLIER ANALYSIS ==========\n")
    print(suppliers)

    print("\n========== LOGISTICS ANALYSIS ==========\n")
    print(logistics)

    print("\n✅ Pipeline completed successfully.")


if __name__ == "__main__":
    main()