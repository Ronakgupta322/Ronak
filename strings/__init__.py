import os
from typing import List

import yaml

languages = {}
languages_present = {}


def get_string(lang: str):
    return languages.get(lang, languages.get("en", {}))


LANGS_DIR = "./strings/langs"


# English pehle load karo
en_file = os.path.join(LANGS_DIR, "en.yml")
if os.path.isfile(en_file):
    with open(en_file, encoding="utf8") as f:
        languages["en"] = yaml.safe_load(f) or {}
    languages_present["en"] = languages["en"].get("name", "English")
else:
    print("Warning: en.yml not found inside strings/langs")
    languages["en"] = {"name": "English"}
    languages_present["en"] = "English"


# Baaki language files load karo
if os.path.isdir(LANGS_DIR):
    for filename in os.listdir(LANGS_DIR):
        if not filename.endswith(".yml"):
            continue

        language_name = filename[:-4]

        if language_name == "en":
            continue

        file_path = os.path.join(LANGS_DIR, filename)

        try:
            with open(file_path, encoding="utf8") as f:
                data = yaml.safe_load(f) or {}

            # Missing keys ko English se fill karo
            for item in languages["en"]:
                if item not in data:
                    data[item] = languages["en"][item]

            languages[language_name] = data
            languages_present[language_name] = data.get("name", language_name)

        except Exception as e:
            print(f"Failed to load language file {filename}: {e}")
            continue
else:
    print("Warning: strings/langs directory not found.")
