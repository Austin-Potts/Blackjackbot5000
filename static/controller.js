
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

d3.select('.money').text(` | Current Money: $${currentMoney}`)

// Have all action buttons disabled until bettin' time
d3.selectAll('.action-btn').attr('disabled',true)

function refreshBoard() {

    // 'Clear' cards
    d3.selectAll('.player').style('opacity',0)
    d3.selectAll('.player2').style('opacity',0)
    d3.selectAll('.dealer').style('opacity',0)

    d3.selectAll('.action-btn').attr('disabled',true)
    d3.select('.placeBet').select('button').node().removeAttribute('disabled')
    d3.select('.gameOver').style('visibility','hidden')

    d3.select('.totalWinProb').text('')

    updateChart([0,0,0,0])

    d3.select('img.down').attr('src','./card_images/green_back.png')

    d3.select('.hand1').style('background-color','rgba(255, 255, 255, 0.05)')
    d3.select('.hand2').style('background-color','rgba(255, 255, 255, 0.05)')
}

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

function startGame() {

    // Grab bet
    value = d3.select('.placeBet').select("input[name='fname']:checked").node().value

    // 'Clear' cards
    d3.selectAll('.player').style('opacity',0)
    d3.selectAll('.player2').style('opacity',0)
    d3.selectAll('.dealer').style('opacity',0)

    // Put us on first hand
    hand = 0
    whichPlayer = 'player'

    d3.select('.hand1').style('background-color','rgba(0, 0, 255, 0.05)')

    // Send signal to flask to begin game

    d3.json(`http://127.0.0.1:5000/new/0/${value}`).then(function(data) {

        // Get player cards
        let player_cards = data['cards_dealt']['player']

        // Make visualization
        for (i=0;i<player_cards.length;i++) {
            suit = suitList[Math.floor(Math.random() * 4)]

            playerCardSlots[i].setAttribute('src',`./card_images/${player_cards[i]}${suit}.png`)
            playerCardSlots[i].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')
        }

        playerCardCount = 2

        // Get dealer cards
        let dealer_cards = data['cards_dealt']['dealer']

        dealerCardCount = 1

        // Make viz for only first card
        suit = suitList[Math.floor(Math.random() * 4)]

        dealerCardSlots[0].setAttribute('src',`./card_images/${dealer_cards[0]}${suit}.png`)
        dealerCardSlots[0].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')
        dealerCardSlots[1].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

        // let buttonList = d3.selectAll('.action-btn').nodes()

        //console.log(data)

        data['actions'].forEach((action,index) => {
            if (action.available == 1) {
                buttonList[index].removeAttribute('disabled')
            }
        })

        // Update win probabilities

        let totalWinProb = d3.select('.totalWinProb')
        totalWinProb.text(`${Math.round(10*data['winProb'])/10}%`)

        let winProbList = []
        data['actions'].forEach(action => {

            winProbList.push(action.winProb)

        })

        d3.select('.betAction').text(actionDict[data['saction']])
        updateChart(winProbList)

        console.log(data)

      })
      .catch(function(error) {
          console.log(error)
      });
    

    // Disable bet placement after placing bet
    d3.select('.placeBet').select('button').node().setAttribute('disabled',true)

}

// This function will move the game forward whenever an action button is hit
function action(action) {

    buttonList[2].setAttribute('disabled',true)
    buttonList[3].setAttribute('disabled',true)

    d3.json(`http://127.0.0.1:5000/continue/${action}/${value}`).then(function(data) {

        // Non split actions

        if (((data['cards_dealt'][whichPlayer]).length > 2) && ((action == '1') || (action == '2'))) {
            
            let player_card = data['cards_dealt'][whichPlayer].slice(-1)
            let suit = suitList[Math.floor(Math.random() * 4)]

            // Append new card image for player
            if (whichPlayer == 'player') {
                let slot = playerCardCount
                playerCardSlots[slot].setAttribute('src',`./card_images/${player_card}${suit}.png`)
                playerCardSlots[slot].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

                playerCardCount++
            } else {
                let slot = player2CardCount
                playerCard2Slots[slot].setAttribute('src',`./card_images/${player_card}${suit}.png`)
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

        if (action == '3') {

            // Take second card of first hand and move it to second hand

            let image = playerCardSlots[1].getAttribute('src')
            
            playerCard2Slots[0].setAttribute('src',image)
            playerCard2Slots[0].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

            // Update first card of second hand
            let player_card = data['cards_dealt']['player'].slice(-1)
            let suit = suitList[Math.floor(Math.random() * 4)]

            playerCardSlots[1].setAttribute('src',`./card_images/${player_card}${suit}.png`)
            

            // Update second card of second hand
            let player2_card = data['cards_dealt']['player2'].slice(-1)
            suit = suitList[Math.floor(Math.random() * 4)]

            playerCard2Slots[1].setAttribute('src',`./card_images/${player2_card}${suit}.png`)
            playerCard2Slots[1].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')

            player2CardCount = 2


        }

        if (data['gameOver'] == 1) {

            let dealer_cards = data['cards_dealt']['dealer']

            for (i=1;i<dealer_cards.length;i++) {
                suit = suitList[Math.floor(Math.random() * 4)]
    
                dealerCardSlots[i].setAttribute('src',`./card_images/${dealer_cards[i]}${suit}.png`)
                dealerCardSlots[i].setAttribute('style','opacity:1; max-width: 100%; max-height: 100%')
            }

            d3.select('.gameOver').style('visibility','visible')

            d3.select('.gameOverText').text(`${outcomeDict[data['outcome']]}`)

            currentMoney = currentMoney + data['outcome']*data['moneyOnLine'];
            d3.select('.money').text(` | Current Money: $${currentMoney}`)
            d3.select('.betAction').text('*Waiting for New Game*')
        } else {
            // Update win probabilities

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


        console.log(data)

        // If splits

    });

    // console.log(action)
}