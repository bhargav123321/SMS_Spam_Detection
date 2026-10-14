
import os
import html
import joblib
import pandas as pd
import streamlit as st
from utils import clean_text

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="SpamShield AI | SMS Spam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080f1e;
    --card: #121e31;
    --border: #293a55;
    --text: #f1f5f9;
    --muted: #a8b8cf;
    --accent: #60a5fa;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 85% 0%,
            rgba(37,99,235,0.17), transparent 45%),
        radial-gradient(ellipse at 0% 75%,
            rgba(124,58,237,0.11), transparent 45%),
        var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 1160px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #101a2b;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

h1, h2, h3 {
    color: #f8fafc !important;
}

p, label {
    color: #d3deed;
}

.hero {
    text-align: center;
    padding: 38px 14px 28px;
    animation: fadeIn 0.7s ease-out;
}

.hero-badge {
    display: inline-block;
    color: #93c5fd;
    background: rgba(37,99,235,0.14);
    border: 1px solid rgba(96,165,250,0.35);
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.2px;
}

.hero-title {
    font-size: clamp(32px, 5vw, 56px);
    font-weight: 800;
    line-height: 1.16;
    letter-spacing: -1.5px;
    margin: 20px 0 14px;
    color: #f8fafc;
}

.gradient-text {
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #a8b8cf;
    font-size: 16px;
    max-width: 660px;
    margin: 0 auto;
    line-height: 1.7;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #f8fafc;
    margin: 12px 0 16px;
}

.info-card {
    background: rgba(18,30,49,0.93);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.info-card:hover {
    transform: translateY(-3px);
    border-color: #4169a5;
}

.stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #93c5fd;
    margin-bottom: 5px;
}

.stat-label {
    color: #a8b8cf;
    font-size: 13px;
}

.result-spam {
    background: linear-gradient(135deg, #3b1728, #231827);
    border: 1px solid #a94462;
    border-radius: 18px;
    padding: 25px;
    margin: 18px 0;
    animation: fadeIn 0.45s ease;
}

.result-ham {
    background: linear-gradient(135deg, #12382f, #14292c);
    border: 1px solid #2d987c;
    border-radius: 18px;
    padding: 25px;
    margin: 18px 0;
    animation: fadeIn 0.45s ease;
}

.result-title {
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 8px;
}

.result-description {
    font-size: 14px;
    line-height: 1.7;
    color: #e2e8f0;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 700;
    min-height: 48px;
    box-shadow: 0 6px 22px rgba(37,99,235,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 9px 26px rgba(99,102,241,0.35);
}

.stTextArea textarea {
    background: #0c1729 !important;
    color: #f8fafc !important;
    border: 1px solid #354762 !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

.stTextArea textarea:focus {
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 2px rgba(96,165,250,0.15) !important;
}

div[data-testid="stMetric"] {
    background: #142238;
    border: 1px solid #293a55;
    border-radius: 14px;
    padding: 16px;
}

div[data-testid="stMetricValue"] {
    color: #93c5fd;
}

.footer {
    text-align: center;
    padding: 28px 10px 12px;
    color: #94a3b8;
    font-size: 12px;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.85rem 2rem;
    }

    .hero {
        padding: 24px 4px 20px;
    }

    .hero-title {
        letter-spacing: -0.7px;
    }

    .hero-subtitle {
        font-size: 14px;
    }

    .info-card {
        padding: 16px;
    }

    .result-title {
        font-size: 21px;
    }

    .stat-value {
        font-size: 23px;
    }
}
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD MODELS --------------------
MODEL_DIR = "models"

@st.cache_resource
def load_models():
    vectorizer = joblib.load(
        os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
    )
    nb = joblib.load(
        os.path.join(MODEL_DIR, "naive_bayes_model.pkl")
    )
    lr = joblib.load(
        os.path.join(MODEL_DIR, "logistic_regression_model.pkl")
    )
    return vectorizer, nb, lr

try:
    vectorizer, nb_model, lr_model = load_models()
except (FileNotFoundError, OSError) as e:
    st.error("Model files not found. Please run python train.py first.")
    st.code("python train.py")
    st.caption(str(e))
    st.stop()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## 🛡️ SpamShield AI")
    st.caption("INTELLIGENT MESSAGE PROTECTION")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📊 Model Comparison", "ℹ️ About Project"]
    )

    st.divider()

    st.markdown("### ⚙️ Model Settings")

    model_name = st.selectbox(
        "Classification Model",
        ["Logistic Regression", "Multinomial Naive Bayes"]
    )

    st.info(
        "Both models use TF-IDF text features. "
        "You can switch models to compare predictions."
    )

    st.divider()
    st.caption("Python • Scikit-learn • Streamlit")
    st.caption("Educational NLP Project")

# -------------------- PREDICTION FUNCTION --------------------
def predict_message(message, model_name):
    cleaned = clean_text(message)

    if not cleaned:
        return None

    features = vectorizer.transform([cleaned])

    model = (
        lr_model if model_name == "Logistic Regression"
        else nb_model
    )

    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    classes = list(model.classes_)
    spam_probability = float(
        probabilities[classes.index("spam")]
    )

    return prediction, spam_probability

# -------------------- DASHBOARD --------------------
if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <div class="hero-badge">✦ AI-POWERED SMS ANALYSIS</div>
        <div class="hero-title">
            Detect SMS Spam<br>
            <span class="gradient-text">Instantly & Intelligently</span>
        </div>
        <div class="hero-subtitle">
            Analyze text messages with Natural Language Processing
            and Machine Learning. Identify patterns associated with
            spam in just a few seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Statistics
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">
            <div class="stat-value">02</div>
            <div class="stat-label">ML Classification Models</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <div class="stat-value">TF-IDF</div>
            <div class="stat-label">NLP Feature Extraction</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <div class="stat-value">Real-Time</div>
            <div class="stat-label">On-Demand Prediction</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">✉️ SMS Message Analyzer</div>',
        unsafe_allow_html=True
    )

    # Example messages
    examples = {
        "Custom Message": "",
        "Promotional Spam": (
            "Congratulations! You have won a free prize. "
            "Click here to claim your reward now!"
        ),
        "Normal Message": (
            "Hey! Are we still meeting at college tomorrow morning?"
        ),
        "Suspicious Link": (
            "Your account will be suspended today. "
            "Verify your details at https://example.com now."
        ),
        "OTP Message": (
            "Your verification code is 482931. "
            "Do not share this code with anyone."
        )
    }

    example_choice = st.selectbox(
        "Try a sample message",
        list(examples.keys())
    )

    if "sms_text" not in st.session_state:
        st.session_state.sms_text = ""

    if st.session_state.get("last_example") != example_choice:
        st.session_state.sms_text = examples[example_choice]
        st.session_state.last_example = example_choice

    message = st.text_area(
        "Enter your SMS message",
        key="sms_text",
        height=155,
        placeholder="Paste or type an SMS message here..."
    )

    st.caption(f"Message length: {len(message)} characters")

    analyze = st.button(
        "🔍 Analyze Message",
        type="primary",
        use_container_width=True
    )

    if analyze:
        if not message.strip():
            st.warning("Please enter a message to analyze.")
        else:
            result = predict_message(message, model_name)

            if result is None:
                st.warning("Please enter a message containing readable text.")
            else:
                prediction, spam_probability = result
                ham_probability = 1 - spam_probability

                st.markdown(
                    '<div class="section-title">📋 Analysis Result</div>',
                    unsafe_allow_html=True
                )

                if prediction == "spam":
                    st.markdown("""
                    <div class="result-spam">
                        <div class="result-title" style="color:#fda4af;">
                            ⚠️ Likely Spam Detected
                        </div>
                        <div class="result-description">
                            This message contains patterns commonly
                            associated with spam in the training data.
                            Be cautious with links, requests for money,
                            and requests for personal information.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="result-ham">
                        <div class="result-title" style="color:#86efac;">
                            ✅ Likely Legitimate Message
                        </div>
                        <div class="result-description">
                            The model classified this message as ham.
                            However, a legitimate classification does
                            not guarantee the message is safe.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Spam Probability",
                        f"{spam_probability * 100:.1f}%"
                    )

                with col2:
                    st.metric(
                        "Ham Probability",
                        f"{ham_probability * 100:.1f}%"
                    )

                st.markdown("#### 📊 Probability Distribution")

                chart_data = pd.DataFrame({
                    "Class": ["Spam", "Ham"],
                    "Estimated Probability": [
                        spam_probability,
                        ham_probability
                    ]
                }).set_index("Class")

                st.bar_chart(
                    chart_data,
                    color="#60a5fa",
                    horizontal=True
                )

                st.caption(
                    "These are model-estimated probabilities, "
                    "not verified fraud or safety probabilities."
                )

                with st.expander("🔎 Detailed Prediction Information"):
                    st.write("**Model:**", model_name)
                    st.write("**Feature Extraction:** TF-IDF")
                    st.write("**Prediction:**", prediction.upper())
                    st.write("**Message Length:**", len(message))
                    st.write("**Cleaned Message:**")
                    st.code(clean_text(message), language=None)

                    st.info(
                        "The model identifies statistical patterns "
                        "in SMS text. It cannot independently verify "
                        "the identity or intentions of a sender."
                    )

    st.markdown(
        '<div class="section-title">🚀 How It Works</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    with a:
        st.markdown("""
        <div class="info-card">
            <h3>📝 01. Input</h3>
            <p>Enter or paste your SMS message into the analyzer.</p>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown("""
        <div class="info-card">
            <h3>🧠 02. Analyze</h3>
            <p>NLP and machine learning extract patterns from text.</p>
        </div>
        """, unsafe_allow_html=True)

    with c:
        st.markdown("""
        <div class="info-card">
            <h3>🛡️ 03. Predict</h3>
            <p>View the predicted class and probability estimates.</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------- MODEL COMPARISON --------------------
elif page == "📊 Model Comparison":

    st.title("📊 Model Performance Dashboard")
    st.write(
        "Compare the trained classifiers using their saved "
        "evaluation metrics and confusion matrices."
    )

    comparison_path = os.path.join(
        MODEL_DIR, "model_comparison.csv"
    )

    if os.path.exists(comparison_path):
        comparison = pd.read_csv(comparison_path)

        st.subheader("Evaluation Metrics")
        st.dataframe(
            comparison.style.format({
                col: "{:.2%}"
                for col in comparison.columns
                if col != "Model"
            }),
            use_container_width=True,
            hide_index=True
        )

        metric = st.selectbox(
            "Choose metric to compare",
            [
                col for col in comparison.columns
                if col != "Model"
            ]
        )

        st.bar_chart(
            comparison.set_index("Model")[[metric]],
            color="#818cf8"
        )
    else:
        st.warning(
            "Model comparison CSV not found. "
            "Run python train.py first."
        )

    st.subheader("Confusion Matrices")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Naive Bayes**")
        path = os.path.join(
            MODEL_DIR, "confusion_naive_bayes.png"
        )
        if os.path.exists(path):
            st.image(path, use_container_width=True)

    with col2:
        st.markdown("**Logistic Regression**")
        path = os.path.join(
            MODEL_DIR, "confusion_logistic_regression.png"
        )
        if os.path.exists(path):
            st.image(path, use_container_width=True)

    st.info(
        "False positive: a legitimate message predicted as spam. "
        "False negative: a spam message predicted as legitimate."
    )

# -------------------- ABOUT PROJECT --------------------
else:

    st.title("ℹ️ About SpamShield AI")

    st.markdown("""
    ### Project Overview

    **SMS Spam Message Detection** is a Natural Language
    Processing project that classifies SMS messages as spam
    or legitimate (ham).

    ### Problem Statement

    SMS spam may include unwanted advertisements, suspicious
    links, deceptive offers, or misleading requests.
    This application estimates whether a message resembles
    spam based on patterns learned from labeled data.

    ### Machine Learning Pipeline

    1. Load the UCI SMS Spam Collection dataset.
    2. Check missing values, duplicates and class imbalance.
    3. Clean and normalize SMS text.
    4. Convert messages into TF-IDF features.
    5. Split the dataset into training and testing sets.
    6. Train Multinomial Naive Bayes and Logistic Regression.
    7. Evaluate accuracy, precision, recall and F1-score.
    8. Examine false positives and false negatives.
    9. Save the models and vectorizer.
    10. Use Streamlit for interactive prediction.

    ### Technologies Used

    - **Python:** Main programming language
    - **Pandas:** Data processing
    - **Scikit-learn:** Machine learning
    - **TF-IDF:** Text feature extraction
    - **Joblib:** Model serialization
    - **Streamlit:** Web application

    ### Dataset

    UCI SMS Spam Collection

    ### Important Limitation

    A spam classification does not prove fraud.
    A ham classification does not guarantee safety.
    Always verify suspicious messages independently.
    """)

# -------------------- FOOTER --------------------
st.markdown("""
<div class="footer">
    🛡️ SpamShield AI · SMS Spam Detection Project<br>
    Built with Python, NLP, Machine Learning & Streamlit<br>
    Educational predictions only — not a fraud verification service.
</div>
""", unsafe_allow_html=True)
