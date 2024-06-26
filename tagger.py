import requests
import time
import sqlite3


def initialize_db():
    conn = sqlite3.connect("words.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS words
                 (word TEXT PRIMARY KEY, details TEXT)"""
    )
    conn.commit()
    conn.close()


def is_word_in_db(word):
    conn = sqlite3.connect("words.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM words WHERE word=?", (word,))
    result = c.fetchone()
    conn.close()
    return result is not None


def add_word_to_db(word):
    conn = sqlite3.connect("words.db")
    c = conn.cursor()
    c.execute("INSERT INTO words (word) VALUES (?)", (word,))
    conn.commit()
    conn.close()


def write_to_file(words, file):
    for word in words:
        print(word)
        if not is_word_in_db(word):
            file.write(f"{word}\n")


class WordTagger:
    url_template = "https://ku.wiktionary.org/w/api.php?action=query&format=json&titles={}&prop=revisions&rvprop=content&rvslots=main"

    existing_word_file = "existing_words.txt"

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    @classmethod
    def download_words(cls):
        url = "https://github.com/sinaahmadi/KurdishHunspell/raw/main/kmr/kmr-Latn.dic"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(cls.existing_word_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print("File downloaded successfully.")
        else:
            print("Failed to download file. Status code:", response.status_code)

    def save_existing_words(self):
        initialize_db()
        with open(self.existing_word_file, "r") as f:
            for line in f:
                word = line.split("/")[0].strip()
                if not is_word_in_db(word):
                    print(f"add the word {word} to db")
                    add_word_to_db(word)

    def tag(self):
        self.save_existing_words()
        words = self._read_input_words()
        with open(self.output_file, "w") as output_file:
            for word in words:

                if is_word_in_db(word):
                    continue

                if " " in word:
                    continue

                content = self._get_word_content(word)
                if content == "":
                    continue

                if "ziman|ku" not in content:
                    continue

                kurmanji_tag = ""
                universal_tag = ""
                if "=== Rengdêr ===" in content:
                    kurmanji_tag = "A"
                    universal_tag = "po:adj"
                    if "=== Navdêr ===" in content:
                        noun_tag, _ = self._get_noun_tag(content)
                        kurmanji_tag += noun_tag
                elif "=== Navdêr ===" in content:
                    kurmanji_tag, universal_tag = self._get_noun_tag(content)

                if kurmanji_tag == "":
                    continue

                tagged_word = f"{word}/{kurmanji_tag} {universal_tag}"
                output_file.write(f"{tagged_word}\n")
                print(tagged_word)
                time.sleep(1)

    def _get_noun_tag(self, content):
        if "nêr}}" in content:
            return "M", "po:noun_masc"
        elif "mê}}" in content:
            return "F", "po:noun_fem"

        return "N", "po:noun"

    def _read_existing_words(self):
        with open(self.existing_word_file, "r") as f:
            for line in f:
                word = line.strip()
                yield word

    def _read_input_words(self):
        with open(self.input_file, "r") as f:
            for line in f:
                word = line.strip()
                yield word

    def _get_word_content(self, word):
        url = self.url_template.format(word)
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to get word info")

        data = response.json()
        if "-1" in data["query"]["pages"]:
            return ""

        page = list(data["query"]["pages"].values())[0]
        return page["revisions"][0]["slots"]["main"]["*"]
