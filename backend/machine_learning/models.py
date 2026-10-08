"""
ML Models Module for Visionlytics.

Defines and configures the statistical machine learning models used for
crowd density classification. Each model is a classical ML algorithm
from scikit-learn (plus XGBoost).

Models:
    1. Logistic Regression — Linear classifier using logistic function
    2. K-Nearest Neighbors (KNN) — Instance-based learning, classifies
       based on k closest training examples
    3. Decision Tree — Tree-based classifier using information gain
    4. Random Forest — Ensemble of decision trees with bagging
    5. Support Vector Machine (SVM) — Finds optimal hyperplane separation
    6. Gradient Boosting — Sequential ensemble correcting prior errors
    7. XGBoost — Optimized distributed gradient boosting (faster, more accurate)
    8. Voting Ensemble — Combines RF, XGBoost, and SVM via soft voting

ML Concepts Demonstrated:
    - Linear vs non-linear classifiers
    - Parametric vs non-parametric models
    - Ensemble methods (bagging, boosting, voting)
    - Kernel methods
    - Overfitting control via hyperparameters
"""

from typing import Any

from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# XGBoost is optional — fall back to a second GradientBoosting if unavailable
try:
    from xgboost import XGBClassifier
    _HAS_XGBOOST = True
except ImportError:
    _HAS_XGBOOST = False


def get_models() -> dict[str, Any]:
    """
    Create and return all ML models with their configurations.

    Each model is configured with tuned hyperparameters for a
    crowd density classification task with 10 features and 3 classes.

    Returns:
        Dictionary mapping model names to model instances.
    """
    models = {
        # ── 1. Logistic Regression ───────────────────────────────────
        # How it works:
        #   Uses the logistic (sigmoid) function to model the probability
        #   of each class. For multi-class, it uses one-vs-rest strategy.
        # Why max_iter=1000:
        #   Ensures convergence for scaled features.
        # Why C=1.0:
        #   Default regularization strength. C controls the trade-off
        #   between fitting the training data and keeping the model simple
        #   (preventing overfitting).
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            C=1.0,
            random_state=42,
        ),

        # ── 2. K-Nearest Neighbors ──────────────────────────────────
        # How it works:
        #   For a new data point, finds the k closest training examples
        #   (neighbors) and assigns the most common class among them.
        # Why k=5:
        #   Odd number avoids ties; 5 balances noise sensitivity vs
        #   underfitting. Feature scaling is critical for KNN since it
        #   uses Euclidean distance.
        # Why weights='distance':
        #   Closer neighbors have more influence than distant ones.
        "KNN": KNeighborsClassifier(
            n_neighbors=5,
            weights="distance",
            metric="euclidean",
        ),

        # ── 3. Decision Tree ────────────────────────────────────────
        # How it works:
        #   Recursively splits the feature space using the most informative
        #   feature at each step (measured by Gini impurity or entropy).
        # Why max_depth=10:
        #   Prevents the tree from growing too deep (overfitting). A tree
        #   without depth limits will memorize the training data.
        # Why min_samples_leaf=5:
        #   Each leaf must have at least 5 samples — another overfitting
        #   control.
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10,
            min_samples_leaf=5,
            criterion="gini",
            random_state=42,
        ),

        # ── 4. Random Forest (tuned) ───────────────────────────────
        # How it works:
        #   Trains multiple decision trees on random subsets of the data
        #   and features (bagging). The final prediction is the majority
        #   vote across all trees. This reduces overfitting compared to
        #   a single decision tree.
        # Tuned params:
        #   200 trees, max_depth=20, min_samples_leaf=2 for better
        #   generalization on the larger 5000-sample dataset.
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_leaf=2,
            min_samples_split=4,
            max_features="sqrt",
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

        # ── 5. Support Vector Machine (tuned) ──────────────────────
        # How it works:
        #   Finds the hyperplane that maximizes the margin between classes.
        #   The RBF kernel allows SVM to handle non-linearly separable data
        #   by projecting features into a higher-dimensional space.
        # Why probability=True:
        #   Enables predict_proba() for confidence scores.
        # Tuned: C=5.0 provides tighter decision boundaries.
        "SVM": SVC(
            kernel="rbf",
            C=5.0,
            gamma="scale",
            class_weight="balanced",
            probability=True,
            random_state=42
        ),

        # ── 6. Gradient Boosting (tuned) ───────────────────────────
        # How it works:
        #   Builds trees sequentially, each one correcting the errors
        #   of the previous.
        # Tuned: 200 estimators, learning_rate=0.05 for smoother convergence.
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            min_samples_leaf=4,
            subsample=0.8,
            random_state=42,
        ),
    }

    # ── 7. XGBoost ─────────────────────────────────────────────────
    # How it works:
    #   Optimized distributed gradient boosting library. Typically
    #   outperforms sklearn's GradientBoosting in both speed and accuracy.
    # Falls back to a second sklearn GB if xgboost isn't installed.
    if _HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        )
    else:
        # Fallback if xgboost is not installed
        models["XGBoost (sklearn)"] = GradientBoostingClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            min_samples_leaf=3,
            subsample=0.8,
            random_state=42,
        )

    # ── 8. Voting Ensemble ─────────────────────────────────────────
    # How it works:
    #   Combines RF, best boosting model, and SVM using 'soft' voting
    #   (averaging probabilities). Creates a highly stable super-model.
    rf_for_vote = RandomForestClassifier(
        n_estimators=200, max_depth=20, min_samples_leaf=2,
        max_features="sqrt", class_weight="balanced",
        random_state=42, n_jobs=-1,
    )
    svm_for_vote = SVC(
        kernel="rbf", C=5.0, class_weight="balanced",
        probability=True, random_state=42,
    )

    if _HAS_XGBOOST:
        boost_for_vote = XGBClassifier(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            min_child_weight=3, subsample=0.8, colsample_bytree=0.8,
            use_label_encoder=False, eval_metric="mlogloss",
            random_state=42, n_jobs=-1, verbosity=0,
        )
        vote_name = "xgb"
    else:
        boost_for_vote = GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05, max_depth=5,
            subsample=0.8, random_state=42,
        )
        vote_name = "gb"

    models["Voting Ensemble"] = VotingClassifier(
        estimators=[
            ("rf", rf_for_vote),
            (vote_name, boost_for_vote),
            ("svm", svm_for_vote),
        ],
        voting="soft",
        n_jobs=-1,
    )

    return models


def get_model_descriptions() -> dict[str, str]:
    """
    Return human-readable descriptions of each model for the UI.

    Returns:
        Dictionary mapping model names to their descriptions.
    """
    descriptions = {
        "Logistic Regression": (
            "A linear classifier that models the probability of each class "
            "using the logistic function. Simple, fast, and interpretable. "
            "Works well when features have a roughly linear relationship with "
            "the log-odds of the target class."
        ),
        "KNN": (
            "K-Nearest Neighbors is a non-parametric algorithm that classifies "
            "a new point based on the majority class among its k closest neighbors "
            "in feature space. It requires feature scaling and is sensitive to the "
            "choice of k and the distance metric."
        ),
        "Decision Tree": (
            "A tree-structured classifier that recursively partitions the feature "
            "space using the most informative feature at each split. Easy to interpret "
            "and visualize, but prone to overfitting without depth constraints."
        ),
        "Random Forest": (
            "An ensemble of decision trees trained on random subsets of data and "
            "features (bagging). Reduces overfitting by averaging predictions across "
            "many trees. Generally provides higher accuracy than a single tree."
        ),
        "SVM": (
            "Support Vector Machine finds the optimal hyperplane that separates "
            "classes with maximum margin. The RBF kernel enables non-linear "
            "classification by mapping features to a higher-dimensional space."
        ),
        "Gradient Boosting": (
            "A sequential ensemble method that builds decision trees iteratively, "
            "where each new tree corrects the errors of the previous ones. "
            "Highly accurate and robust to complex, non-linear relationships."
        ),
        "XGBoost": (
            "Extreme Gradient Boosting — an optimized gradient boosting library "
            "that is faster and often more accurate than standard gradient boosting. "
            "Uses regularization (L1/L2), column subsampling, and efficient "
            "tree-building algorithms for superior performance."
        ),
        "XGBoost (sklearn)": (
            "Fallback implementation using scikit-learn's GradientBoosting when "
            "the xgboost library is not installed. Provides similar sequential "
            "boosting behavior with slightly less optimization."
        ),
        "Voting Ensemble": (
            "Combines predictions from Random Forest, XGBoost (or Gradient Boosting), "
            "and SVM using 'soft' voting (averaging probabilities). This creates a highly "
            "stable 'super-model' that minimizes the weaknesses of any single algorithm."
        ),
    }
    return descriptions
