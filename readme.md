This a Kurdish Kurmanji words tagger for [klpt](https://pypi.org/project/klpt/)

How it works?

1. It downloads words from klpt
2. It save downloaded words to db
3. It iterate over input file words and check if it is in db
4. If it is not it tags and save it to output file

Note: Now It only tags noun and adjective words

How to use it?

```py
from tagger import WordTagger

WordTagger.download_words()
WordTagger("input.txt", "output.txt").tag()

```
