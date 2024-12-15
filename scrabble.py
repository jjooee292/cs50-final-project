scores = {
    "A" : 1, 
    "B" : 3,
    "C" : 3,
    "D" : 2,
    "E" : 1,
    "F" : 4,
    "G" : 2,
    "H" : 4,
    "I" : 1,
    "J" : 8,
    "K" : 5,
    "L" : 1,
    "M" : 3,
    "N" : 1,
    "O" : 1,
    "P" : 3,
    "Q" : 10,
    "R" : 1,
    "S" : 1,
    "T" : 1,
    "U" : 1,
    "V" : 4,
    "W" : 4,
    "X" : 8,
    "Y" : 4,
    "Z" : 10,
}

def double_word(score):
    new_score = score * 2
    return new_score

def triple_word(score):
    new_score = score * 3
    return new_score

def double_letter(word):
    new_score = []
    for letter in word:
        score = scores[letter.upper()]
        new_score.append(score)
    return new_score

def triple_letter(word):
    new_score = []
    for letter in word:
        score = scores[letter.upper()]
        score = score * 2
        new_score.append(score)
    return new_score

def blanks(word):
    new_score = []
    for letter in word:
        score = scores[letter.upper()]
        new_score.append(score)
    return new_score