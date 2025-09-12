import pandas as pd
from deep_translator import GoogleTranslator

# Read the dataset
df = pd.read_csv("yoruba_health.csv")

# Create translator instance
translator = GoogleTranslator(source="yo", target="en")

# Translate Yoruba to English
def safe_translate(text):
    try:
        if pd.isnull(text) or str(text).strip() == "":
            return ""
        return translator.translate(text)
    except Exception as e:
        print(f"Translation failed for: {text[:30]}... | Error: {e}")
        return text  # fallback: keep Yoruba text

# Add translation columns
df["title_translation"] = df["title"].apply(safe_translate)
df["content_translation"] = df["content"].apply(safe_translate)

# Save results to new CSV
df.to_csv("yoruba_health_translated.csv", index=False, encoding="utf-8-sig")

print("Translation complete! Saved as yoruba_health_translated.csv")
