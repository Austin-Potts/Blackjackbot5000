
// Initialize variables

var value;
var playerCardSlots = d3.selectAll('.player').nodes();
var playerCard2Slots = d3.selectAll('.player2').nodes();
var dealerCardSlots = d3.selectAll('.dealer').nodes();
var actionList = ['0','1','2','3']
var buttonList = d3.selectAll('.action-btn').nodes()
var playerCardCount = 0
var player2CardCount = 0
var dealerCardCount = 0
var outcomeDict = 
        {'-2': 'You lost both hands!',
        '-1': 'Loser!',
        '0': 'Nobody likes ties',
        '1': 'Boom! Winner! Ca$h Money',
        '2': 'Double Ca$h Money!'}
var actionDict = {0: 'Stay', 1: 'Hit', 2: 'Double Down', 3: 'Split'}
var hand = 0
var whichPlayer = 'player'


var suitList = ['C','S','H','D']

var startingMoney = 1000;
var currentMoney = startingMoney;

// Variables to persist game data

// gameOver, outcome, gameState,whichHand,saction,cardsDealt[player,player2,dealer]
// useAce, value, bet, moneyOnLine, split_potential
var paramList = `[0, 0, 0, 0, 0, [[],[],[]],[False,False,False],[0,0,0],${value},${value},0]`

// Update html with starting money
d3.select('.money').text(` | Current Money: $${currentMoney}`)

// Have all action buttons disabled until bettin' time
d3.selectAll('.action-btn').attr('disabled',true)

// Function to clear the board after a game
function refreshBoard() {

    // 'Clear' cards
    d3.selectAll('.player').style('opacity',0)
    d3.selectAll('.player2').style('opacity',0)
    d3.selectAll('.dealer').style('opacity',0)

    // Reset buttons
    d3.selectAll('.action-btn').attr('disabled',true)
    d3.select('.placeBet').select('button').node().removeAttribute('disabled')
    d3.select('.gameOver').style('visibility','hidden')

    // Clear win probabilities
    d3.select('.totalWinProb').text('')

    updateChart([0,0,0,0])

    // Set the dealer's face-down card back to the card back image
    d3.select('img.down').attr('src','./static/card_images/green_back.png')

    // Clear the active hand coloring
    d3.select('.hand1').style('background-color','rgba(255, 255, 255, 0.05)')
    d3.select('.hand2').style('background-color','rgba(255, 255, 255, 0.05)')

    // Clear player/dealer totals
    d3.select('.player1Label').text(`Player - Hand 1`)
    d3.select('.player2Label').text(`Player - Hand 2 (For Splits)`)
    d3.select('.dealerLabel').text(`Dealer Hand`)
}

// Function to update the d3 bar chart
function updateChart(newData) {

    svg.selectAll('rect')
        .data(newData)
        .transition()
        .duration(100)
        .attr("width", x);

    svg.selectAll('.probText')
        .data(newData)
        .transition()
        .duration(100)
        .attr("x", d => x(d) - 3)
        .text(d => `${Math.floor(10*d)/10}%`)

}

// Function to start the game
function startGame() {

    // Grab bet
    value = d3.select('.placeBet').select("input[name='fname']:checked").node().value

    // 'Clear' cards
    d3.selectAll('.player').style('opacity',0)
    d3.selectAll('.player2').style('opacity',0)
    d3.selectAll('.dealer').style('opacity',0)

    // Put the game on the first hand
    hand = 0
    whichPlayer = 'player'
    d3.select('.hand1').style('background-color','rgba(0, 0, 255, 0.05)')

    // gameOver, outcome, gameState,whichHand,saction,cardsDealt[player,player2,dealer]
    // useAce, value, bet, moneyOnLine, split_potential
    paramList = `[0, 0, 0, 0, 0, [[],[],[]],[False,False,False],[0,0,0],${value},${value},0]`


    // Send signal to flask to begin game

    d3.json(`/new/0/${value}/${paramList}`).then(function(data) {

        // Get player cards
        let player_cards = data['cards_dealt']['player']

        // Make visualization
        for (i=0;i<player_cards.length;i++) {
            suit = suitList[Math.floor(Math.random() * 4)]

            playerCardSlots[i].setAttribute('src',`./static/card_images/${player_cards[i]}${suit}.png`)
            playerCardSlots[i].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')
        }

        // Use the player card count to keep track of which images to update in the hand
        playerCardCount = 2

        // Get dealer cards
        let dealer_cards = data['cards_dealt']['dealer']

        dealerCardCount = 1

        // Make viz for only first card
        suit = suitList[Math.floor(Math.random() * 4)]

        dealerCardSlots[0].setAttribute('src',`./static/card_images/${dealer_cards[0]}${suit}.png`)
        dealerCardSlots[0].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')
        dealerCardSlots[1].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

        // Update the buttons for available actions
        data['actions'].forEach((action,index) => {
            if (action.available == 1) {
                buttonList[index].removeAttribute('disabled')
            }
        })

        // Update win probabilities
        let totalWinProb = d3.select('.totalWinProb')
        totalWinProb.text(`${Math.round(10*data['winProb'])/10}%`)

        // Use a win probability list to update data for the d3 chart
        let winProbList = []
        data['actions'].forEach(action => {

            winProbList.push(action.winProb)

        })

        // Update the suggested action element and run the updateChart function with our new data
        d3.select('.betAction').text(actionDict[data['saction']])
        updateChart(winProbList)

        d3.select('.player1Label').text(`Player - Hand 1 // Total: ${data['value'][0]}`)


        // Format the booleans properly to return to flask
        for (let i=0;i<3;i++) {

            if (data['use_ace'][i] == false) {
                
                data['use_ace'][i] = 'False'
            } else {
                console.log(data['use_ace'][i])
                data['use_ace'][i] = 'True'
            }
        }


        paramList = `[${data['gameOver']},${data['outcome']},${data['gameState']},${data['whichHand']},${data['saction']},"([${data['cards_dealt']['player']}]-[${data['cards_dealt']['player2']}]-[${data['cards_dealt']['dealer']}])",[${data['use_ace']}],[${data['value']}],${data['bet']},${data['moneyOnLine']},${data['split_potential']}]`

        //console.log(paramList)

      })
      .catch(function(error) {
          console.log(error)
      });
    

    // Disable bet placement after placing bet
    d3.select('.placeBet').select('button').node().setAttribute('disabled',true)

}

// This function will move the game forward whenever an action button is hit
function action(action) {

    // Disable double down and split buttons once the game moves forward
    buttonList[2].setAttribute('disabled',true)
    buttonList[3].setAttribute('disabled',true)

    console.log(paramList)

    // Send action to flask route
    d3.json(`/continue/${action}/${value}/${paramList}`).then(function(data) {

        // Logic to update card images, when the action is 1 or 2
        if (((data['cards_dealt'][whichPlayer]).length > 2) && ((action == '1') || (action == '2'))) {
            
            // Get last card of the list
            let player_card = data['cards_dealt'][whichPlayer].slice(-1)

            // For our viz, just randomly choose a suit
            let suit = suitList[Math.floor(Math.random() * 4)]

            // Append new card image for player(s)
            if (whichPlayer == 'player') {
                let slot = playerCardCount
                playerCardSlots[slot].setAttribute('src',`./static/card_images/${player_card}${suit}.png`)
                playerCardSlots[slot].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

                playerCardCount++
            } else {
                let slot = player2CardCount
                playerCard2Slots[slot].setAttribute('src',`./static/card_images/${player_card}${suit}.png`)
                playerCard2Slots[slot].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

                player2CardCount++
            }
        }

        // Update the hand we're playing
        hand = data['whichHand']
        if (hand == 1) {
            whichPlayer = 'player2'
            d3.select('.hand1').style('background-color','rgba(255, 255, 255, 0.05)')
            d3.select('.hand2').style('background-color','rgba(0, 0, 255, 0.05)')
        }

        // If the action is a split
        if (action == '3') {

            // Take second card of first hand and move it to second hand
            let image = playerCardSlots[1].getAttribute('src')
            
            playerCard2Slots[0].setAttribute('src',image)
            playerCard2Slots[0].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

            // Update first card of second hand
            let player_card = data['cards_dealt']['player'].slice(-1)
            let suit = suitList[Math.floor(Math.random() * 4)]

            playerCardSlots[1].setAttribute('src',`./static/card_images/${player_card}${suit}.png`)
            

            // Update second card of second hand
            let player2_card = data['cards_dealt']['player2'].slice(-1)
            suit = suitList[Math.floor(Math.random() * 4)]

            playerCard2Slots[1].setAttribute('src',`./static/card_images/${player2_card}${suit}.png`)
            playerCard2Slots[1].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

            player2CardCount = 2


        }

        // If the game is over, follow this logic
        if (data['gameOver'] == 1) {

            // console.log(data)
            d3.select('.dealerLabel').text(`Dealer Hand // Total: ${data['value'][2]}`)

            // Disable all buttons
            d3.selectAll('.action-btn').attr('disabled',true)

            // Get the dealer cards
            let dealer_cards = data['cards_dealt']['dealer']

            console.log(dealer_cards)

            // Loop through the cards and update images
            for (i=1;i<dealer_cards.length;i++) {
                suit = suitList[Math.floor(Math.random() * 4)]
    
                dealerCardSlots[i].setAttribute('src',`./static/card_images/${dealer_cards[i]}${suit}.png`)
                dealerCardSlots[i].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')
            }

            // Make the game over div visible & update the outcome text
            d3.select('.gameOver').style('visibility','visible')
            d3.select('.gameOverText').text(`${outcomeDict[data['outcome']]}`)

            // Update the current money
            currentMoney = currentMoney + data['outcome']*data['moneyOnLine'];
            d3.select('.money').text(` | Current Money: $${currentMoney}`)
            d3.select('.betAction').text('*Waiting for New Game*')
        } else {

            // Update win probabilities and suggestion
            let totalWinProb = d3.select('.totalWinProb')
            totalWinProb.text(`${Math.round(10*data['winProb'])/10}%`)

            let winProbList = []
            data['actions'].forEach(action => {

                winProbList.push(action.winProb)

            })

            // Update d3 bars
            updateChart(winProbList)

            // Update suggested action
            d3.select('.betAction').text(actionDict[data['saction']])
        }

        console.log(data['value'])
        d3.select('.player1Label').text(`Player - Hand 1 // Total: ${data['value'][0]}`)
        if (data['value'][1] > 0) {
            d3.select('.player2Label').text(`Player - Hand 2 (For Splits) // Total: ${data['value'][1]}`)
        }

        for (let i=0;i<3;i++) {

            if (data['use_ace'][i] == false) {
                
                data['use_ace'][i] = 'False'
            } else {
                console.log(data['use_ace'][i])
                data['use_ace'][i] = 'True'
            }
        }

        paramList = `[${data['gameOver']},${data['outcome']},${data['gameState']},${data['whichHand']},${data['saction']},"([${data['cards_dealt']['player']}]-[${data['cards_dealt']['player2']}]-[${data['cards_dealt']['dealer']}])",[${data['use_ace']}],[${data['value']}],${data['bet']},${data['moneyOnLine']},${data['split_potential']}]`

    });

}