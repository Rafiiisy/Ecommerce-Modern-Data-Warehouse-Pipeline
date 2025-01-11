from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import requests
from datetime import datetime
import time

def create_spark_session():
    """Create a Spark session with Hive support enabled."""
    return SparkSession.builder \
        .appName("ExchangeRateETL") \
        .config("spark.sql.catalogImplementation", "hive") \
        .enableHiveSupport() \
        .getOrCreate()

def fetch_exchange_rates():
    """Fetch exchange rate data from the API."""
    try:
        url = "https://openexchangerates.org/api/latest.json?app_id=cb24f865600248ad942811c72bbe3429&base=USD&symbols=IDR&prettyprint=false&show_alternative=false"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant information
        rate = data["rates"]["IDR"]
        timestamp = data["timestamp"]
        return {"currency": "IDR", "rate": rate, "timestamp": timestamp}
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return None

def process_and_save_to_hive(spark, data):
    """Process and save the exchange rate data to Hive."""
    if not data:
        print("No data to process.")
        return False
    
    try:
        # Convert timestamp to datetime
        timestamp_dt = datetime.fromtimestamp(data['timestamp'])
        
        # Create a DataFrame row
        row = {
            'currency': data['currency'],
            'rate': float(data['rate']),
            'timestamp': str(datetime.fromtimestamp(data['timestamp'])),
            'date': str(datetime.fromtimestamp(data['timestamp']).date())
        }
        
        # Define schema
        schema = StructType([
            StructField("currency", StringType(), True),
            StructField("rate", DoubleType(), True),
            StructField("timestamp", StringType(), True),
            StructField("date", StringType(), True)
        ])
        
        # Create DataFrame
        df = spark.createDataFrame([row], schema)
        
        # Display the data to be saved
        print("\nData to be saved to Hive:")
        df.show()
        
        # Write to Hive table
        df.write.mode("append").insertInto("default.exchange_rates")
        print("Data successfully written to Hive table: exchange_rates")
        
        return True
        
    except Exception as e:
        print(f"Error processing and saving data to Hive: {e}")
        return False

def main():
    print(f"Starting Exchange Rate ETL at {datetime.now()}")
    
    try:
        # Create Spark Session
        spark = create_spark_session()
        print("Spark session created successfully")
        
        while True:
            try:
                # Step 1: Fetch Data
                print("Fetching exchange rates...")
                data = fetch_exchange_rates()
                
                # Step 2: Process & Save Data to Hive
                print("Processing and saving data to Hive...")
                success = process_and_save_to_hive(spark, data)
                
                if success:
                    print("ETL cycle completed successfully")
                else:
                    print("ETL cycle failed")
                
                # Wait for an hour before the next cycle
                wait_time = 3600  # 1 hour
                print(f"Waiting {wait_time} seconds before the next cycle...")
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"Error in ETL cycle: {e}")
                print("Retrying in 5 minutes...")
                time.sleep(300)  # 5 minutes
                
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        if 'spark' in locals():
            spark.stop()
            print("Spark session stopped")

if __name__ == "__main__":
    main()
