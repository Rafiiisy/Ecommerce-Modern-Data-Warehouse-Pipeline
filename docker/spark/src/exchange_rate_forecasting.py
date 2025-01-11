from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from datetime import datetime
from functools import reduce
import time


def forecast_currency(spark, currency_df, min_date, currency):
    """
    Train a Linear Regression model and forecast the next 30 days for the given currency.
    """
    # Assemble features for the model
    assembler = VectorAssembler(inputCols=["days_since_start"], outputCol="features")
    currency_df = assembler.transform(currency_df).select("features", F.col("rate").alias("label"), "days_since_start")

    # Train Linear Regression model
    lr = LinearRegression(featuresCol="features", labelCol="label")
    model = lr.fit(currency_df)

    # Prepare future DataFrame
    max_days = int(currency_df.agg(F.max("days_since_start")).collect()[0][0])
    future_dates = [(max_days + i) for i in range(0, 30)]  # Include last date in the forecast
    future_df = spark.createDataFrame(future_dates, IntegerType()).toDF("days_since_start")

    # Apply VectorAssembler to future_df to create the features column
    future_df = assembler.transform(future_df)

    # Predict future rates
    forecast = model.transform(future_df)
    forecast = forecast.withColumn("prediction", F.col("prediction").cast("double"))  # Explicitly cast to double
    forecast = forecast.withColumn("date", F.expr(f"date_add('{min_date}', days_since_start)"))

    return forecast.select("date", F.lit(currency).alias("currency"), F.col("prediction").alias("forecasted_rate"))


def main():
    spark = SparkSession.builder \
        .appName("ExchangeRateForecast") \
        .config("spark.sql.catalogImplementation", "hive") \
        .enableHiveSupport() \
        .getOrCreate()

    while True:
        try:
            # Define HDFS base path
            base_hdfs_path = "hdfs://namenode:9820/user/hive/warehouse/exchange_rates"
            hdfs_input_path = f"{base_hdfs_path}"

            # Load the data
            df = spark.read.parquet(hdfs_input_path)
            if df.rdd.isEmpty():
                print("No data available. Skipping...")
                time.sleep(86400)
                continue

            # Convert string columns to proper types for calculation
            df = df.withColumn("date", F.to_date("date", "yyyy-MM-dd"))
            df = df.withColumn("timestamp", F.to_timestamp("timestamp"))

            # Prepare data for forecasting
            df = df.select("currency", "rate", "timestamp", "date")
            min_date = df.agg(F.min("date")).collect()[0][0]
            df = df.withColumn("days_since_start", F.datediff(F.col("date"), F.lit(min_date)).cast(IntegerType()))

            # Forecasting for each currency
            currencies = [row.currency for row in df.select("currency").distinct().collect()]
            forecasts = [forecast_currency(spark, df.filter(F.col("currency") == currency), min_date, currency) for currency in currencies]

            # Combine forecasts
            if forecasts:
                forecast_result = reduce(lambda df1, df2: df1.union(df2), forecasts)

                # Convert 'date' back to string for Hive compatibility
                forecast_result = forecast_result.withColumn("date", F.col("date").cast("string"))

                # Use a temporary directory to avoid overwrite conflicts
                temp_output_path = "hdfs://namenode:9820/user/hive/warehouse/temp_forecast_outputs"
                final_output_path = "hdfs://namenode:9820/user/hive/warehouse/forecast_outputs"

                # Write forecast to a temporary directory
                forecast_result.write \
                    .mode("overwrite") \
                    .parquet(temp_output_path)

                print("Forecast data saved to temporary HDFS location.")

                # Move temporary data to the final directory
                fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
                temp_path = spark._jvm.org.apache.hadoop.fs.Path(temp_output_path)
                final_path = spark._jvm.org.apache.hadoop.fs.Path(final_output_path)

                # Delete the final directory if it exists
                if fs.exists(final_path):
                    fs.delete(final_path, True)

                # Move temp directory to the final location
                fs.rename(temp_path, final_path)

                print("Forecast data moved to final HDFS location.")

                # Update Hive table
                forecast_data = spark.read.parquet(final_output_path)

                # Ensure consistency with Hive table schema
                forecast_data = forecast_data.withColumn("date", F.col("date").cast("string")) \
                     .withColumn("forecasted_rate", F.col("forecasted_rate").cast("double"))

                # Write to Hive table
                forecast_data.write.mode("overwrite").insertInto("forecast_outputs")

                print("Hive table updated successfully with new data from HDFS.")
            else:
                print("No forecast data generated.")

        except Exception as e:
            print(f"Error in forecasting process: {e}")

        print("Waiting 24 hours before the next forecast...")
        time.sleep(86400)


if __name__ == "__main__":
    main()
