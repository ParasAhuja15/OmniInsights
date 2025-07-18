import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from simple_salesforce import Salesforce
from scipy import stats
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Salesforce connection
def get_salesforce_connection():
    """Establish connection to Salesforce"""
    try:
        sf = Salesforce(
            username=os.environ.get('SF_USERNAME'),
            password=os.environ.get('SF_PASSWORD'),
            security_token=os.environ.get('SF_SECURITY_TOKEN'),
            domain='test'  # Use 'test' for sandbox, None for production
        )
        return sf
    except Exception as e:
        logger.error(f"Failed to connect to Salesforce: {e}")
        return None

# Campaign Analytics Commands
@app.command("/campaign")
def campaign_analytics(ack, respond, command):
    """Get campaign analytics from Salesforce"""
    ack()
    
    campaign_name = command['text'].strip()
    if not campaign_name:
        respond("Please provide a campaign name. Usage: `/campaign <campaign_name>`")
        return
    
    sf = get_salesforce_connection()
    if not sf:
        respond("Unable to connect to Salesforce")
        return
    
    try:
        # Query campaign data
        query = f"""
        SELECT Id, Name, ActualCost, BudgetedCost, 
               NumberOfLeads, NumberOfConvertedLeads,
               NumberOfContacts, NumberOfOpportunities,
               AmountAllOpportunities, AmountWonOpportunities,
               StartDate, EndDate, Status
        FROM Campaign 
        WHERE Name LIKE '%{campaign_name}%'
        LIMIT 5
        """
        
        results = sf.query(query)
        
        if not results['records']:
            respond(f"No campaigns found matching '{campaign_name}'")
            return
        
        # Format response with business metrics
        response_blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"Campaign Analytics: {campaign_name}"}
            }
        ]
        
        for record in results['records']:
            # Calculate ROI
            roi = 0
            if record.get('ActualCost') and record.get('AmountWonOpportunities'):
                roi = ((record['AmountWonOpportunities'] - record['ActualCost']) / record['ActualCost']) * 100
            
            # Calculate conversion rate
            conversion_rate = 0
            if record.get('NumberOfLeads') and record.get('NumberOfConvertedLeads'):
                conversion_rate = (record['NumberOfConvertedLeads'] / record['NumberOfLeads']) * 100
            
            campaign_block = {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Campaign:* {record['Name']}"},
                    {"type": "mrkdwn", "text": f"*Status:* {record.get('Status', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Actual Cost:* ${record.get('ActualCost', 0):,.2f}"},
                    {"type": "mrkdwn", "text": f"*Revenue Won:* ${record.get('AmountWonOpportunities', 0):,.2f}"},
                    {"type": "mrkdwn", "text": f"*ROI:* {roi:.1f}%"},
                    {"type": "mrkdwn", "text": f"*Conversion Rate:* {conversion_rate:.1f}%"},
                    {"type": "mrkdwn", "text": f"*Leads:* {record.get('NumberOfLeads', 0)}"},
                    {"type": "mrkdwn", "text": f"*Opportunities:* {record.get('NumberOfOpportunities', 0)}"}
                ]
            }
            response_blocks.append(campaign_block)
            response_blocks.append({"type": "divider"})
        
        respond(blocks=response_blocks)
        
    except Exception as e:
        logger.error(f"Campaign query error: {e}")
        respond(f"Error retrieving campaign data: {str(e)}")

# Data Quality Monitoring
@app.command("/dq-scan")
def data_quality_scan(ack, respond, command):
    """Perform data quality scan on Salesforce data"""
    ack()
    
    sf = get_salesforce_connection()
    if not sf:
        respond("❌ Unable to connect to Salesforce")
        return
    
    try:
        respond("🔍 Starting data quality scan...")
        
        quality_issues = []
        
        # Check Accounts for data quality
        account_query = """
        SELECT Id, Name, Phone, BillingStreet, BillingCity, 
               BillingState, BillingPostalCode, AnnualRevenue
        FROM Account 
        WHERE CreatedDate = LAST_N_DAYS:30
        LIMIT 1000
        """
        
        account_data = sf.query_all(account_query)
        if account_data['records']:
            df_accounts = pd.DataFrame(account_data['records'])
            
            # Check for missing critical fields
            missing_phone = df_accounts['Phone'].isna().sum()
            missing_address = df_accounts['BillingStreet'].isna().sum()
            
            # Check for revenue anomalies using Z-score
            if 'AnnualRevenue' in df_accounts.columns:
                revenues = pd.to_numeric(df_accounts['AnnualRevenue'], errors='coerce').dropna()
                if len(revenues) > 10:
                    z_scores = np.abs(stats.zscore(revenues))
                    revenue_anomalies = (z_scores > 3).sum()
                    quality_issues.append(f"Revenue Anomalies: {revenue_anomalies} accounts with unusual revenue values")
            
            quality_issues.append(f"Missing Phone Numbers: {missing_phone} accounts")
            quality_issues.append(f"Missing Addresses: {missing_address} accounts")
        
        # Check Opportunities for data quality
        opp_query = """
        SELECT Id, Name, Amount, CloseDate, StageName, Probability
        FROM Opportunity 
        WHERE CreatedDate = LAST_N_DAYS:30
        LIMIT 1000
        """
        
        opp_data = sf.query_all(opp_query)
        if opp_data['records']:
            df_opps = pd.DataFrame(opp_data['records'])
            
            # Check for amount anomalies
            if 'Amount' in df_opps.columns:
                amounts = pd.to_numeric(df_opps['Amount'], errors='coerce').dropna()
                if len(amounts) > 10:
                    z_scores = np.abs(stats.zscore(amounts))
                    amount_anomalies = (z_scores > 3).sum()
                    quality_issues.append(f"💵 Opportunity Amount Anomalies: {amount_anomalies} opportunities")
            
            # Check for missing close dates
            missing_close_dates = df_opps['CloseDate'].isna().sum()
            quality_issues.append(f"📅 Missing Close Dates: {missing_close_dates} opportunities")
        
        # Format and send results
        if quality_issues:
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🚨 Data Quality Scan Results"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "\\n".join([f"• {issue}" for issue in quality_issues])}
                }
            ]
            
            # Calculate overall data quality score
            total_issues = sum([int(issue.split(':')[1].split()[0]) for issue in quality_issues if ':' in issue])
            total_records = len(account_data.get('records', [])) + len(opp_data.get('records', []))
            quality_score = max(0, 100 - (total_issues / total_records * 100)) if total_records > 0 else 100
            
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Overall Data Quality Score:* {quality_score:.1f}%"}
            })
            
            respond(blocks=blocks)
        else:
            respond("No data quality issues detected!")
            
    except Exception as e:
        logger.error(f"Data quality scan error: {e}")
        respond(f"Error during data quality scan: {str(e)}")

# Help Command
@app.command("/omni-help")
def help_command(ack, respond, command):
    """Show available commands"""
    ack()
    
    help_blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🤖 OmniInsights Help"}
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Available Commands:*\\n"
                        "• `/campaign <name>` - Get campaign analytics\\n"
                        "• `/dq-scan` - Run data quality scan\\n"
                        "• `/omni-help` - Show this help message"
            }
        }
    ]
    
    respond(blocks=help_blocks)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
