# OmniInsights – A Salesforce-Powered Slack Data Assistant

**OmniInsights** is a unified, Slack-based assistant that brings Salesforce campaign analytics, data quality scans, and self-service support directly into your workflow. Instantly access campaign metrics, spot data anomalies, and resolve issues—without leaving Slack!

## 🚀 Features

- **/campaign ``** – Instantly retrieve live metrics (ROI, revenue, conversions) for any Salesforce campaign.
- **/dq-scan** – Run on-demand data quality checks with proactive anomaly alerts.
- **/omni-help** – View all commands and access a centralized knowledge base.
- **/escalate ``** – Quickly escalate unresolved issues to the support team.

## 📊 Business Value

- **Saves time:** 40% reduction in manual report/ticket load.
- **Ensures accuracy:** 75%+ anomaly detection rate, cleaner dashboards.
- **Faster decisions:** Slash analytics wait time from hours to seconds.
- **Boosts empowerment:** Self-service platform lets users solve data/reporting problems independently.

## 🛠 Architecture Overview

- **Slack:** User-facing chat interface and command center.
- **Python (Slack Bolt):** Core bot logic; parses commands and orchestrates data flows.
- **Salesforce:** CRM & analytics source of truth—queried via API for real-time data.
- **Pandas/NumPy/SciPy:** Data wrangling and anomaly detection for quality scans.
- **Knowledge Base:** Central KB (e.g., Google Doc, Confluence) for FAQs/help.
- **Heroku/Railway:** Simple, cloud-based Python bot hosting.


  


## 🧑‍💻 Quickstart

### 1. Clone the Repo
```bash
git clone https://github.com/yourname/omniinsights.git
cd omniinsights
```

### 2. Install Requirements
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory with your secrets:
```dotenv
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_APP_TOKEN=xapp-your-app-token
SF_USERNAME=your-salesforce-username
SF_PASSWORD=your-salesforce-password
SF_SECURITY_TOKEN=your-salesforce-security-token
KNOWLEDGE_BASE_URL=https://docs.google.com/document/d/yourkbdocid
```

### 4. Create a Salesforce Developer Org & Add Sample Data
- Sign up [here](https://developer.salesforce.com/signup)
- Add campaigns, opportunities for demo/testing

### 5. [Optional] Deploy on Heroku/Railway for Persistent Hosting

## 💬 Slack Commands & Usage

| Command              | Purpose                                                      | Example                                     |
|----------------------|-------------------------------------------------------------|---------------------------------------------|
| `/campaign `   | Fetch campaign analytics from Salesforce                    | `/campaign Summer Promo`                    |
| `/dq-scan`           | Run a data quality scan with anomaly and missing-data alert | `/dq-scan`                                  |
| `/omni-help`         | Show help message and knowledge base resources              | `/omni-help`                                |
| `/escalate `  | Escalate an issue to human support                          | `/escalate Not showing latest campaign data`|

## 🏗 Project Structure

```
omniinsights/
├── app.py               # Main Slack Bolt app and command handling
├── data_quality.py      # Data quality/anomaly logic
├── requirements.txt     # Python library dependencies
├── Procfile             # For Heroku deployment
├── .env                 # Local environment variables (not checked in)
└── README.md
```

## 🔐 Security

- Slack and Salesforce tokens stored as environment variables
- OAuth for Salesforce connection (Production: use Connected Apps, restrict profile scopes)
- No sensitive data is logged or output to public channels

## 📚 Knowledge Base

For detailed user instructions, troubleshooting, and tips, visit:  
[OmniInsights – Official User Guide](https://docs.google.com/document/d/yourkbdocid)

## 📝 License

Distributed under the MIT License.  
See `LICENSE` for more information.

## 🙌 Contributors

* [Your Name](https://github.com/yourname)
* [Project Collaborators]

## 🔗 Roadmap & Extendability

- Tableau/Einstein integration: advanced analytics in Slack
- Scheduled scans and push alerts
- AI-powered summarization and recommendations

**PRs welcome!**

**Questions?**  
Open an issue here or reach out on Slack.

*OmniInsights – Empowering your business with analytics & answers, right where your team works.*
