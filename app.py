from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# Path to dataset folder
dataset_dir = os.path.join(os.path.dirname(__file__), 'dataset')

# Load datasets
def load_datasets():
    datasets = {}
    for file_name in os.listdir(dataset_dir):
        if file_name.endswith('.csv'):
            company_name = file_name.split('.')[0].lower()  # Extract name from filename
            file_path = os.path.join(dataset_dir, file_name)
            df = pd.read_csv(file_path)
            datasets[company_name] = df
    return datasets

datasets = load_datasets()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()

    # Respond to user commands
    if 'hello' in user_message:
        return jsonify({"response": "Hello! I can help you with stock data. Ask about companies, investments,buy, sell, hold or recommendations."})
    
    elif 'recommend' in user_message:  # Handle recommendations directly
        return jsonify(get_recommendations())

    elif any(action in user_message for action in ['buy', 'sell', 'hold']):
        company_name = extract_company_name(user_message)
        if not company_name:
            return jsonify({"response": "Please specify a valid company name for trading actions."})
        return jsonify(get_trading_action(company_name, user_message))
    
    elif 'companies' in user_message:
        company_names = ', '.join(datasets.keys())
        return jsonify({"response": f"I have data for these companies: {company_names}"})
    
    elif 'stock' in user_message:
        company_name = extract_company_name(user_message)
        if not company_name:
            return jsonify({"response": "Please specify a company name."})
        return jsonify(get_stock_summary(company_name))
    
    elif 'correlation' in user_message:
        company_name = extract_company_name(user_message)
        if not company_name:
            return jsonify({"response": "Please specify a company name for correlation analysis."})
        return jsonify(get_correlation_info(company_name))
    
    else:
        return jsonify({"response": "Sorry, I didn't understand that. Please try asking about stock performance, recommendations, or trading actions (Buy, Sell, Hold)."})

# Extract company name from the user's message
def extract_company_name(message):
    for company in datasets.keys():
        if company in message:
            return company
    return None

# Get stock summary
def get_stock_summary(company_name):
    if company_name not in datasets:
        return {"response": f"I don't have data for {company_name}."}
    
    company_data = datasets[company_name]
    if 'Close' in company_data.columns:
        latest_close = company_data['Close'].iloc[-1]
        high_price = company_data['High'].max()
        low_price = company_data['Low'].min()
        total_volume = company_data['Volume'].sum()

        return {"response": (f"Stock Summary for {company_name}:\n"
                             f"Latest Close Price: ${latest_close:.2f}\n"
                             f"Highest Price: ${high_price:.2f}\n"
                             f"Lowest Price: ${low_price:.2f}\n"
                             f"Total Trading Volume: {total_volume} shares")}
    else:
        return {"response": f"Data for {company_name} is incomplete."}

# Generate recommendations
def get_recommendations():
    if not datasets:  # Check if datasets are loaded
        return {"response": "No datasets available to generate recommendations."}
    
    recommendations = []
    for company, data in datasets.items():
        if 'Close' in data.columns and 'Open' in data.columns:
            avg_return = data['Close'].mean() - data['Open'].mean()
            if avg_return > 5:  # Example threshold for recommendation
                recommendations.append(company)
    
    if recommendations:
        return {"response": f"Recommended stocks based on performance: {', '.join(recommendations)}"}
    else:
        # Return all available companies if no specific recommendation
        company_names = ', '.join(datasets.keys())
        return {"response": f"Recommended stocks for potential trading: tsla, amd, mtdr.Here are the available companies: {company_names}"}

# Get trading action (Buy, Sell, Hold)
def get_trading_action(company_name, user_message):
    if company_name not in datasets:
        return {"response": f"I don't have data for {company_name}."}
    
    company_data = datasets[company_name]
    if 'Close' in company_data.columns:
        latest_close = company_data['Close'].iloc[-1]

        if 'buy' in user_message:
            return {"response": f"You could consider BUYING {company_name}. The latest closing price is ${latest_close:.2f}."}
        elif 'sell' in user_message:
            return {"response": f"You could consider SELLING {company_name}. The latest closing price is ${latest_close:.2f}."}
        elif 'hold' in user_message:
            return {"response": f"It might be wise to HOLD {company_name} for now. The latest closing price is ${latest_close:.2f}."}
    return {"response": f"Data for {company_name} is incomplete for trading actions."}

# Get correlation between Close and Volume
def get_correlation_info(company_name):
    if company_name not in datasets:
        return {"response": f"I don't have data for {company_name}."}
    
    company_data = datasets[company_name]
    if 'Close' in company_data.columns and 'Volume' in company_data.columns:
        correlation = company_data['Close'].corr(company_data['Volume'])
        return {"response": f"The correlation between {company_name}'s closing price and trading volume is {correlation:.2f}."}
    else:
        return {"response": f"Data for {company_name} is missing required columns ('Close' and 'Volume')."}

if __name__ == '__main__':
    app.run(debug=True)
