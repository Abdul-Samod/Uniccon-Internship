import pandas as pd
import html

# Inspecting the dataset
df = pd.read_csv("data/raw/english_sentences.csv")

# Inspecting the dataset
print (df.head())
print (df.tail())
print ("Shape:", df.shape)
print (df.info())
print (df.describe())

# Rename columns to make them more readable
df = df.rename(columns={
    "sentence": "english_sentence",
    "source": "source_name"
})

# Checking the changes
print(df.head())

# Fixing text and encoding
df["english_sentence"] = df["english_sentence"].str.strip()
df["english_sentence"] = df["english_sentence"].str.replace(r"\s+", " ", regex=True)

df["source_name"] = df["source_name"].str.strip()
df["source_name"] = df["source_name"].str.replace(r"\s+", " ", regex=True)

# Checking the changes
print(df.head(10))    

# Check number of duplicates
print("Duplicate rows:", df.duplicated().sum())

print(df[df.duplicated()].head(9))

# Removing duplicates
df = df.drop_duplicates(subset=["english_sentence"])

# Check again
print("After removing duplicates, shape:", df.shape)

# Checking for HTML entities
entities_left = df[df["english_sentence"].str.contains(r"&[^ ]+;|&#\d+;", regex=True)]
print(f"Entities left: {len(entities_left)}")
entities_left.head(10)

# Saving the cleaned dataset
df.to_csv("english_sentences-cleaned.csv", index=False)
