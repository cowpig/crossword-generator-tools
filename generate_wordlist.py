from statistics import median, mean
import re

overrides_good = '''
ABE
DIN
ELF
NPR
SSL
HOG
WOO
LEN
IPS
BON
MLB
NUM
XXX
VOD
REC
PAW
JEN
SEN
ALS
ERR
ORE
HEM
SCH
SYS
SUV
STR
TAR
SOL
GEL
EOS
ABB
ALG
XYY
EWW
XXY
KFC
DRJ
FEU
RYU
OYS
UMP
UZI
LOX
OVO
XYZ
DEW
DAY
CVS
GIG
HAM
GIA
HOW
AND
OWL
HUH
SEW
IVY
DEV
DIV
'''

overrides_meh = '''
CUS
AJO
AOK
BBW
MYA
RFK
NME
AUK
KHI
DNC
EYING
BARRON
BARRIE
'''

# first list gives scores directly, and is
#   based on crosswordese
with open("./wordlist_sources/crossword_wordlist_scored.txt", 'r') as f: 
    cross_raw = f.readlines()

# second list is based in google searches so it's more
#   realistic, but also kind of all over the place.
#   we'll calc a score based on the order:
#   3-4 letter words will be high-rated early and then drop
#   5-letter words will start dropping after 10k
#   every 6+ letter word will be rated 50
with open("./wordlist_sources/30k-eng-word-freq.txt", 'r') as f:
    freq_raw = f.readlines()

# third list is a compilation of lemmas :
#   http://corpus.leeds.ac.uk/list.html
# and seems to be the most realistic
with open("./wordlist_sources/lemmas_by_freq.txt", 'r') as f:
    lemma_raw = f.readlines()

# the final list is based on a study:
#   https://www.researchgate.net/project/Word-prevalence-measures-for-62K-English-lemmas
with open("./wordlist_sources/word_prevalences.tsv", 'r') as f:
    prev_raw = f.readlines()


# for 3- and 4-letter and 5-letter words we'll defer to the leeds
#   corpus and then take the lower of the other two
# for 6+ we'll defer to the 2nd and 3rd lists and cap anything 
#   which appears on the first but not the other two at 39

pattern = re.compile('[^a-zA-Z]')
def cleanup(word):
    w = pattern.sub('', word)
    return w.upper()

cross_wl = {}
for w in cross_raw: 
    w, s = w.split(';') 
    cross_wl[cleanup(w)] = int(s.strip())

def score_freq(word, i):
    if len(word) == 3:
        if i < 3000:
            return 50
        elif i < 5000:
            return 49
        elif i < 8000:
            return 48
        elif i < 12000:
            return int(48 - (i-8001)/4000 * 4)
        elif i < 15000:
            return int(44 - (i-12001)/8000 * 9)
        else:
            return 35

    elif len(word) == 4:
        if i < 5000:
            return 50
        elif i < 8000:
            return 49
        elif i < 11000:
            return 48
        elif i < 15000:
            return int(48 - (i-11001)/4000 * 4)
        else:
            return int(44 - (i-15001)/15000 * 9)

    elif len(word) == 5:
        if i < 8000:
            return 50
        elif i < 12000:
            return 49
        elif i < 15000:
            return 48
        else:
            return int(48 - (i-15001)/15000 * 10)

    elif len(word) == 6:
        if i < 20000:
            return 50
        else:
            return int(50 - (i-20001)/10000 * 10)

    else:
        return 50

freq_wl = {}
for i, w in enumerate(freq_raw):
    word = cleanup(w)
    freq_wl[word] = score_freq(word, i)

def score_lemma(word, i):
    if len(word) == 3:
        if i < 6000:
            return 50
        elif i < 8000:
            return 49
        elif i < 12000:
            return int(48 - (i-8001)/4000 * 3)
        else:
            return int(45 - (i-12001)/8000 * 5)

    elif len(word) == 4:
        if i < 12000:
            return 50
        elif i < 15000:
            return 49
        else:
            return 48

    else:
        return 50


lemma_wl = {}
for i, w in enumerate(lemma_raw):
    word = cleanup(w)
    lemma_wl[word] = score_lemma(word, i)

overrides = {
    'good': overrides_good.split('\n'),
    'meh': overrides_meh.split('\n')
}
overrides_all = [*overrides['good'], *overrides['meh']]

def prev_score(word, s):
    s = float(s)
    if len(word) < 5:
        if s > 0.72:
            return 50
        elif s > 0.69:
            return 49
        elif s > 0.65:
            return 48
        else:
            return (s / 0.65) * 16 + 32
    if s > 0.75:
        return 50
    if s > 0.69:
        return 49
    return (s / 0.65) * 24 + 25

prev_wl = {}
for line in prev_raw: 
    w, s, _, _, _ = line.split('\t') 
    word = cleanup(w)
    prev_wl[word] = prev_score(word, s)

def combined_score(word, 
                   lemma_wl=lemma_wl, 
                   freq_wl=freq_wl, 
                   cross_wl=cross_wl):
    if word in overrides['good']:
        return 50

    if word in overrides['meh']:
        return 45

    # trust the word prevalence study on dictionary words
    if word in prev_wl:
        if word not in lemma_wl:
            return prev_wl[word]

        scores = (
            prev_wl[word],
            prev_wl[word],
            lemma_wl[word],
        )
        return mean(scores)

    if word in lemma_wl:
        scores = (
            freq_wl.get(word, 35),
            cross_wl.get(word, 35),
            lemma_wl.get(word, 35),
        )
        return mean((median(scores), mean(scores)))

    if word in freq_wl:
        return mean((
            freq_wl.get(word, 35),
            cross_wl.get(word, 35)
        ))

    # exclude anything else from the "BEST" lists
    #   crossword list overvalues proper names + 'S'
    if len(word) == 3 or word.endswith("S"):
        return cross_wl[word] - 5

    return cross_wl[word] - 4


combined_words = [*lemma_wl.keys(), *freq_wl.keys(), *cross_wl.keys()]
wls = {
    word: combined_score(word)
    for word in combined_words
}


wls_fair = [
    w for w, s in wls.items()
    if s > 25 and len(w) > 2
] 

wls_good = [
    w for w, s in wls.items()
    if s > 42 and len(w) > 2
] 

wls_great = [
    w for w, s in wls.items()
    if s > 45 and len(w) > 2
] 

wls_best = [
    w for w, s in wls.items()
    if s > 47 and len(w) > 2
] 

with open('./data/wls_fair.txt', 'w') as f: 
    f.write('\n'.join(wls_fair))
        
with open('./data/wls_good.txt', 'w') as f: 
    f.write('\n'.join(wls_good))
        
with open('./data/wls_great.txt', 'w') as f: 
    f.write('\n'.join(wls_great))
        
with open('./data/wls_best.txt', 'w') as f: 
    f.write('\n'.join(wls_best))


print('Dictonary creation complete:')
print('wls_best:')
best_3 = sorted([word for word in wls_best if len(word) == 3], key=wls.get)
best_4 = sorted([word for word in wls_best if len(word) == 5], key=wls.get)
print(f'\t{len(best_3)}\t3-letter words, worst: {best_3[0]}')
print(f'\t{len(best_4)}\t4-letter words, worst: {best_4[0]}')
print('wls_great:')
great_3 = sorted([word for word in wls_great if len(word) == 3], key=wls.get)
great_4 = sorted([word for word in wls_great if len(word) == 5], key=wls.get)
print(f'\t{len(great_3)}\t3-letter words, worst: {great_3[0]}')
print(f'\t{len(great_4)}\t4-letter words, worst: {great_4[0]}')
print('wls_good:')
good_3 = sorted([word for word in wls_good if len(word) == 3], key=wls.get)
good_4 = sorted([word for word in wls_good if len(word) == 5], key=wls.get)
print(f'\t{len(good_3)}\t3-letter words, worst: {good_3[0]}')
print(f'\t{len(good_4)}\t4-letter words, worst: {good_4[0]}')
print('wls_good:')
good_3 = sorted([word for word in wls_good if len(word) == 3], key=wls.get)
good_4 = sorted([word for word in wls_good if len(word) == 5], key=wls.get)
print(f'\t{len(good_3)}\t3-letter words, worst: {good_3[0]}')
print(f'\t{len(good_4)}\t4-letter words, worst: {good_4[0]}')

def explain(word):
    word = word.upper()
    print(word, f'({wls.get(word)})')
    if word in overrides_all:
        print('\t[overridden]', '50' if word in overrides_good else '45')
    print('\tprev:', prev_wl.get(word))
    print('\tlemma:', lemma_wl.get(word))
    print('\tfreq:', freq_wl.get(word))
    print('\tcross:', cross_wl.get(word))
