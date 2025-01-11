import pandas as pd

# Define the input and output file paths
# parquet_file = "data/productCust_data_cleaned.csv"
csv_file = "data/processed/products.csv"

# Load the Parquet file into a Pandas DataFrame
df = pd.read_csv(csv_file).head(2)

# Print column names and data types
print("Column Data Types:")
print(df.dtypes)

# # Save the DataFrame to a CSV file
# df.to_csv(csv_file, index=False)

# # Print the contents of the CSV
# print("Converted CSV:")
# print(df)
