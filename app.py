# Dependencies
import numpy as np
from flask_cors import CORS
from flask import Flask, jsonify, render_template
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

num_decks = 6
f_dict = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                 '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10,
                 'K': 10}


# A function to create a new stack
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

# Make a stack to draw from
gamestack = makeStack()

# A function to deal one card, using the game stack
def giveCard():
        
    # Remove the first card from the stack and set it to card to deal
    #cardToDeal = stackGive.pop(0)
    cardToDeal = random.choice(gamestack)
    
    return cardToDeal

# A function to deal two cards at the beginning of a game
def deal2Cards(cardsTrack, show=False):

    splits = 0

    # We return value, usable_ace, and split_potential after two cards dealt
    # so initialize those here
    value, usable_ace = 0, False
    
    # Deal two cards
    cards = [giveCard(),giveCard()] 
    #cards = ['3','3']

    # If dealing to player
    if not show: 
        
        cardsTrack[0].append(cards[0])
        cardsTrack[0].append(cards[1])

        # If cards are the same, we turn on the split potential
        if (cards[0] == cards[1]):
            splits = 1

    # If dealing to house/dealer
    else:
        cardsTrack[2].append(cards[0])
        cardsTrack[2].append(cards[1])
    
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
        return value, usable_ace, splits

# Use to avoid erroring out with division by 0
def weirdDivision(n,d):
    return n / d if d else 0

# Use this to get win probs and Q value suggestion
def makeSuggestion(state,actionCount,dict):
    
    # Get current player value
    playerVal = state[0]

    # Calculate win probs
    stateOutcome = win_pct[state[0:3]]

    # Holder list to return values
    probValues = [0,0,0,0,0,0]

    # Get the win percentages for individual actions, using our current state

    probValues[0] = weirdDivision(stateOutcome[0][0],stateOutcome[0][1])*100
    probValues[1] = weirdDivision(stateOutcome[1][0],stateOutcome[1][1])*100
    probValues[2] = weirdDivision(stateOutcome[2][0],stateOutcome[2][1])*100
    probValues[3] = weirdDivision(stateOutcome[3][0],stateOutcome[3][1])*100

    # Logic to calculate the total (unconditional) win probability

    # If first action and we can split, allow all possibilities
    if (dict['split_potential'] == 1) and (actionCount == 0):
        totalWins = stateOutcome[0][0] + stateOutcome[1][0] + stateOutcome[2][0] + stateOutcome[3][0] 
        totalGames = stateOutcome[0][1] + stateOutcome[1][1] + stateOutcome[2][1] + stateOutcome[3][1]

    # If just first action, allow all possibilities except splits
    elif (actionCount == 0):
        totalWins = stateOutcome[0][0] + stateOutcome[1][0] + stateOutcome[2][0] 
        totalGames = stateOutcome[0][1] + stateOutcome[1][1] + stateOutcome[2][1]

        #final_dict['actions'][3]['winProb'] = 0
        probValues[3] = 0

    # If second action or later, only allow hits/stays
    elif (actionCount > 0):
        totalWins = stateOutcome[0][0] + stateOutcome[1][0]
        totalGames = stateOutcome[0][1] + stateOutcome[1][1]

        probValues[3] = 0
        probValues[2] = 0

    currentWinProb = round(totalWins/totalGames,4)*100

    probValues[4] = currentWinProb

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
            if ((dict['split_potential'] == 0) and (a == 3)):
                continue

            # if the above two conditions aren't true, all actions are on the table
            if qVals[a] > v:
                saction = a
                v = qVals[a]

    #final_dict['saction'] = saction
    probValues[5] = saction

    dict['actions'][0]['winProb'] = probValues[0]
    dict['actions'][1]['winProb'] = probValues[1]
    dict['actions'][2]['winProb'] = probValues[2]
    dict['actions'][3]['winProb'] = probValues[3]
    dict['winProb'] = probValues[4]
    dict['saction'] = probValues[5]
    

    return dict
    

# Function to get the dealer's cards
def dealerPolicy(dealerValue,dealerUseAce,dealerCards):
    
    if dealerValue > 21:
              
        # If dealer has a usable ace, convert it from an 11 to a 1 (subtract 10)
        # Otherwise, game is over, dealer busts
        if dealerUseAce:
            dealerValue -= 10
            dealerUseAce = False
        else:
            # Returning dealer value, usable ace, and if game is over
            return dealerValue, dealerUseAce, True, dealerCards

    # Dealer stays on 17 or greater
    # Otherwise, deal a new card
    if dealerValue >= 17:
        return dealerValue, dealerUseAce, True, dealerCards
    else:
        card = giveCard()
        card_value = f_dict[card]

        dealerCards.append(card)
        # If card is an ace, check current_value and decide if we can convert
        # it to 11 or have to keep it as 1
        if card_value == 1:
            if dealerValue <= 10:
                return dealerValue + 11, True, False, dealerCards
            return dealerValue + 1, dealerUseAce, False, dealerCards
        else:
            
            return dealerValue + card_value, dealerUseAce, False, dealerCards

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

# Function to get the next state/value based on the action
def nextValue(action,cards_dealt,value,useAce,initSplit=False,hand=0):

    if (action == '1'):

        # Update the player values if we're splitting
        if initSplit:

            # Logic to ensure split Aces are given values of 11 each
            if value[0] == 2:
                value[0] = 11
                value[1] = 11

                useAce[0] = True
                useAce[1] = True
            else:
                value[0] = int(value[0]/2)
                value[1] = int(value[0])

            # Get a new card for each hand
            for i in [0,1]:
                card = giveCard()

                cards_dealt[i].append(card)

                # Check if the card is an ace and update player values
                if f_dict[card] == 1:
                    if value[i] <= 10:
                        value[i] += 11
                        useAce[i] = True
                    else:
                        value[i] += 1
                else:
                    value[i] += f_dict[card]
            

        # If we're not splitting, perform similar actions, but just for one hand
        else:
            card = giveCard()

            cards_dealt[hand].append(card)

            if f_dict[card] == 1:
                if value[hand] <= 10:
                    value[hand] += 11
                    useAce[hand] = True
                else:
                    value[hand] += 1
            else:
                value[hand] += f_dict[card]

        return cards_dealt, useAce, value
        
            

#################################################
# Flask Routes
#################################################

# D3.js will navigate to this url based on user actions/inputs
# Flask will use arguments from these inputs to advance
# gameplay forward. It will then return jsonified data
# to the front-end so it can be visualized

@app.route("/")
def template_test():
    return render_template('index.html')

@app.route("/<game>/<action>/<bet>/<paramList>")
def gamePlay(game,action,bet,paramList):

    # Get our tracked variables from the paramList
    paramList = eval(paramList)
    gameOver = paramList[0]
    outcome = paramList[1]
    gameState = paramList[2]
    whichHand = paramList[3]
    saction = paramList[4]
    cards_dealt = paramList[5]
    useAce = paramList[6]
    value = paramList[7]
    bet = paramList[8]
    moneyOnLine = paramList[9]
    split_potential = paramList[10]


    # If new game, deal cards and reset the dictionary to deliver to front-end
    if (game == 'new'):

        #reset()
        final_dict = {
            'cards_dealt': 
                {
                    'player': [],
                    'player2': [],
                    # First card in dealer list is the show card
                    'dealer': []
                },
            'use_ace':[False,False,False],
            'value': [0,0,0],
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
            'bet': bet,
            'moneyOnLine': bet,
            'split_potential': 0
        }

        # Deal two cards to player
        value[0], useAce[0], split_potential = deal2Cards(cards_dealt, show=False)

        final_dict['value'][0] = value[0]
        final_dict['use_ace'][0] = useAce[0]
        final_dict['split_potential'] = split_potential
        final_dict['cards_dealt']['player'] = cards_dealt[0]

        # Deal two cards to dealer
        value[2], useAce[2], dealerShow = deal2Cards(cards_dealt, show=True)
        

        final_dict['value'][2] = value[2]
        final_dict['use_ace'][2] = useAce[2]
        final_dict['cards_dealt']['dealer'] = cards_dealt[2]        
        
        # Get split potential and adjust available actions

        if split_potential == 1:
            final_dict['actions'][3]['available'] = 1
        else:
            final_dict['actions'][3]['available'] = 0

        # Create our initial state and update win probs / suggested actions
        state = (value[0], dealerShow, useAce[0], bet)
        final_dict = makeSuggestion(state,0,final_dict)

        return jsonify(final_dict)

    # Else if not new game, take action input and perform proper processing
    else:

        # cards_dealt processing of string returned from JS
        cards_dealt = cards_dealt.strip('(').strip(')').split('-')
        emptyList = []
        for element in cards_dealt:
            newInner = []
            if (element == '[]'):
                newInner = []
            else:
                newInner = element.strip('[').strip(']').split(',')

            emptyList.append(newInner)

        cards_dealt = emptyList


        final_dict = {
            'cards_dealt': 
                {
                    'player': cards_dealt[0],
                    'player2': cards_dealt[1],
                    # First card in dealer list is the show card
                    'dealer': cards_dealt[2]
                },
            'use_ace':useAce,
            'value': value,
            'actions': [
                # Action (0: Stay, 1: Hit, 2: Double Down, 3: Split)
                {'action':0,'winProb':0,'available':1},
                {'action':1,'winProb':0,'available':1},
                {'action':2,'winProb':0,'available':1},
                {'action':3,'winProb':0,'available':0}],
            'winProb': 0,
            'saction': 0,
            # Standard (0) = typical game, no split ongoing; Standard (1) = split game
            'gameState': gameState,
            'whichHand': whichHand,
            'gameOver': gameOver,
            'outcome': outcome,
            'bet': bet,
            'moneyOnLine': moneyOnLine,
            'split_potential': split_potential
        }


        # Manage ongoing game based on actions
        if gameState == 0:

            # Stay
            if action == '0':

                isEnd = 0
                # Need a function to deal cards to dealer until they're done
                while not isEnd:
                    value[2], useAce[2], isEnd, cards_dealt[2] = dealerPolicy(value[2],useAce[2],cards_dealt[2])

                dealerValue = value[2]
                dealerUseAce = useAce[2]
                dealerCards = cards_dealt[2]

                # Update the dictionary
                final_dict['outcome'] = winner(value[0],dealerValue)
                final_dict['gameOver'] = 1
                final_dict['cards_dealt']['dealer'] = dealerCards

            # Hit
            elif (action == '1'):
                
                # Give card to player
                cards_dealt, useAce, value = nextValue(action,cards_dealt,value,useAce)

                # Update dictionary
                final_dict['cards_dealt']['player'] = cards_dealt[0]

                # Check if player is over 21 -- if so, see if it's fixable with a usable ace
                if value[0] > 21:
                    if useAce[0]:
                        value[0] -= 10
                        useAce[0] = False

                        state = (value[0], f_dict[cards_dealt[2][0]], useAce[0], final_dict['bet'])
                        final_dict = makeSuggestion(state,1,final_dict)
                    
                    # If not, the game is over
                    else:
                        final_dict['outcome'] = -1
                        final_dict['gameOver'] = 1

                # If not over 21, game continues
                else:
                    
                    state = (value[0], f_dict[cards_dealt[2][0]], useAce[0], final_dict['bet'])
                    final_dict = makeSuggestion(state,1,final_dict)

            # Double down
            elif (action == '2'):
                
                # Give card to player, double bet, and deal to dealer
                cards_dealt, useAce, value = nextValue('1',cards_dealt,value,useAce)

                # Update dictionary
                final_dict['cards_dealt']['player'] = cards_dealt[0]
                final_dict['moneyOnLine'] = int(final_dict['bet'])*2

                # Check if player is over 21 -- if so, see if it's fixable with a usable ace
                if value[0] > 21:
                    if useAce[0]:
                        value[0] -= 10
                        useAce[0] = False

                        isEnd = 0
                        # Need a function to deal cards to dealer until they're done
                        while not isEnd:
                            value[2], useAce[2], isEnd, cards_dealt[2] = dealerPolicy(value[2],useAce[2],cards_dealt[2])

                        dealerValue = value[2]
                        dealerUseAce = useAce[2]
                        dealerCards = cards_dealt[2]

                        # Update the dictionary
                        final_dict['outcome'] = winner(playerValue[0],dealerValue)
                        final_dict['gameOver'] = 1
                        final_dict['cards_dealt']['dealer'] = dealerCards

                    else:
                        final_dict['outcome'] = -1
                        final_dict['gameOver'] = 1
                else:

                    isEnd = 0
                    # Need a function to deal cards to dealer until they're done
                    while not isEnd:
                        value[2], useAce[2], isEnd, cards_dealt[2] = dealerPolicy(value[2],useAce[2],cards_dealt[2])

                    dealerValue = value[2]
                    dealerUseAce = useAce[2]
                    dealerCards = cards_dealt[2]

                    # Update the dictionary
                    final_dict['outcome'] = winner(value[0],dealerValue)
                    final_dict['gameOver'] = 1
                    final_dict['cards_dealt']['dealer'] = dealerCards

            # Split
            elif (action == '3'):
                
                # Split cards
                # Move second card to playerCards
                # Update player values

                cards_dealt[1].append(cards_dealt[0].pop(1))

                final_dict['cards_dealt']['player2'] = cards_dealt[1]

                # Give card to player hand 1
                cards_dealt, useAce, value = nextValue('1',cards_dealt,value,useAce,initSplit=True)

                # Update final dict
                final_dict['cards_dealt']['player'] = cards_dealt[0]
                
                # Create state and make suggestion
                state = (value[0], f_dict[cards_dealt[2][0]], useAce[0], final_dict['bet'])
                final_dict = makeSuggestion(state,1,final_dict)

                # Update game state so we can apply proper logic down the line for splits
                final_dict['gameState'] = 1



            return jsonify(final_dict)

        # Dealing with a split game
        else:

            # Use dictionary to determine which hand to update
            if final_dict['whichHand'] == 0:

                # Stay
                if action == '0':
                    
                    # Switch to second hand
                    final_dict['whichHand'] = 1

                    # Now need to make suggestion for hand 2
                    state = (value[1], f_dict[cards_dealt[2][0]], useAce[1], final_dict['bet'])
                    final_dict = makeSuggestion(state,1,final_dict)

                # Hit
                elif action == '1':
                    # Give card to player
                    cards_dealt, useAce, value = nextValue(action,cards_dealt,value,useAce)

                    # Update player hand 1 cards in dictionary
                    final_dict['cards_dealt']['player'] = cards_dealt[0]


                    # Perform our standard 21 check, but with added switch to hand 2 if game is over
                    if value[0] > 21:
                        if useAce[0]:
                            value[0] -= 10
                            useAce[0] = False

                            state = (value[0], f_dict[cards_dealt[2][0]], useAce[0], final_dict['bet'])
                            final_dict = makeSuggestion(state,1,final_dict)
                        else:
                            final_dict['outcome'] = -1
                            final_dict['whichHand'] = 1

                            # Now need to make suggestion for hand 2
                            state = (value[1], f_dict[cards_dealt[2][0]], useAce[1], final_dict['bet'])
                            final_dict = makeSuggestion(state,1,final_dict)
                    else:
                        state = (value[0], f_dict[cards_dealt[2][0]], useAce[0], final_dict['bet'])
                        final_dict = makeSuggestion(state,1,final_dict)
            # Switch to second hand
            else:

                # Stay
                if action == '0':
                    
                    isEnd = 0
                    # Need a function to deal cards to dealer until they're done
                    while not isEnd:
                        value[2], useAce[2], isEnd, cards_dealt[2] = dealerPolicy(value[2],useAce[2],cards_dealt[2])

                    dealerValue = value[2]
                    dealerUseAce = useAce[2]
                    dealerCards = cards_dealt[2]

                    # If hand 1 busted, no need to check it again
                    if final_dict['outcome'] == -1:

                        # Update the dictionary
                        final_dict['outcome'] = final_dict['outcome'] + winner(value[1],dealerValue)
                        final_dict['cards_dealt']['dealer'] = dealerCards
                    
                    # If neither busted, add up both outcomes
                    else: 

                        final_dict['outcome'] = winner(value[0],dealerValue) + winner(value[1],dealerValue)

                    final_dict['gameOver'] = 1

                # Hit
                if action == '1':

                    # Get next value of second hand
                    cards_dealt, useAce, value = nextValue(action,cards_dealt,value,useAce,hand=1)

                    # Update player hand 2 cards in dictionary
                    final_dict['cards_dealt']['player2'] = cards_dealt[1]

                    # If value goes over 21, try to fix with usable ace
                    if value[1] > 21:
                        if useAce[1]:
                            value[1] -= 10
                            useAce[1] = False

                            state = (value[1], f_dict[cards_dealt[2][0]], useAce[1], final_dict['bet'])
                            final_dict = makeSuggestion(state,1,final_dict)

                        # if unable to fix, this hand busts
                        else:
                            
                            # if first hand also bust, set score to -2
                            if final_dict['outcome'] == -1:
                                final_dict['outcome'] = -2

                            # if first hand didn't bust, check first hand vs dealer and subtract 1 (for second hand bust)
                            else:
                                
                                isEnd = 0
                                # Need a function to deal cards to dealer until they're done
                                while not isEnd:
                                    value[2], useAce[2], isEnd, cards_dealt[2] = dealerPolicy(value[2],useAce[2],cards_dealt[2])

                                dealerValue = value[2]
                                dealerUseAce = useAce[2]
                                dealerCards = cards_dealt[2]

                                final_dict['outcome'] = winner(value[0],dealerValue) - 1

                            final_dict['gameOver'] = 1

                    else:
                        state = (value[1], f_dict[cards_dealt[2][0]], useAce[1], final_dict['bet'])
                        final_dict = makeSuggestion(state,1,final_dict)

            
            return jsonify(final_dict)


    

if __name__ == '__main__':
    app.run(debug=True)
