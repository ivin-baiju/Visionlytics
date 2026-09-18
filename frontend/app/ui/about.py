"""
About Page for Visionlytics.

Provides detailed project documentation, academic background, architecture
explanations, statistical machine learning methodology, and ethical considerations
for the Semester 3 Statistical Machine Learning project.
"""

import streamlit as st

from app.components.icons import ICON_OBJECTIVES, ICON_TARGET
from app.components.styles import header_html


def render_about():
    """Render the About & Documentation page."""
    st.markdown(header_html(), unsafe_allow_html=True)
    st.header("About Visionlytics", icon=":material/info:")
    st.markdown(
        "**VISIONLYTICS: Intelligent Visual Crowd Analytics** is a comprehensive "
        "Computer Vision and Statistical Machine Learning project engineered for "
        "academic evaluation in Semester 3 Statistical Machine Learning."
    )

    st.markdown("---")

    col_proj, col_obj = st.columns(2)

    with col_proj:
        st.markdown(f"""
        <div class="section-container">
            <h3 style="margin-top:0; color:#4A7DFF; display:flex; align-items:center; gap:0.6rem;">
                {ICON_TARGET}
                <span>Project purpose</span>
            </h3>
            <p style="color: #5a6578; font-size: 0.9rem;">
                Traditional computer vision demonstrations often rely solely on pretrained
                black-box models. <strong>VISIONLYTICS</strong> bridges modern Computer Vision
                and classical <strong>Statistical Machine Learning</strong> by using object detection
                as a spatial sensor to extract rigorous geometric feature vectors, followed by
                rigorous statistical classification, validation, and benchmarking.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_obj:
        st.markdown(f"""
        <div class="section-container">
            <h3 style="margin-top:0; color:#2ECDA7; display:flex; align-items:center; gap:0.6rem;">
                {ICON_OBJECTIVES}
                <span>Key objectives</span>
            </h3>
            <p style="color: #5a6578; font-size: 0.9rem;">
                • Real-time person detection across images, video files, and webcam streams.<br>
                • Extraction of 10 calibrated spatial, geometric, and regional crowd features.<br>
                • Training, validation, and empirical comparison of 7 classical ML algorithms.<br>
                • Strict prevention of data leakage via disciplined 70/15/15 stratified splits.<br>
                • Interactive visual crowd analytics, spatial heatmaps, and temporal charts.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Feature Engineering Section ──────────────────────────────────
    st.subheader("Feature engineering (10 spatial attributes)", icon=":material/square_foot:")
    st.markdown("""
    The system extracts a **10-dimensional feature vector** $\\mathbf{x} \\in \\mathbb{R}^{10}$
    for each video frame or static image:
    """)

    st.markdown(r"""
    | # | Feature Name | Description | Statistical Relevance |
    |---|--------------|-------------|-----------------------|
    | 1 | `people_count` | Total count of detected individuals ($N$) | Primary scale indicator for crowd density |
    | 2 | `occupancy_ratio` | Total bounding box area / Frame area | Accounts for scale and perspective variations |
    | 3 | `avg_person_area` | Mean individual bounding box area | Distinguishes distant dense crowds vs close individuals |
    | 4 | `avg_distance` | Mean pairwise Euclidean distance between centers | Measures spatial packing and interpersonal spacing |
    | 5 | `min_distance` | Minimum pairwise distance in the frame | Pinpoints localized clustering and bottleneck points |
    | 6 | `spatial_spread` | Spatial standard deviation ($\sigma_x^2 + \sigma_y^2$) | Quantifies uniformity vs localized gathering |
    | 7 | `top_region_count` | Persons detected in upper vertical third | Captures depth distribution and background density |
    | 8 | `middle_region_count`| Persons detected in middle vertical third | Captures midground gathering density |
    | 9 | `bottom_region_count`| Persons detected in lower vertical third | Captures foreground proximity and camera ingress |
    | 10 | `frame_occupancy_density`| $\frac{N}{\text{frame width} \times \text{frame height}} \times 10^5$ | Normalized scale-invariant spatial frequency |
    """)

    st.markdown("---")

    # ── ML Algorithms Section ────────────────────────────────────────
    st.subheader("Statistical machine learning algorithms", icon=":material/neurology:")

    c_ml1, c_ml2 = st.columns(2)

    with c_ml1:
        st.markdown("""
        #### 1. Multinomial Logistic Regression
        - **Formulation**: Softmax over linear combinations of standardized features:
          $$P(y = k \\mid \\mathbf{x}) = \\frac{e^{\\mathbf{w}_k^T \\mathbf{x} + b_k}}{\\sum_{j=1}^K e^{\\mathbf{w}_j^T \\mathbf{x} + b_j}}$$
        - **Role**: Provides a parametric linear baseline with direct interpretability of odds ratios.

        #### 2. K-Nearest Neighbors (KNN)
        - **Formulation**: Instance-based voting over the $k=5$ closest neighbors under Euclidean metric:
          $$d(\\mathbf{u}, \\mathbf{v}) = \\sqrt{\\sum_{i=1}^{10} (u_i - v_i)^2}$$
        - **Role**: Non-parametric model sensitive to local neighborhood density in feature space.

        #### 3. Decision Tree (CART)
        - **Formulation**: Recursive axis-aligned binary splits minimizing Gini impurity:
          $$I_G(p) = 1 - \\sum_{k=1}^K p_k^2$$
        - **Role**: Generates interpretable if-then decision thresholds on spatial features.
        """)

    with c_ml2:
        st.markdown("""
        #### 4. Random Forest Classifier
        - **Formulation**: Ensemble of 100 decorrelated decision trees using bootstrap aggregating (bagging) and random feature subspace sampling:
          $$\\hat{y} = \\text{mode}\\{T_1(\\mathbf{x}), T_2(\\mathbf{x}), \\dots, T_B(\\mathbf{x})\\}$$
        - **Role**: Highly robust non-linear classifier with low variance and feature importance estimation.

        #### 5. Support Vector Machine (SVM)
        - **Formulation**: Maximum-margin hyperplane with Radial Basis Function (RBF) kernel:
          $$K(\\mathbf{x}, \\mathbf{x}') = \\exp(-\\gamma \\|\\mathbf{x} - \\mathbf{x}'\\|^2)$$
        - **Role**: Excels at separating complex, non-linear class frontiers with high generalization power.

        #### 6. Gradient Boosting
        - **Formulation**: Sequentially builds trees correcting errors of the ensemble:
          $$F_m(\\mathbf{x}) = F_{m-1}(\\mathbf{x}) + \\eta \\cdot h_m(\\mathbf{x})$$
        - **Role**: State-of-the-art accuracy on tabular data, dominant in ML benchmarks.

        #### 7. Voting Ensemble (Soft)
        - **Formulation**: Averages predicted probabilities from RF, GB, and SVM:
          $$\\hat{p}_k = \\frac{1}{M} \\sum_{m=1}^M p_{m,k}(\\mathbf{x})$$
        - **Role**: Meta-learner that cancels out individual model biases for maximum stability.
        """)

    st.markdown("---")

    # ── Methodological Rigor & Data Leakage Prevention ───────────────
    st.subheader("Experimental rigor & leakage prevention", icon=":material/verified_user:")
    st.markdown(r"""
    In accordance with statistical best practices:
    - **Stratified Partitioning**: The dataset is split into **70% Training**, **15% Validation**, and **15% Held-Out Testing** with class proportion preservation.
    - **Independent Feature Standardization**: The `StandardScaler` is fitted **strictly on the training partition** $\mathbf{X}_{\text{train}}$ ($\mu_{\text{train}}, \sigma_{\text{train}}$) and applied without modification to $\mathbf{X}_{\text{val}}$ and $\mathbf{X}_{\text{test}}$.
    - **Evaluation Metrics**: Models are compared using multi-class **Accuracy**, class-specific and weighted **Precision**, **Recall**, **F1-Score**, and complete **Confusion Matrices**.
    """)

    st.markdown("---")

    # ── Privacy and Ethical Standards ────────────────────────────────
    st.subheader("Privacy, ethics & governance", icon=":material/security:")
    st.markdown("""
    <div class="info-box">
        <strong>Privacy by Design:</strong>
        <ul>
            <li><strong>No Facial Recognition:</strong> Bounding boxes and features detect body presence only. No facial embeddings or biometric identities are stored or processed.</li>
            <li><strong>Transient Processing:</strong> Uploaded images and video buffers are processed ephemerally in volatile memory and cleaned up immediately after inference.</li>
            <li><strong>Ethical Attribute Analysis:</strong> Apparent sex classification is disabled / marked UNKNOWN to avoid demographic bias and prevent discriminatory automated classification.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Technology Stack ─────────────────────────────────────────────
    st.subheader("Technology stack", icon=":material/terminal:")
    st.markdown("""
    - **Computer Vision**: Ultralytics YOLOv8s, OpenCV, Pillow
    - **Statistical ML**: Scikit-Learn (7 Classifiers + Ensemble), NumPy, Pandas, Joblib
    - **Visualization**: Plotly Interactive Charts, Matplotlib, Seaborn
    - **Application**: Streamlit, Custom Glassmorphism Design System
    """)
