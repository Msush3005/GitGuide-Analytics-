# GitGuide Analytics - Exploratory Notebooks

This directory contains interactive Jupyter Notebooks (`.ipynb`) used for exploratory data analysis (EDA), data cleaning trials, outlier detection visual checks, feature engineering experimentation, and correlation matrix analysis prior to production script modularization.

## Notebook Index

1. **`01_data_exploration_and_ingestion.ipynb`**:
   - Initial Data Profiling & Null Value Distribution
   - Multi-Format Data Ingestion Checks
   - Feature Histograms & Skewness Analysis
2. **`02_cleaning_outliers_and_merging.ipynb`**:
   - Z-score and IQR Outlier Detection Visualizations & Capping
   - String Cleaning & Normalization Experiments
   - Relational Table Merging & Join Diagnostic Checks
3. **`03_feature_engineering_and_segmentation.ipynb`**:
   - Ratio Feature Construction (Time & Volume Normalization)
   - Equal-Width (`pd.cut`) & Equal-Frequency (`pd.qcut`) Binning Visualizations
   - Composite RFM (Recency, Frequency, Monetary) Customer Segmentation Scoring
4. **`04_feature_correlation_and_causation.ipynb`**:
   - Pearson (linear) vs. Spearman (monotonic) Correlation Matrix Comparisons
   - Annotated Heatmap Visualizations (`output/correlation_heatmap.png`)
   - High Collinear Pair Isolation ($|r| > 0.7$) & Business Causation Analysis
   - Redundancy Feature Selection
