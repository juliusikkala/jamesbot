def have_common_words(words1, words2):
    lwords2 = list(map(lambda l: l.lower(), words2))
    for word1 in words1:
        if word1 and word1.lower() in lwords2:
            return True
    return False
