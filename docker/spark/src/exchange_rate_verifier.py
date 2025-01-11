from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import requests
from datetime import datetime
import time

def create_spark_session():
    return SparkSession.builder \
        .appName("ExchangeRateVerifier") \
        .config("spark.sql.catalogImplementation", "hive") \
        .enableHiveSupport() \
        .getOrCreate()

def fetch_with_retry(url, retries=3, backoff=5):
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
    raise Exception("Failed to fetch data after multiple attempts.")

def check_hive_data(spark):
    try:
        print("\nChecking Hive Data:")
        # Read from Hive table
        df = spark.sql("SELECT * FROM exchange_rates")
        
        # Get basic stats
        total_records = df.count()
        unique_dates = df.select("date").distinct().count()
        unique_currencies = df.select("currency").distinct().count()
        
        print(f"Total records in Hive: {total_records}")
        print(f"Unique dates: {unique_dates}")
        print(f"Unique currencies: {unique_currencies}")
        
        # Show latest data
        print("\nLatest Exchange Rates in Hive:")
        df.orderBy(desc("timestamp")).select(
            "currency", "rate", "timestamp"
        ).show(5)
        
        return df
    except Exception as e:
        print(f"Error reading Hive data: {e}")
        return None

def compare_data(api_data, hive_df):
    print("\nComparing API vs Hive data:")
    
    if hive_df is None:
        print("No Hive data available for comparison")
        return
    
    # Get latest rates from Hive
    latest_rates = hive_df.orderBy(desc("timestamp")) \
        .dropDuplicates(["currency"]) \
        .collect()
    
    hive_rates = {row.currency: row.rate for row in latest_rates}
    api_rates = api_data['conversion_rates']
    
    # Compare major currencies
    major_currencies = ['EUR', 'GBP', 'JPY', 'IDR', 'SGD']
    print("\nComparison for major currencies:")
    print("Currency | API Rate | Hive Rate | Difference")
    print("-" * 50)
    
    for curr in major_currencies:
        api_rate = api_rates.get(curr, 0)
        hive_rate = hive_rates.get(curr, 0)
        diff = abs(api_rate - hive_rate) if api_rate and hive_rate else 0
        print(f"{curr:8} | {api_rate:8.4f} | {hive_rate:9.4f} | {diff:9.4f}")

def main():
    print(f"Starting Data Verification at {datetime.now()}")
    spark = create_spark_session()
    
    try:
        # Fetch API data
        url = "https://v6.exchangerate-api.com/v6/d859a94bdc40c124d4842d22/latest/USD"
        api_data = fetch_with_retry(url)
        
        # Check Hive data
        hive_df = check_hive_data(spark)
        
        # Compare API data with Hive data
        compare_data(api_data, hive_df)
        
    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
