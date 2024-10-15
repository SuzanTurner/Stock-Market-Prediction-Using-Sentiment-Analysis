import requests
from textblob import TextBlob
import yfinance as yf
from datetime import datetime, timedelta

def fetch_stock_news(stock_symbol, api_key):
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&language=en&sortBy=publishedAt&pageSize=10&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['articles']
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []
        
def analyze_sentiment(articles):
    total_polarity = 0
    for article in articles:
        content = article['title'] + '. ' + article['description'] if article['description'] else article['title']
        blob = TextBlob(content)
        total_polarity += blob.sentiment.polarity

    avg_polarity = total_polarity / len(articles) if articles else 0
    return avg_polarity

def should_invest(sentiment_score):
    if sentiment_score > 0.5:
        return "Positive sentiment detected. It is a great time to invest!"
    elif sentiment_score > 0.1:
        return "Postive sentiment detected. It might be a good time to invest."
    elif sentiment_score <= 0.1:
        return "Neutral sentiment detected. Consider other factors before investing"
    else:
        return "Negetive sentiment detected. It is a bad time to invest"

def predict_stock_movement(stock_symbol, sentiment_score):
    stock = yf.Ticker(stock_symbol)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    historical_hourly_data = stock.history(interval="1h", start=start_date, end=end_date)
    historical_daily_data = stock.history(interval="1d", start=start_date, end=end_date)

    if historical_hourly_data.empty or historical_daily_data.empty:
        return "Not enough historical data to make predictions."

    recent_hour_close = historical_hourly_data['Close'].values[-1]  # Most recent hourly closing price
    two_hours_ago_close = historical_hourly_data['Close'].values[-3]  # Closing price 2 hours ago

    recent_day_close = historical_daily_data['Close'].values[-1]  # Most recent daily closing price
    yesterday_close = historical_daily_data['Close'].values[-2]  # Closing price yesterday

    week_ago_close = historical_daily_data['Close'].values[0]  # Closing price a week ago

    hourly_prediction = ""
    daily_prediction = ""
    weekly_prediction = ""
    
    if sentiment_score > 0.1 and recent_hour_close > two_hours_ago_close:
        hourly_prediction = "Stock is likely to rise in the next few hours."
    elif sentiment_score < -0.1 and recent_hour_close < two_hours_ago_close:
        hourly_prediction = "Stock is likely to fall in the next few hours."
    else:
        hourly_prediction = "Neutral hourly trend. Expect minor fluctuations."

    if sentiment_score > 0.1 and recent_day_close > yesterday_close:
        daily_prediction = "Stock is likely to rise tomorrow."
    elif sentiment_score < -0.1 and recent_day_close < yesterday_close:
        daily_prediction = "Stock is likely to fall tomorrow."
    else:
        daily_prediction = "Neutral daily trend. Stock may fluctuate or stay stable tomorrow."

    if sentiment_score > 0.1 and recent_day_close > week_ago_close:
        weekly_prediction = "Stock is likely to rise this week."
    elif sentiment_score < -0.1 and recent_day_close < week_ago_close:
        weekly_prediction = "Stock is likely to fall this week."
    else:
        weekly_prediction = "Neutral weekly trend. Stock may remain stable or fluctuate slightly."

    return hourly_prediction, daily_prediction, weekly_prediction

def main():
    stock_symbol = input("Enter the stock symbol: ").upper()
    api_key = "e42e1415bc8e4c4e9dea2415073ee37d"  # Your API key here
    
    print(f"Fetching news for {stock_symbol}...")
    articles = fetch_stock_news(stock_symbol, api_key)
    
    if not articles:
        print(f"No news found for {stock_symbol}.")
        return
    
    print(f"Analyzing sentiment for {stock_symbol}...")
    sentiment_score = analyze_sentiment(articles)
    investment_advice = should_invest(sentiment_score)
    hourly_prediction, daily_prediction, weekly_prediction = predict_stock_movement(stock_symbol, sentiment_score)
    
    print(f"Sentiment score: {sentiment_score}")
    print(investment_advice)
    print(f"\nHourly Prediction: {hourly_prediction}")
    print(f"Daily Prediction: {daily_prediction}")
    print(f"Weekly Prediction: {weekly_prediction}")

if __name__ == "__main__":
    main()