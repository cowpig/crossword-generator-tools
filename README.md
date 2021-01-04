# crossword-generator-tools
Some tools I wrote for building crossword puzzles:

`themefinder.py`

Takes a list of themed answers (or unthemed, whatever floats your boat) and returns all subsets which can be crisscrossed in a 15x15 grid, like this:

```raw
     F
     F
 BBBXZBBYBBW
     F     G
     F     G
     F     G
     F     G
     F     G
     F     G
     F     G
     F     G
     F     G
     UHHHHHZHHHH
           G
           G
```

`generate_wordlist.py`

Uses four sources of word lists that I found online, and then combines them into four answer dictionaries, ranging from "fair" to "best". The ranking is based on my subjective opinion, but my goals were to choose recognizeable lemmas that can be clued creatively, and avoid crosswordese as much as possible.

I use the output with [Kevin](https://github.com/dnapoleoni/Kevin), an open-source fork of [Phil](https://github.com/keiranking/Phil), two browser-based crossword building apps with autofill that can use whatever wordlist/dictionary you provide.
