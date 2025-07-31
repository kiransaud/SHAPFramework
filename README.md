# XAI-SHAP Framework: Explainable AI for Defect Prediction

## 📖 Overview

This repository contains a comprehensive **Explainable AI (XAI) framework** using **SHAP (SHapley Additive exPlanations)** for defect prediction and analysis. The framework provides interpretable machine learning models with detailed explanations for stakeholders to understand model decisions and feature importance.

## 🌟 Features

- **Defect Prediction Model**: Machine learning model for predicting defects with high accuracy
- **SHAP Explanations**: Comprehensive model interpretability using SHAP values
- **Multi-Stakeholder Analysis**: Tailored explanations for different user groups
- **Rich Visualizations**: Interactive plots and charts for better understanding
- **HTML Reports**: Detailed explanation reports for stakeholders

## 📊 Visualizations Included

- **🐝 Beeswarm Plot**: Feature importance distribution
- **🔥 Heat Map**: Feature correlation analysis  
- **📊 Local Bar Plot**: Individual prediction explanations
- **💧 Waterfall Plot**: Step-by-step prediction breakdown
- **📈 Decision Plot**: Model decision pathways
- **🎯 Force Plot**: Individual instance explanations
- **📋 Feature Importance**: Global feature ranking

## 🗂️ Repository Structure

```
XAI-SHAP/
├── 📓 defect-model.ipynb          # Main analysis notebook
├── 📊 dataset/                    # Training and test datasets
├── 🤖 models/                     # Trained models and artifacts
│   ├── background.pkl             # SHAP background data
│   └── threshold.json             # Model thresholds
├── 📈 explanations/               # SHAP explanation outputs
├── 🖼️ *.png                      # Visualization outputs
├── 📄 *.html                      # Interactive explanation reports
├── 📋 static/                     # Static web assets
└── 📊 *.csv                       # Analysis results
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install shap
pip install pandas numpy scikit-learn
pip install matplotlib seaborn plotly
pip install jupyter
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kiransaud/SHAPFramework.git
   cd SHAPFramework
   ```

2. **Open the main notebook**
   ```bash
   jupyter notebook defect-model.ipynb
   ```

3. **Run the analysis**
   - Execute all cells in the notebook
   - View generated visualizations
   - Check HTML reports for detailed explanations

## 📋 Usage

### 1. Model Training & Prediction
The main notebook (`defect-model.ipynb`) contains:
- Data preprocessing and feature engineering
- Model training and validation
- Performance evaluation metrics

### 2. SHAP Analysis
- **Global Explanations**: Understanding overall model behavior
- **Local Explanations**: Individual prediction explanations
- **Feature Interactions**: How features work together

### 3. Stakeholder Reports
- **Technical Users**: Detailed SHAP analysis with code
- **Business Users**: High-level insights in HTML reports
- **End Users**: Simple, actionable explanations

## 📈 Key Insights

- **Most Important Features**: Identified through SHAP global importance
- **Prediction Confidence**: Model uncertainty quantification  
- **Feature Interactions**: Complex relationships between variables
- **Decision Boundaries**: Clear model decision criteria

## 🔍 Explanation Types

| Explanation Type | File | Purpose |
|-----------------|------|---------|
| **Global Summary** | `feature importance.png` | Overall feature ranking |
| **Local Instance** | `force_plot_instance_5.png` | Individual prediction |
| **Population View** | `BeeswarmPlot.png` | Feature distribution impact |
| **Correlation Analysis** | `HeatMap.png` | Feature relationships |
| **Decision Path** | `decisionplot.png` | Model reasoning path |

## 📊 Model Performance

- **Accuracy**: High predictive performance on test set
- **Interpretability**: Full model transparency with SHAP
- **Robustness**: Validated across multiple datasets
- **Stakeholder Satisfaction**: Clear, actionable explanations

## 🛠️ Technical Details

- **Framework**: Python-based implementation
- **ML Library**: Scikit-learn for model development
- **Explainability**: SHAP for model interpretability
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Export**: HTML and PNG formats for sharing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📝 Citation

If you use this framework in your research, please cite:

```bibtex
@software{shap_framework_2024,
  title={XAI-SHAP Framework: Explainable AI for Defect Prediction},
  author={Kiran Saud},
  year={2024},
  url={https://github.com/kiransaud/SHAPFramework}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Author**: Kiran Saud
- **GitHub**: [@kiransaud](https://github.com/kiransaud)
- **Repository**: [SHAPFramework](https://github.com/kiransaud/SHAPFramework)

## 🙏 Acknowledgments

- SHAP library developers for excellent explainability tools
- Open source community for valuable feedback and contributions
- Research community for advancing explainable AI methods

---

⭐ **Star this repository if you find it helpful!**
