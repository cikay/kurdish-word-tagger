from tagger import WordTagger

WordTagger.download_words()
WordTagger("words.txt", "output.txt").tag()
