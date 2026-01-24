🚀 AI-Powered CRM Analytics: CLTV Prediction & Churn Management
This project is a comprehensive SaaS-ready CRM solution that combines advanced statistical modeling with Generative AI. It predicts the future value of customers, identifies those at risk of leaving, and automatically generates personalized marketing strategies.

🛠️ Tech Stack & Models
Data Processing: Python, Pandas, Numpy

Statistical Modeling: * BG/NBD: To predict the expected number of transactions.

Gamma-Gamma: To estimate the average transaction value.

Generative AI: Integrated with OpenAI's GPT-4o-mini via API for automated insight generation.

Visualization: Power BI (Professional Dashboard with Fixed Decimal formatting).

💡 Key Features
CLTV Prediction: Calculates the 6-month "Customer Lifetime Value" for each individual.

Churn Risk Analysis: A custom algorithm calculates risk scores based on "Probability of Being Alive" (prob_alive) and segments customers from "Stable" to "Critical Risk".

AI Strategy Engine: Automatically sends segment data to GPT-4o-mini to receive tailored "Win-back" and "Upselling" actions in English.

Professional Dashboard: Includes KPI cards, Churn risk donut charts, and AI-generated strategy cards.

📊 Business Impact
Instead of looking at historical data only, this tool provides forward-looking insights:

Retention: Identify high-value customers before they churn.

Efficiency: Use low-cost, high-speed AI models (GPT-4o-mini) to replace manual marketing analysis.

Data Integrity: Cleaned financial data using fixed-point decimals to ensure reporting accuracy.

How to Run
Clone the repo.

Install dependencies: pip install -r requirements.txt

Create a .env file and add your OPENAI_API_KEY.

Run the main_analysis.ipynb notebook.
<img width="1292" height="869" alt="image" src="https://github.com/user-attachments/assets/ceed99b3-a775-4749-8019-348868192ca2" />

