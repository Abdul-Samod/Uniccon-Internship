import pandas as pd
import re

# Load the dataset
df = pd.read_csv("train -new.csv")

# Extract only Yoruba sentences
yoruba_sentences = df["yo"].dropna()  # drop NaN if any

# Split sentences by ".", "?", "!" and flatten into one list
sentences = []
for text in yoruba_sentences:
    parts = [s.strip() for s in re.split(r"[.!?]", str(text)) if s.strip()]
    sentences.extend(parts)

# Convert into DataFrame
yoruba_df = pd.DataFrame(sentences, columns=["yoruba_sentence"])

# Save to Excel
yoruba_df.to_excel("yoruba_sentences-split.xlsx", index=False)

print("✅ Yoruba sentences split and saved successfully!")


