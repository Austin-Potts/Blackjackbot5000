# Dependencies
import numpy as np
from flask_cors import CORS
from flask import Flask, jsonify
import pickle
import random


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

#################################################
# Basis for Gameplay
#################################################

# Load model policy file
policy_file = 'Q_policy'
fr = open(policy_file, 'rb')
policy = pickle.load(fr)
fr.close()

# Load win % file
winpct_file = 'win_pct'
fr = open(winpct_file, 'rb')
win_pct = pickle.load(fr)
fr.close()

# Other variables needed
# Have a second list & usable ace in player cards to handle splits if necessary
#actionCount = 0
playerCards = [[],[]]
playerUseAce = [False, False]
playerValue = [0,0]
dealerCards = []
dealerUseAce = False
dealerValue = 0
f_dict = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                 '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10,
                 'K': 10}
num_decks = 6
gamestack = []
split_potential = 0
state = (0,0,False,10)
moneyOnLine = 0
isEnd = 0

def reset():

    # Reset actionCount, playerCards, playerUseAce, dealerCards, dealerUseAce
    #global actionCount
    #actionCount = 0

    global playerCards
    playerCards = [[],[]]

    global playerUseAce
    playerUseAce = [False, False]

    global playerValue
    playerValue = [0,0]

    global dealerCards
    dealerCards = []

    global dealerUseAce
    dealerUseAce = False

    global dealerValue
    dealerValue = 0

    global gamestack
    gamestack = []

    global split_potential
    split_potential = 0

    global state
    state = (0,0,False,10)

    global isEnd
    isEnd = 0


def makeStack():

    # Create empty stack
    test_stack = []
    
    # Define new list with faces
    f_list = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
    
    # Extend empty stack by 4*num_decks*(list of cards)
    for i in range(num_decks):
        for j in range(4):
            test_stack.extend(f_list)
    
    # Shuffle the stack
    random.shuffle(test_stack)
    
    # Set the new stack
    return test_stack

def giveCard(stack):
        
    # Remove the first card from the stack and set it to card to deal
    cardToDeal = stack.pop(0)
    
    return cardToDeal

def deal2Cards(stack, show=False):

    global split_potential

    # Stuff here for dealing
    # return value, usable_ace, and split_potential after two cards dealt
    # so initialize those here
    value, usable_ace = 0, False
    
    # Deal two cards
    cards = [giveCard(stack),giveCard(stack)] 
    #cards = ['3','3']

    if not show: 
        
        playerCards[0].append(cards[0])
        playerCards[0].append(cards[1])

        if (cards[0] == cards[1]):
            split_potential = 1

    else:
        dealerCards.append(cards[0])
        dealerCards.append(cards[1])
    
    # Create a list of card values from our cards
    card_values = [f_dict[cards[0]],f_dict[cards[1]]]
    
    # If we have two aces, we'll consider our value as 2 if it's the player
    # Otherwise for the dealer, since the dealer can't split, we'll consider it as 12
    if (card_values[0] == 1) and (card_values[1] == 1):
        
        if show:
            value = 12
            usable_ace = True
        else:
            value = 2
            usable_ace = True
        
    # If we make it to this condition, but it's True, we have one ace
    elif 1 in card_values:
        
        # Sum(card_values) = card + Ace
        # Since Ace is stored as a value of 1, we need to add 10 more to make the Ace 11
        value = sum(card_values) + 10
        usable_ace = True
        
    # Else no aces
    else:
        value = sum(card_values)
        usable_ace = False

    # If dealer, also return the show card
    if show:
        return value, usable_ace, card_values[0]
    else:
        return value, usable_ace

# Use to avoid erroring out with division by 0
def weirdDivision(n,d):
    return n / d if d else 0

# Use this to get win probs and Q value suggestion
def makeSuggestion(state,actionCount):
    
    #print(state)
    playerVal = state[0]

    # Calculate win probs
    stateOutcome = win_pct[state[0:3]]

    # ***** New stuff ******

    final_dict['actions'][0]['winProb'] = weirdDivision(stateOutcome[0][0],stateOutcome[0][1])*100
    final_dict['actions'][1]['winProb'] = weirdDivision(stateOutcome[1][0],stateOutcome[1][1])*100
    final_dict['actions'][2]['winProb'] = weirdDivision(stateOutcome[2][0],stateOutcome[2][1])*100
    final_dict['actions'][3]['winProb'] = weirdDivision(stateOutcome[3][0],stateOutcome[3][1])*100

    global split_potential

    # If first action and we can split, allow all possibilities
    if (split_potential == 1) and (actionCount == 0):
        totalWins = stateOutcome[0][0] + stateOutcome[1][0] + stateOutcome[2][0] + stateOutcome[3][0] 
        totalGames = stateOutcome[0][1] + stateOutcome[1][1] + stateOutcome[2][1] + stateOutcome[3][1]

    # If just first action, allow all possibilities except splits
    elif (actionCount == 0):
        totalWins = stateOutcome[0][0] + stateOutcome[1][0] + stateOutcome[2][0] 
        totalGames = stateOutcome[0][1] + stateOutcome[1][1] + stateOutcome[2][1]

        final_dict['actions'][3]['winProb'] = 0

    # If second action or later, only allow hits/stays
    elif (actionCount > 0):
        totalWins = stateOutcome[0][0] + stateOutcome[1][0]
        totalGames = stateOutcome[0][1] + stateOutcome[1][1]

        final_dict['actions'][3]['winProb'] = 0
        final_dict['actions'][2]['winProb'] = 0

    currentWinProb = round(totalWins/totalGames,4)*100
    final_dict['winProb'] = currentWinProb

    # New part above / old part below

    #totalWins = stateOutcome[0][0] + stateOutcome[1][0] + stateOutcome[2][0] + stateOutcome[3][0] 
    #totalGames = stateOutcome[0][1] + stateOutcome[1][1] + stateOutcome[2][1] + stateOutcome[3][1]

    #global final_dict

    #final_dict['actions'][0]['winProb'] = weirdDivision(stateOutcome[0][0],stateOutcome[0][1])*100
    #final_dict['actions'][1]['winProb'] = weirdDivision(stateOutcome[1][0],stateOutcome[1][1])*100
    #final_dict['actions'][2]['winProb'] = weirdDivision(stateOutcome[2][0],stateOutcome[2][1])*100
    #final_dict['actions'][3]['winProb'] = weirdDivision(stateOutcome[3][0],stateOutcome[3][1])*100


    # Override probability calc if splits are unavailable
    #global split_potential
    #if split_potential == 0:
    #    final_dict['actions'][3]['winProb'] = 0

    # Assess best choice
    qVals = policy[state]

    # Use our basic rules to set an action if we can
    if playerVal == 21:
        saction = 0
    elif playerVal == 2:
        saction = 3
        
    # Otherwise we go through checking our Q scores
    else:
        # Initialize a 'v' variable to compare against first Q value and set a default
        # action of staying
        v = -9999999
        saction = 0
        
        # Check each action's Q value for that state -- if it's higher than previous Q value,
        # make this the new chosen action.

        # Note that we skip checking some actions, as they cannot be performed with
        # certain states
        for a in qVals:

            # If we've already made a prior action, we can't double down or split
            # Therefore, skip these actions in the loop
            if ((actionCount > 0) and (a > 1)):        
                continue

            # If there's no split potential, skip splitting as a choice
            if ((split_potential == 0) and (a == 3)):
                continue

            # if the above two conditions aren't true, all actions are on the table
            if qVals[a] > v:
                saction = a
                v = qVals[a]

    final_dict['saction'] = saction
    
    #print(f'Action Count: {actionCount}')
    #print(saction)

def dealerPolicy(stack):
    
    global dealerValue, dealerUseAce
    if dealerValue > 21:
            
        # If dealer has a usable ace, convert it from an 11 to a 1 (subtract 10)
        # Otherwise, game is over, dealer busts
        if dealerUseAce:
            dealerValue -= 10
            dealerUseAce = False
        else:
            # Returning dealer value, usable ace, and if game is over
            return dealerValue, dealerUseAce, True

    # Dealer stays on 17 or greater
    # Otherwise, deal a new card
    if dealerValue >= 17:
        return dealerValue, dealerUseAce, True
    else:
        card = giveCard(stack)
        card_value = f_dict[card]

        dealerCards.append(card)
        # If card is an ace, check current_value and decide if we can convert
        # it to 11 or have to keep it as 1
        if card_value == 1:
            if dealerValue <= 10:
                return dealerValue + 11, True, False
            return dealerValue + 1, dealerUseAce, False
        else:
            return dealerValue + card_value, dealerUseAce, False

# Method to check winner
def winner(player_value, dealer_value):
    # player 1 | draw 0 | dealer -1
    winner = 0
    if player_value > 21:
        winner = -1
    else:
        if dealer_value > 21:
            winner = 1
        else:
            if player_value < dealer_value:
                winner = -1
            elif player_value > dealer_value:
                winner = 1
            else:
                winner = 0
    return winner

def nextValue(action,stack,initSplit=False,hand=0):

    global playerValue, playerUseAce
    if (action == '1'):

        # Update the player values if we're splitting
        if initSplit:
            playerValue[0] = int(playerValue[0]/2)
            playerValue[1] = int(playerValue[0])

            for i in [0,1]:
                card = giveCard(stack)
                #card = 'A'

                playerCards[i].append(card)

                #print(playerCards)

                if f_dict[card] == 1:
                    if playerValue[i] <= 10:
                        playerValue[i] += 11
                        playerUseAce[i] = True
                    else:
                        playerValue[i] += 1
                else:
                    playerValue[i] += f_dict[card]
        else:
            card = giveCard(stack)

            playerCards[hand].append(card)

            if f_dict[card] == 1:
                if playerValue[hand] <= 10:
                    playerValue[hand] += 11
                    playerUseAce[hand] = True
                else:
                    playerValue[hand] += 1
            else:
                playerValue[hand] += f_dict[card]


        print(hand,playerCards[hand])
            


# Template for dictionary to jsonify/return
final_dict = {
        'cards_dealt': 
            {
                'player': [],
                'player2': [],
                # First card in dealer list is the show card
                'dealer': []
            },
        'actions': [
            # Action (0: Stay, 1: Hit, 2: Double Down, 3: Split)
             {'action':0,'winProb':0,'available':1},
             {'action':1,'winProb':0,'available':1},
             {'action':2,'winProb':0,'available':1},
             {'action':3,'winProb':0,'available':0}],
        'winProb': 0,
        'saction': 0,
        # Standard (0) = typical game, no split ongoing; Standard (1) = split game
        'gameState': 0,
        'whichHand': 0,
        'gameOver': 0,
        'outcome': 0,
        'moneyOnLine': 0
    }

#################################################
# Flask Routes
#################################################

# D3.js will navigate to this url based on user actions/inputs
# Flask will use arguments from these inputs to advance
# gameplay forward. It will then return jsonified data
# to the front-end so it can be visualized

@app.route("/<game>/<action>/<bet>")
def gamePlay(game,action,bet):

    bet = int(bet)

    # If new game, deal cards
    if (game == 'new'):

        reset()
        final_dict['gameOver'] = 0
        final_dict['outcome'] = 0
        final_dict['gameState'] = 0
        final_dict['whichHand'] = 0
        final_dict['saction'] = 0
        final_dict['cards_dealt']['player'] = []
        final_dict['cards_dealt']['player2'] = []

        # Make new stack
        global gamestack
        gamestack = makeStack()

        # Deal two cards to player
        global playerValue, playerUseAce
        playerValue[0], playerUseAce[0] = deal2Cards(gamestack, show=False)
        print(f'Player cards: {playerCards}')

        # Deal two cards to dealer
        global dealerValue, dealerUseAce, dealerShow
        dealerValue, dealerUseAce, dealerShow = deal2Cards(gamestack, show=True)
        
        # Get split potential and adjust available actions
        global split_potential
        if split_potential == 1:
            final_dict['actions'][3]['available'] = 1
        else:
            final_dict['actions'][3]['available'] = 0

        global state
        state = (playerValue[0], dealerShow, playerUseAce[0], bet)
        makeSuggestion(state,0)

        final_dict['cards_dealt']['player'] = playerCards[0]
        final_dict['cards_dealt']['dealer'] = dealerCards
        final_dict['moneyOnLine'] = bet

        # Stuff to set up new round
        return jsonify(final_dict)

    # Else take action input and perform proper processing
    else:

        #global dealerValue, dealerUseAce, isEnd, gamestack
        # Manage ongoing game based on actions

        if final_dict['gameState'] == 0:
            if action == '0':
                
                global isEnd
                # Need a function to deal cards to dealer until they're done
                while not isEnd:
                    dealerValue, dealerUseAce, isEnd = dealerPolicy(gamestack)


                # Update the dictionary
                final_dict['outcome'] = winner(playerValue[0],dealerValue)
                final_dict['gameOver'] = 1
                final_dict['cards_dealt']['dealer'] = dealerCards
                

            elif (action == '1'):
                
                # Give card to player
                nextValue(action,gamestack)

                final_dict['cards_dealt']['player'] = playerCards[0]

                if playerValue[0] > 21:
                    if playerUseAce[0]:
                        playerValue[0] -= 10
                        playerUseAce[0] = False

                        state = (playerValue[0], dealerShow, playerUseAce[0], bet)
                        makeSuggestion(state,1)
                    else:
                        final_dict['outcome'] = -1
                        final_dict['gameOver'] = 1
                else:
                    state = (playerValue[0], dealerShow, playerUseAce[0], bet)
                    
                    makeSuggestion(state,1)

                #print(playerUseAce)

                #return jsonify(final_dict)

            elif (action == '2'):
                
                # Give card to player, double bet, and deal to dealer
                nextValue('1',gamestack)

                final_dict['cards_dealt']['player'] = playerCards[0]
                final_dict['moneyOnLine'] = bet*2

                if playerValue[0] > 21:
                    if playerUseAce[0]:
                        playerValue[0] -= 10
                        playerUseAce[0] = False

                        # Need a function to deal cards to dealer until they're done
                        while not isEnd:
                            dealerValue, dealerUseAce, isEnd = dealerPolicy(gamestack)

                        # Update the dictionary
                        final_dict['outcome'] = winner(playerValue[0],dealerValue)
                        final_dict['gameOver'] = 1
                        final_dict['cards_dealt']['dealer'] = dealerCards

                    else:
                        final_dict['outcome'] = -1
                        final_dict['gameOver'] = 1
                else:
                    # Need a function to deal cards to dealer until they're done
                    while not isEnd:
                        dealerValue, dealerUseAce, isEnd = dealerPolicy(gamestack)


                    # Update the dictionary
                    final_dict['outcome'] = winner(playerValue[0],dealerValue)
                    final_dict['gameOver'] = 1
                    final_dict['cards_dealt']['dealer'] = dealerCards

            elif (action == '3'):
                
                # Split cards
                # Move second card to playerCards
                # Update player values

                playerCards[1].append(playerCards[0].pop(1))

                final_dict['cards_dealt']['player2'] = playerCards[1]

                # Give card to player hand 1
                nextValue('1',gamestack,initSplit=True)

                # Update final dict
                final_dict['cards_dealt']['player'] = playerCards[0]
                
                # Create state and make suggestion
                state = (playerValue[0], dealerShow, playerUseAce[0], bet)
                makeSuggestion(state,1)

                # Update game state so we can apply proper logic down the line for splits
                final_dict['gameState'] = 1

                # Double bet
                #final_dict['moneyOnLine'] = bet*2

                print(playerCards, playerValue, playerUseAce)

            # zero-out unneeded win probabilities
            #final_dict['actions'][2]['winProb'] = 0
            #final_dict['actions'][3]['winProb'] = 0

            return jsonify(final_dict)

        # Dealing with a split game
        else:
            if final_dict['whichHand'] == 0:
                if action == '0':

                    final_dict['whichHand'] = 1

                    # Now need to make suggestion for hand 2
                    state = (playerValue[1], dealerShow, playerUseAce[1], bet)
                    makeSuggestion(state,1)

                elif action == '1':
                    # Give card to player
                    nextValue(action,gamestack)

                    final_dict['cards_dealt']['player'] = playerCards[0]

                    if playerValue[0] > 21:
                        if playerUseAce[0]:
                            playerValue[0] -= 10
                            playerUseAce[0] = False

                            state = (playerValue[0], dealerShow, playerUseAce[0], bet)
                            makeSuggestion(state,1)
                        else:
                            final_dict['outcome'] = -1
                            final_dict['whichHand'] = 1

                            # Now need to make suggestion for hand 2
                            state = (playerValue[1], dealerShow, playerUseAce[1], bet)
                            makeSuggestion(state,1)
                    else:
                        state = (playerValue[0], dealerShow, playerUseAce[0], bet)
                        
                        makeSuggestion(state,1)
            # Switch to second hand
            else:
                if action == '0':
                    # Need a function to deal cards to dealer until they're done
                    while not isEnd:
                        dealerValue, dealerUseAce, isEnd = dealerPolicy(gamestack)

                    # If hand 1 busted, no need to check it again
                    if final_dict['outcome'] == -1:

                        # Update the dictionary
                        final_dict['outcome'] = final_dict['outcome'] + winner(playerValue[1],dealerValue)
                        final_dict['cards_dealt']['dealer'] = dealerCards
                    
                    else: 

                        final_dict['outcome'] = winner(playerValue[0],dealerValue) + winner(playerValue[1],dealerValue)

                    final_dict['gameOver'] = 1

                if action == '1':

                    nextValue(action,gamestack,hand=1)

                    final_dict['cards_dealt']['player2'] = playerCards[1]

                    # If value goes over 21, try to fix with usable ace
                    if playerValue[1] > 21:
                        if playerUseAce[1]:
                            playerValue[1] -= 10
                            playerUseAce[1] = False

                            state = (playerValue[1], dealerShow, playerUseAce[1], bet)
                            makeSuggestion(state,1)

                        # if unable to fix, this hand busts
                        else:
                            
                            # if first hand also bust, set score to -2
                            if final_dict['outcome'] == -1:
                                final_dict['outcome'] = -2

                            # if first hand didn't bust, check first hand vs dealer and subtract 1 (for second hand bust)
                            else:
                                # Need a function to deal cards to dealer until they're done
                                while not isEnd:
                                    dealerValue, dealerUseAce, isEnd = dealerPolicy(gamestack)

                                final_dict['outcome'] = winner(playerValue[0],dealerValue) - 1

                            final_dict['gameOver'] = 1

                    else:
                        state = (playerValue[1], dealerShow, playerUseAce[1], bet)
                        
                        makeSuggestion(state,1)

            # zero-out unneeded win probabilities
            #final_dict['actions'][2]['winProb'] = 0
            #final_dict['actions'][3]['winProb'] = 0


            print(playerCards, playerValue, playerUseAce)
            
            return jsonify(final_dict)


    

if __name__ == '__main__':
    app.run(debug=True)
