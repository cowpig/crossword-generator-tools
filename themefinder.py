from collections import defaultdict
from itertools import combinations


def center_letter_pair(w1, w2):
    # e.g.                                        
    # 'AAAXAAAXAAA'
    #     'BBBXZBBYBBW'
    # should return ('X', 'X')

    assert len(w1) == len(w2)
    if len(w1) < 8:
        return []

    pad = 15 - len(w1)
    return (w1[7], w2[7 - pad])


def side_letter_pairs(w1, w2):
    # e.g.                                        
    # 'BBBXZBBYBBW', 
    #     'UHHHHHZHHHH'
    # should return (('Z', 'Z'), ('W', 'Z'))

    assert len(w1) == len(w2)
    if len(w1) < 10:
        # for smaller words, assume they merely connect
        #   at their tips
        return [
            (w1[0], w2[0]),
            (w1[-1], w2[-1])
        ]
    
    pad = 15 - len(w1)
    return [
        (w1[pad], w2[0]),
        (w1[-1], w2[-pad - 1]),
    ]


def themefinder(wl):
    # break up into same-length groups
    # break groups in combinations of two
    # for each pair, look to see if:
        # 1. there is an individual word that can fit down the center
        # 2. there is another pair that can fit, padded

    themes = []

    grouped = defaultdict(list)
    for word in wl:
        if len(word) > 15 or len(word) < 7:
            raise Exception(
                f'Found word "{word}" with invalid length {len(word)}.'
                '\nNote that words of length <7 cannot be used for a theme,'
                ' as there will never be enough space to fit blanks in between.'
            )
        grouped[len(word)].append(word)

    pairs = [pair 
        for group in grouped.values() 
            for pair in combinations(group, 2)
    ]

    for pair in pairs:
        for word in wl:
            themes = [*themes, *pair_word_matches(pair, word)]

    for pair_combo in combinations(pairs, 2):
        themes = [*themes, *pair_pair_matches(*pair_combo)]

    return themes


def pair_pair_matches(pair1, pair2):
    matches = []

    # no repeats
    if len(set([*pair1, *pair2])) < 4:
        return []

    for pair_1_order in [pair1, pair1[::-1]]:
        for pair_2_order in [pair2, pair2[::-1]]:
            slp1 = side_letter_pairs(*pair_1_order)
            slp2 = side_letter_pairs(*pair_2_order)

            # e.g.

            #     F
            #     F
            # BBBXZBBYBBW
            #     F     G
            #     F     G
            #     F     G
            #     F     G
            #     F     G
            #     F     G
            #     F     G
            #     F     G
            #     F     G
            #     UHHHHHZHHHH
            #           G
            #           G

            # the output side_letter_pairs for:
            #   ('BBBXZBBYBBW', 'UHHHHHZHHHH')
            #   ('FFZFFFFFFFFFU', 'WGGGGGGGGGZGG')
            # will be:
            #   [('Z', 'U'), ('W', 'Z')]
            #   [('Z', 'W'), ('U', 'Z')]

            # so we want to make sure the reverse is equal

            if equal_in_reverse_flattened(slp1, slp2):
                matches.append((slp2, pair_1_order, pair_2_order))
    return matches


def equal_in_reverse_flattened(lofl1, lofl2):
    flattened1 = [item for sublist in lofl1 for item in sublist]
    flattened2 = [item for sublist in lofl2 for item in sublist]
    return flattened1 == flattened2[::-1]


def pair_word_matches(pair, word):
    if word in pair or len(word) % 2 == 0:
        return []

    clp = center_letter_pair(*pair)
    if word_letterpair_match(word, clp):
        return [(clp, pair, (word, ))]

    return []


def word_letterpair_match(word, letter_pair):
    # -1 because it won't work squeezed together
    for i in range(len(word) // 2 - 1):
        if (word[i], word[-(i+1)]) == letter_pair:
            return True

    return False



def test_themefinder():
    wl = [
        'UHHHHHZHHHH',
        'AAAXAAAXAAA',
        'BBBXZBBYBBW',
        'CCXCCCCXCC',
        'DDXDDDDYDD',
        'FFZFFFFFFFFFU',
        'WGGGGGGGGGZGG',
    ]

    assert (
        ('AAAXAAAXAAA', 'BBBXZBBYBBW',),
        ('CCXCCCCXCC',),
    ) in themefinder(wl)

    assert (
        ('BBBXZBBYBBW', 'UHHHHHZHHHH'), 
        ('FFZFFFFFFFFFU', 'WGGGGGGGGGZGG')
    ) in themefinder(wl)

    assert (
        ('AAAXAAAXAAA','BBBXZBBYBBW',),
        ('DDXDDDDYDD',),
    ) not in themefinder(wl)

    assert (
        ('AAAXAAAXAAA', 'BBBXZBBYBBW',),
        ('FFZFFFFFFFFFU', 'ZGGGGGGGGWGG',),
    ) not in themefinder(wl)

    assert (
        ('UHHHHHZHHHH', 'BBBXZBBYBBW'), 
        ('FFZFFFFFFFFFU', 'WGGGGGGGGGZGG')
    ) not in themefinder(wl)

def test_letter_pairs():
    w1 = "abcdefghijk" 
    w2 = "lmnopqrstuv"
    pairs = [
        [('al', 'kv'), ('bm', 'ju'), ('cn', 'it'), ('do', 'hs'), ('ep', 'gr'), ('fq')],
        [('bl', 'ku'), ('cm', 'jt'), ('dn', 'is'), ('eo', 'hr'), ('fp', 'gq')],
        [('cl', 'kt'), ('dm', 'js'), ('en', 'ir'), ('fo', 'hq'), ('gp')],
        [('dl', 'ks'), ('em', 'jr'), ('fn', 'iq'), ('go', 'hp')],
        [('el', 'kr'), ('fm', 'jq'), ('gn', 'ip'), ('ho')],
    ]

    assert get_letter_pairs(w1, w2) == pairs

    example_word = 'viking'
    # UNFINISHED
