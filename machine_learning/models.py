"""
ML Models Module for Visionlytics.

Defines and configures the statistical machine learning models used for
crowd density classification. Each model is a classical ML algorithm
from scikit-learn.

Models:
    1. Logistic Regression — Linear classifier using logistic function
    2. K-Nearest Neighbors (KNN) — Instance-based learning, classifies
       based on k closest training examples
    3. Decision Tree — Tree-based classifier using information gain
    4. Random Forest — Ensemble of decision trees with bagging
    5. Support Vector Machine (SVM) — Finds optimal hyperplane separation

ML Concepts Demonstrated:
    - Linear vs non-linear classifiers
    - Parametric vs non-parametric models
    - Ensemble methods
    - Kernel methods
    - Overfitting control via hyperparameters
"""

from typing import Any

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def get_models() -> dict[str, Any]:
    """
    Create and return all ML models with their configurations.

    Each model is configured with reasonable hyperparameters for a
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

        # ── 4. Random Forest ────────────────────────────────────────
        # How it works:
        #   Trains multiple decision trees on random subsets of the data
        #   and features (bagging). The final prediction is the majority
        #   vote across all trees. This reduces overfitting compared to
        #   a single decision tree.
        # Why n_estimators=100:
        #   100 trees provide a good balance between performance and
        #   computation time.
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=2,  # Constrain cores to prevent memory exhaustion
        ),

        # ── 5. Support Vector Machine ───────────────────────────────
        # How it works:
        #   Finds the hyperplane that maximizes the margin between classes.
        #   The RBF kernel allows SVM to handle non-linearly separable data
        #   by projecting features into a higher-dimensional space.
        # Why probability=True:
        #   Enables predict_proba() for confidence scores.
        # Why C=2.0 and class_weight='balanced':
        #   Optimized for better boundary resolution on imbalanced subsets.
        "SVM": SVC(
            kernel="rbf", 
            C=2.0, 
            gamma="scale", 
            class_weight="balanced", 
            probability=True, 
            random_state=42
        ),

        # ── 6. Gradient Boosting ────────────────────────────────────
        # How it works:
        #   Builds trees sequentially, each one correcting the errors of the previous.
        # Why max_depth=5:
        #   Keeps individual trees relatively weak to prevent overfitting.
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
        ),

        # ── 7. Voting Ensemble ──────────────────────────────────────
        # How it works:
        #   Combines RF, GB, and SVM using 'soft' voting (averaging probabilities).
        # Why:
        #   Produces a highly stable model that leverages the strengths of all 3.
        "Voting Ensemble": VotingClassifier(
            estimators=[
                ("rf", RandomForestClassifier(n_estimators=150, max_depth=15, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=2)),
                ("gb", GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)),
                ("svm", SVC(kernel="rbf", C=2.0, class_weight="balanced", probability=True, random_state=42)),
            ],
            voting="soft",
            n_jobs=2
        ),
    }

    return models


def get_model_descriptions() -> dict[str, str]:
    """
    Return human-readable descriptions of each model for the UI.

    Returns:
        Dictionary mapping model names to their descriptions.
    """
    return {
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
        "Voting Ensemble": (
            "Combines predictions from Random Forest, Gradient Boosting, and SVM "
            "using 'soft' voting (averaging probabilities). This creates a highly "
            "stable 'super-model' that minimizes the weaknesses of any single algorithm."
        ),
    }
