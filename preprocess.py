import pandas as pd

# Path to the input and output CSV files
input_file = "data/products.csv"  # Adjust this to the actual path of your file
output_file = "data/processed/products.csv"

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(input_file)

# Remove double quotes from all string columns
df = df.applymap(lambda x: x.replace('"', '') if isinstance(x, str) else x)

# Save the cleaned DataFrame back to a new CSV file
df.to_csv(output_file, index=False)

print(f"Cleaned data saved to {output_file}")
