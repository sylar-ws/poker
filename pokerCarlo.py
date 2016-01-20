"""

Approximates heads-up probability of winning your poker hand using Monte Carlo.
Enter cards into main function with 

"""

import itertools
import random

NUMSAMPLES = 5000
suits = {"s": "Spades", "h": "Hearts", "d": "Diamonds", "c": "Clubs"}
numbers = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
faces = {14: "Ace", 13: "King", 12: "Queen", 11: "Jack"}

class Card:

	def __init__(self, string):
		if len(string) == 3:
			self.number = numbers[string[:2:]]
			self.suit = suits[string[2]]
		else:
			self.number = numbers[string[0]]
			self.suit = suits[string[1]]

	def __str__(self):
		if self.number in faces:
			return faces[self.number] + " of " + self.suit
		return str(self.number) + " of " + self.suit

	def __eq__(self, other):
		return self.suit == other.suit and self.number == other.number

def main():
	hand1 = [Card("Ah"), Card("5s")]
	hand2 = [Card("Jd"), Card("5d")]
	community = []
	# community = [Card("2c"), Card("Qs"), Card("Qd"), Card("5c"), Card("10s")]
	results = calculate([hand1, hand2], community)
	print(str(hand1[0]) + ", " + str(hand1[1]) + ": " + str(results[0]) + "%")
	print(str(hand2[0]) + ", " + str(hand2[1]) + ": " + str(results[1]) + "%")
	if results[2] > 0.01:
		print("Chop pot: " + str(results[2]) + "%") 

def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)

def calculate(listOfHands, community):
	"Evaluates the results of NUMSAMPLES samples and returns the results as a percentage"
	deck = makeDeck(listOfHands, community)
	numCardsToCome = 5 - len(community)
	p1wins = 0
	p2wins = 0
	ties = 0
	for _ in range(NUMSAMPLES):
		combination = random_combination(deck, numCardsToCome)
		newCommunity = community + [c for c in combination]
		# for c in newCommunity:
		# 	print(c)
		score1, score2 = evaluate(listOfHands[0] + newCommunity), evaluate(listOfHands[1] + newCommunity)
		if score1 > score2:
			p1wins += 1
		elif score2 > score1:
			p2wins += 1
		else:
			ties += 1
	return [p1wins/float(NUMSAMPLES) * 100, p2wins/float(NUMSAMPLES) * 100, ties/float(NUMSAMPLES) * 100]

def makeDeck(listOfHands, community):
	"Creates deck of possible cards to draw from"
	faces = ["A", "K", "Q", "J"]
	retvalue = []
	for suit in suits:
		for i in range(2, 11):
			retvalue += [Card(str(i) + suit)]
		for face in faces:
			retvalue += [Card(face + suit)]
	for hand in listOfHands:
		for card in hand:
			retvalue.remove(card)
	for card in community:
		retvalue.remove(card)
	return retvalue

def kickers(cards):
	"Evaluates the numerical kicker value of all 5 cards"
	numbers = []
	for card in cards:
		numbers += [card.number]
	numbers.sort()
	weight = .07
	score = 0
	for n in numbers[::-1]:
		score += weight * n
		weight *= .01
	return score

def evaluate(cards):
	"Determines score of a player's hand"
	best = 0
	for combination in itertools.combinations(cards, 5):
		flush = isFlush(combination)
		straight = isStraight(combination)
		kickerScore = kickers(combination)
		if flush and straight:
			return 9999
		if isFourKind(combination):
			return 7 + kickerScore
		if isFullHouse(combination):
			if best < 6:
				best = 6 + kickerScore
			continue
		if flush:
			if best < 5:
				best = 5 + kickerScore
			continue
		if straight:
			if best < 4:
				best = 4 + kickerScore
			continue
		if isThreeKind(combination):
			score = 3 + kickerScore
			if score > best:
				best = score
			continue
		if isTwoPair(combination):
			twoPairScore = calcTwoPair(combination)
			score = 2 + twoPairScore
			if score > best:
				best = score
			continue
		if isPair(combination):
			score = 1 + kickerScore
			if score > best:
				best = score
			continue
		else:
			score = kickerScore
			if score > best:
				best = score
	return best

def isFourKind(cards):
	"Returns True iff 4 of a kind exists in 5 card hand"
	for combination in itertools.combinations(cards, 4):
		number = combination[0].number
		kind = True
		for card in combination:
			if card.number != number:
				kind = False
		if kind:
			return True
	return False

def isFullHouse(cards):
	"Returns True iff full house exists in 5 card hand"
	for three in itertools.combinations(cards, 3):
		t = [t for t in three]
		rest = []
		for card in cards:
			if card not in t:
				rest += [card]
		if isThreeKind(t) and isPair(rest):
			return True
	return False

def isFlush(cards):
	"Returns True iff flush exists in 5 card hand"
	suit = cards[0].suit
	for card in cards:
		if card.suit != suit:
			return False
	return True

def isStraight(cards):
	"Returns True iff straight exists in 5 card hand"
	numbers = []
	for card in cards:
		numbers += [card.number]
	numbers.sort()
	for i in range(len(numbers)-1):
		if i == 3 and numbers[i+1] == 14:
			return True
		if numbers[i+1] - numbers[i] != 1:
			return False
	return True

def isThreeKind(cards):
	"Returns True iff three of a kind exists in 5 card hand"
	for combination in itertools.combinations(cards, 3):
		number = combination[0].number
		kind = True
		# print(number)
		for card in combination:
			if card.number != number:
				kind = False
		if kind:
			return kind
	return False

def isTwoPair(cards):
	"Returns True iff two pairs exist in 5 card hand"
	numPairs = 0
	for combination in itertools.combinations(cards, 2):
		if combination[0].number == combination[1].number:
			numPairs += 1
	if numPairs > 1:
		return True
	return False

def calcTwoPair(combinations):
	"Returns value of the two pair"
	numbers = []
	for combination in itertools.combinations(combinations, 2):
		number = combination[0].number
		if number == combination[1].number:
			if number not in numbers:
				numbers += [number]
	for c in combinations:
		if c.number not in numbers:
			other = c.number
	return numbers[0] * .07 + numbers[1] * .07 * .01 + other * .07 * .0001

def isPair(cards):
	"Returns True iff pair exists in 5 card hand"
	for combination in itertools.combinations(cards, 2):
		if combination[0].number == combination[1].number:
			return True
	return False

main()

