import os
import json
import pandas as pd
import requests
from io import StringIO

# If datasets import causes issues for JW300, wrap usage
from datasets import load_dataset, DatasetDict, Dataset
from datasets import logging as hf_logging

hf_logging.set_verbosity_error()  # suppress benign HF warnings

AGRI_KEYWORDS = [
    "oko", "ogbin", "irugbin", "eweko",
    "ogbin ogba", "eran", "ewure", "agutan",
    "maalu", "agbe", "oko nla", "ise agbe",
    "irin ajo oko", "agriculture", "farm",
    "farming", "crop", "livestock"
]

def contains_agriculture(text: str) -> bool:
    if not isinstance(text, str):
        return False
    tl = text.lower()
    return any(kw in tl for kw in AGRI_KEYWORDS)

def load_menyo():
    base_url = "https://raw.githubusercontent.com/uds-lsv/menyo-20k_MT/master/data"
    splits = ["train.tsv", "dev.tsv", "test.tsv"]
    frames = []
    for split in splits:
        url = f"{base_url}/{split}"
        print(f"Downloading MENYO split: {split} from {url} ...")
        r = requests.get(url)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text), sep="\t")
        frames.append(df)
    df_all = pd.concat(frames, ignore_index=True)
    print(f"MENYO-20k total rows: {len(df_all)}")
    if "Yoruba" not in df_all.columns or "English" not in df_all.columns:
        print("❌ MENYO format unexpected; columns:", df_all.columns)
        return pd.DataFrame(columns=["yoruba", "english"])
    df_all = df_all[["Yoruba", "English"]].rename(columns={"Yoruba": "yoruba", "English": "english"})
    return df_all

def load_jw300():
    """Attempt to load JW300 via HF with several possible identifiers."""
    candidates = ["jw300", "jw300_en-yo", "jhu/jw300", "Masakhane/jw300-yo-en"]
    for candidate in candidates:
        try:
            print(f"Trying to load JW300 via identifier: {candidate}")
            ds = load_dataset(candidate, split="train")
            # check structure: needs translation or columns with Yoruba & English
            df = ds.to_pandas()
            # Case 1: 'translation' column
            if "translation" in df.columns:
                df2 = df[df["translation"].apply(lambda x: isinstance(x, dict) and "yo" in x and "en" in x)]
                df2 = df2.rename(columns={"translation": "pair"})
                df_good = pd.DataFrame({
                    "yoruba": df2["pair"].apply(lambda x: x["yo"]),
                    "english": df2["pair"].apply(lambda x: x["en"])
                })
                print(f"✅ Loaded JW300 via {candidate}, rows: {len(df_good)}")
                return df_good
            # Case 2: separate 'yo' and 'en' columns
            if "yo" in df.columns and "en" in df.columns:
                df_good = df.rename(columns={"yo": "yoruba", "en": "english"})
                df_good = df_good[["yoruba", "english"]].dropna()
                print(f"✅ Loaded JW300 via {candidate}, rows: {len(df_good)}")
                return df_good

            # Otherwise wrong format, continue to next candidate
        except Exception as e:
            print(f"❌ Failed loading JW300 via {candidate}: {e}")

    # If all attempts fail:
    print("⚠️ JW300 could not be loaded via any candidate identifier.")
    return pd.DataFrame(columns=["yoruba", "english"])

def main():
    # Output folder
    output_dir = os.path.join(os.path.dirname(__file__), "..", "02_agri_filtered")
    os.makedirs(output_dir, exist_ok=True)

    # Load MENYO
    df_menyo = load_menyo()

    # Load JW300
    df_jw300 = load_jw300()

    # Merge
    df_all = pd.concat([df_menyo, df_jw300], ignore_index=True)
    print(f"Combined total rows before filtering: {len(df_all)}")

    # Filter for agriculture
    df_agri = df_all[
        df_all["yoruba"].apply(contains_agriculture) |
        df_all["english"].apply(contains_agriculture)
    ]
    print(f"✅ Agriculture-related rows: {len(df_agri)}")

    # Save outputs
    csv_path = os.path.join(output_dir, "yoruba_agriculture_dataset.csv")
    df_agri.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print("Saved CSV:", csv_path)

    excel_path = os.path.join(output_dir, "yoruba_agriculture_dataset.xlsx")
    df_agri.to_excel(excel_path, index=False, engine="openpyxl")
    print("Saved Excel:", excel_path)

    jsonl_path = os.path.join(output_dir, "yoruba_agriculture_dataset.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for _, row in df_agri.iterrows():
            rec = {"yoruba": row["yoruba"], "english": row["english"]}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("Saved JSONL:", jsonl_path)

    print("✅ Done.")

if __name__ == "__main__":
    main()
