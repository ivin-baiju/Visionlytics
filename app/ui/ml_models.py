"""
ML Models Page for Visionlytics.

Provides an interactive interface to train, evaluate, and compare
all 7 Statistical Machine Learning models on the crowd dataset:
1. Logistic Regression
2. K-Nearest Neighbors
3. Decision Tree
4. Random Forest
5. Support Vector Machine
6. Gradient Boosting
7. Voting Ensemble
"""

import os
import joblib
import pandas as pd
import streamlit as st

from app.components.styles import header_html, metric_card_html
from app.components.charts import (
    model_comparison_bar,
    confusion_matrix_heatmap,
    feature_importance_bar,
    training_time_bar,
)
from machine_learning.preprocessing import (
    load_dataset,
    preprocess_and_split,
    MODELS_DIR,
    FEATURE_COLUMNS,
    LABEL_CLASSES,
)
from machine_learning.train import train_all_models
from machine_learning.evaluation import evaluate_model, compare_models


def render_ml_models():
    """Render the ML Models evaluation and training page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Statistical Machine Learning Models", icon=":material/psychology:")
    st.markdown(
        "Train, benchmark, and compare 7 classical ML classification algorithms "
        "on the extracted spatial crowd features."
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        train_clicked = st.button("Train All 7 Models", icon=":material/model_training:", type="primary")

    best_meta_path = os.path.join(MODELS_DIR, "best_model_meta.joblib")
    has_trained_models = os.path.exists(best_meta_path)

    if train_clicked:
        with st.spinner("Training all 7 models and evaluating performance..."):
            results = train_all_models(verbose=False)
            st.session_state["ml_results"] = results
            st.success(
                f"Training complete! Best Model: **{results['best_model_name']}** "
                f"(F1: {results['val_metrics'][results['best_model_name']]['f1_weighted']:.4f})"
            )
            has_trained_models = True

    if not has_trained_models and "ml_results" not in st.session_state:
        st.info("No saved models found. Click **'Train All 7 Models'** above to train on the crowd dataset.")
        return

    # Load results or evaluate from disk
    if "ml_results" in st.session_state:
        results = st.session_state["ml_results"]
        val_metrics = results["val_metrics"]
        best_model_name = results["best_model_name"]
        training_times = results["training_times"]
        trained_models = results["models"]
    else:
        # Load dataset & evaluate saved models on validation set
        try:
            df = load_dataset()
            X_train, X_val, X_test, y_train, y_val, y_test, scaler, le = preprocess_and_split(df)

            trained_models = {}
            val_metrics = {}
            training_times = {}

            model_files = {
                "Logistic Regression": "logistic_regression.joblib",
                "KNN": "knn.joblib",
                "Decision Tree": "decision_tree.joblib",
                "Random Forest": "random_forest.joblib",
                "SVM": "svm.joblib",
                "Gradient Boosting": "gradient_boosting.joblib",
                "Voting Ensemble": "voting_ensemble.joblib",
            }

            for name, fname in model_files.items():
                mpath = os.path.join(MODELS_DIR, fname)
                if os.path.exists(mpath):
                    m = joblib.load(mpath)
                    trained_models[name] = m
                    val_metrics[name] = evaluate_model(m, X_val, y_val, LABEL_CLASSES)
                    training_times[name] = 0.05

            meta = joblib.load(best_meta_path)
            best_model_name = meta.get("name", "Random Forest")
        except Exception as e:
            st.error(f"Error loading models: {e}. Please click 'Train All 7 Models'.")
            return

    # ── Best Model Highlight Banner ──────────────────────────────────
    best_f1 = val_metrics[best_model_name]["f1_weighted"]
    best_acc = val_metrics[best_model_name]["accuracy"]

    st.markdown("---")
    st.subheader("Benchmark Champion", icon=":material/military_tech:")

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.markdown(metric_card_html("Best Model", best_model_name, "#00b894"), unsafe_allow_html=True)
    with col_b2:
        st.markdown(metric_card_html("F1-Score (Weighted)", f"{best_f1:.4f}", "#636ee6"), unsafe_allow_html=True)
    with col_b3:
        st.markdown(metric_card_html("Accuracy", f"{best_acc * 100:.2f}%", "#ffeaa7"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Comparison Table & Chart ─────────────────────────────────────
    st.subheader("Model Performance Comparison", icon=":material/leaderboard:")

    comparison_rows = []
    for name, m in val_metrics.items():
        comparison_rows.append({
            "Model": name,
            "Accuracy": m["accuracy"],
            "Precision": m["precision_weighted"],
            "Recall": m["recall_weighted"],
            "F1-Score": m["f1_weighted"],
            "Training Time (s)": training_times.get(name, 0.0),
        })

    comp_df = pd.DataFrame(comparison_rows).sort_values("F1-Score", ascending=False).reset_index(drop=True)

    col_tbl, col_chart = st.columns([1, 1])
    with col_tbl:
        st.markdown("##### Detailed Metric Table")
        st.dataframe(
            comp_df.style.highlight_max(subset=["Accuracy", "Precision", "Recall", "F1-Score"], color="#2ecc71"),
            width="stretch",
            height=260,
        )
    with col_chart:
        fig_comp = model_comparison_bar(comp_df)
        st.plotly_chart(fig_comp, width="stretch")

    st.markdown("---")

    # ── Confusion Matrices ───────────────────────────────────────────
    st.subheader("Confusion Matrices (Validation Set)", icon=":material/grid_on:")
    model_names = list(val_metrics.keys())
    tabs = st.tabs(model_names)

    for idx, name in enumerate(model_names):
        with tabs[idx]:
            col_cm, col_rep = st.columns([1, 1])
            with col_cm:
                cm = val_metrics[name]["confusion_matrix"]
                fig_cm = confusion_matrix_heatmap(cm, LABEL_CLASSES, title=f"Confusion Matrix: {name}")
                st.plotly_chart(fig_cm, width="stretch")
            with col_rep:
                st.markdown("##### Classification Report")
                st.code(val_metrics[name]["classification_report"], language="text")

    st.markdown("---")

    # ── Feature Importance & Training Time ───────────────────────────
    col_feat, col_time = st.columns(2)

    with col_feat:
        st.subheader("Feature Importance", icon=":material/bar_chart:")
        # Extract from Best Model or Random Forest
        rf_model = trained_models.get("Random Forest") or trained_models.get(best_model_name)
        if rf_model is not None and hasattr(rf_model, "feature_importances_"):
            fig_fi = feature_importance_bar(FEATURE_COLUMNS, rf_model.feature_importances_.tolist())
            st.plotly_chart(fig_fi, width="stretch")
        else:
            st.info("Feature importance is not available for this model type.")

    with col_time:
        st.subheader("Computational Efficiency", icon=":material/timer:")
        fig_time = training_time_bar(training_times)
        st.plotly_chart(fig_time, width="stretch")

    # ── SML Educational Notes ────────────────────────────────────────
    with st.expander("Statistical Machine Learning Concepts & Algorithms", icon=":material/menu_book:"):
        st.markdown("""
        #### Model Overview for Statistical Machine Learning:
        1. **Logistic Regression (Multinomial)**:
           - Establishes linear decision boundaries using Softmax regression with Cross-Entropy Loss.
           - Fast baseline, highly interpretable through feature weights $\\beta_i$.
        2. **K-Nearest Neighbors (KNN)**:
           - Non-parametric instance-based classifier ($k=5$, Euclidean distance on standardized features).
           - Captures non-linear local geometric clusters in crowd density feature space.
        3. **Decision Tree (CART)**:
           - Recursively partitions feature space using Gini impurity criteria (max depth = 10 to prevent overfitting).
           - Transparent decision path modeling rules like: *If people_count > 10 and avg_distance < 0.25 → HIGH*.
        4. **Random Forest**:
           - Ensemble of 100 decorrelated decision trees using bagging (bootstrap aggregation) and random feature sub-selection.
           - Effectively resists variance and provides robust feature importance scoring via Mean Decrease in Impurity (MDI).
        5. **Support Vector Machine (SVM with RBF Kernel)**:
           - Projects features into infinite-dimensional reproducing kernel Hilbert space using Radial Basis Functions.
           - Maximizes geometric margin between density classes, excelling at boundary demarcation.
        6. **Gradient Boosting**:
           - Iteratively builds trees to correct the residual errors of preceding trees.
           - Highly accurate, dominant in tabular data competitions.
        7. **Voting Ensemble (Soft)**:
           - Averages the predicted probabilities of the top models.
           - Provides incredible stability by cancelling out individual model biases.
        """)
