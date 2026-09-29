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

import pandas as pd
import streamlit as st

from app.api_client import (
    get_feature_importance_api,
    get_model_evaluation_api,
    get_models_list_api,
    train_models_api,
)
from app.components.charts import (
    confusion_matrix_heatmap,
    feature_importance_bar,
    model_comparison_bar,
    training_time_bar,
)
from app.components.styles import header_html, metric_card_html
from app.components.theme import DENSITY, INK, LIME_DARK, MUTED

# Fallbacks so the page still renders if the backend is unreachable.
FALLBACK_FEATURE_COLUMNS = [
    "people_count",
    "occupancy_ratio",
    "avg_person_area",
    "avg_distance",
    "min_distance",
    "spatial_spread",
    "top_region_count",
    "middle_region_count",
    "bottom_region_count",
    "frame_occupancy_density",
]
FALLBACK_LABEL_CLASSES = ["LOW", "MEDIUM", "HIGH"]


def _local_results_fallback():
    """Best-effort local read of saved evaluation results (dev/offline only).

    Returns (results_dict, models_dir) or (None, None). Never raises: the
    backend package is absent inside the frontend container.
    """
    try:
        import joblib  # noqa: PLC0415

        from machine_learning.preprocessing import MODELS_DIR  # noqa: PLC0415

        results_path = os.path.join(MODELS_DIR, "evaluation_results.joblib")
        if not os.path.exists(results_path):
            return None, MODELS_DIR
        return joblib.load(results_path), MODELS_DIR
    except Exception:
        return None, None


def render_ml_models():
    """Render the ML Models evaluation and training page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("Statistical machine learning models", icon=":material/psychology:")
    st.markdown(
        "Train, benchmark, and compare 7 classical ML classification algorithms "
        "on the extracted spatial crowd features."
    )

    # ── Backend registry state ───────────────────────────────────────
    registry = get_models_list_api() or {}
    backend_online = bool(registry)
    feature_columns = registry.get("feature_columns") or FALLBACK_FEATURE_COLUMNS
    label_classes = registry.get("class_labels") or FALLBACK_LABEL_CLASSES
    has_trained_models = bool(registry.get("has_trained_models", False))

    if not backend_online:
        st.warning(
            "Backend API is offline — showing locally stored results where available. "
            "Start the FastAPI service to train or refresh models.",
            icon=":material/cloud_off:",
        )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        train_clicked = st.button(
            "Train All 7 Models",
            icon=":material/model_training:",
            type="primary",
            disabled=not backend_online,
            help="Runs the full 70/15/15 stratified training pipeline in the backend.",
        )
        if not backend_online:
            st.caption("Requires the FastAPI backend.")

    # ── Training / results acquisition (API-first) ───────────────────
    results = None

    if train_clicked:
        with st.spinner("Training all 7 models and evaluating performance..."):
            trained_payload = train_models_api()
        if trained_payload:
            results = trained_payload
            st.session_state["ml_results"] = trained_payload
            best_name = trained_payload.get("best_model_name", "n/a")
            best_f1 = trained_payload["val_metrics"].get(best_name, {}).get("f1_weighted", 0.0)
            st.success(f"Training complete! Best Model: **{best_name}** (F1: {best_f1:.4f})")
            has_trained_models = True
        else:
            st.error("Training failed — the backend API did not respond.", icon=":material/error:")
            return

    if results is None:
        results = st.session_state.get("ml_results")

    if results is None:
        results = get_model_evaluation_api()

    if results is None:
        local_results, _local_models_dir = _local_results_fallback()
        results = local_results

    if results is None:
        if not has_trained_models:
            st.info(
                "No saved models found. Click **'Train All 7 Models'** above to train "
                "on the crowd dataset."
            )
            return
        st.info("Evaluation metrics are unavailable. Retrain the models to regenerate them.")
        return

    val_metrics = results.get("val_metrics", {})
    test_metrics = results.get("test_metrics", {})
    best_model_name = results.get("best_model_name", "n/a")
    training_times = results.get("training_times", {})

    if not val_metrics:
        st.info("Evaluation metrics are empty. Retrain the models to regenerate them.")
        return

    # ── Champion summary ─────────────────────────────────────────────
    st.markdown("---")
    best_metrics = val_metrics.get(best_model_name, {})
    best_f1 = float(best_metrics.get("f1_weighted", 0.0))
    best_acc = float(best_metrics.get("accuracy", 0.0))

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.markdown(metric_card_html("Best Model", best_model_name, DENSITY["LOW"]), unsafe_allow_html=True)
    with col_b2:
        st.markdown(metric_card_html("F1-Score (Weighted)", f"{best_f1:.4f}", INK), unsafe_allow_html=True)
    with col_b3:
        st.markdown(metric_card_html("Accuracy", f"{best_acc * 100:.2f}%", MUTED), unsafe_allow_html=True)

    st.markdown("---")

    # ── Model comparison table & chart ───────────────────────────────
    st.subheader("Model comparison (validation set)", icon=":material/leaderboard:")
    comp_rows = []
    for name, m in val_metrics.items():
        comp_rows.append({
            "Model": name,
            "Accuracy": float(m.get("accuracy", 0.0)),
            "Precision": float(m.get("precision_weighted", 0.0)),
            "Recall": float(m.get("recall_weighted", 0.0)),
            "F1-Score": float(m.get("f1_weighted", 0.0)),
        })

    if comp_rows:
        comp_df = pd.DataFrame(comp_rows).sort_values("F1-Score", ascending=False).reset_index(drop=True)
        st.dataframe(
            comp_df.style.highlight_max(
                subset=["Accuracy", "Precision", "Recall", "F1-Score"], color=LIME_DARK
            ),
            width="stretch",
            height=260,
        )
        fig_comp = model_comparison_bar(comp_df)
        st.plotly_chart(fig_comp, width="stretch")
    else:
        st.info("No model comparison data available.")



    # ── Confusion Matrices & Test Results ────────────────────────────
    st.subheader("Detailed Model Evaluation", icon=":material/grid_on:")
    
    eval_tabs = st.tabs(["Validation Set", "Test Set (Unseen Data)"])
    
    with eval_tabs[0]:
        model_names = list(val_metrics.keys())
        val_sub_tabs = st.tabs(model_names)
        
        for idx, name in enumerate(model_names):
            with val_sub_tabs[idx]:
                col_cm, col_rep = st.columns([1, 1])
                with col_cm:
                    cm = val_metrics[name]["confusion_matrix"]
                    fig_cm = confusion_matrix_heatmap(cm, label_classes, title=f"Val CM: {name}")
                    st.plotly_chart(fig_cm, width="stretch")
                with col_rep:
                    st.markdown("##### Validation Classification Report")
                    st.code(val_metrics[name]["classification_report"], language="text")

    with eval_tabs[1]:
        if "test_metrics" in locals() and test_metrics:
            test_sub_tabs = st.tabs(model_names)
            for idx, name in enumerate(model_names):
                with test_sub_tabs[idx]:
                    col_cm, col_rep = st.columns([1, 1])
                    with col_cm:
                        cm = test_metrics[name]["confusion_matrix"]
                        fig_cm = confusion_matrix_heatmap(cm, label_classes, title=f"Test CM: {name}")
                        st.plotly_chart(fig_cm, width="stretch")
                    with col_rep:
                        st.markdown("##### Test Classification Report")
                        st.code(test_metrics[name]["classification_report"], language="text")
        else:
            st.info("Test set metrics not available. Please retrain models to generate them.")

    st.markdown("---")

    # ── Feature Importance & Training Time ───────────────────────────
    col_feat, col_time = st.columns(2)

    with col_feat:
        st.subheader("Feature Importance", icon=":material/bar_chart:")
        fi_payload = get_feature_importance_api()
        if fi_payload and fi_payload.get("importances"):
            fig_fi = feature_importance_bar(
                fi_payload.get("feature_names") or feature_columns,
                fi_payload["importances"],
            )
            st.plotly_chart(fig_fi, width="stretch")
            st.caption(f"Source model: **{fi_payload.get('model_name', 'n/a')}**")
        else:
            st.info("Feature importance is not available for the trained model types.")

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
