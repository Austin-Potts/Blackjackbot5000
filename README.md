# Black Jack & Machine Learning
### https://blackjackbot5000.herokuapp.com/
-----------------------------------------------------
### https://github.com/Austin-Potts/Blackjackbot5000
### https://github.com/jpicca/blackjackML
----
### Group team members: 
* Austin Potts
* Chris Armstrong
* Joey Picca
* Lance Westlake
* Ming Gao
* Shane Gatenby
----
#### Data Source
* <<**PLACEHOLDER**>>
    * <<**PLACEHOLDER**>>
    * <<**PLACEHOLDER**>>

----
#### Key Files:
1) <<**PLACEHOLDER**>>
    1) <<**PLACEHOLDER**>>
2) <<**PLACEHOLDER**>>
3) <<**PLACEHOLDER**>>
4) Webpage/dashboard: 
    1) html: <<**PLACEHOLDER**>>
    2) css: <<**PLACEHOLDER**>>
    3) javascript: <<**PLACEHOLDER**>>
    3) javascript: <<**PLACEHOLDER**>>
    3) javascript: <<**PLACEHOLDER**>>
    3) javascript: <<**PLACEHOLDER**>>
5) Presentation: <<**PLACEHOLDER**>>
----
#### Notes and instruction for using the blackJackReinforcement jupyter notebook file
##### *In order to replicate the process we used in creating our RL policies and datasets, please note the following...*
* There are three main sections within the blackJackReinforcement jupyter notebook file

    * Section 1: Black Jack Simulation
        * This section is able to be ran straight through, *(unless used in conjunction with Section 3, see notes within that section below)*
        * This is the Black Jack simulation where the game is set up using the BlackJackSolution class and various methods
        * An object of the BlackJackSolution class is created and game play initiated playing 1 million rounds using a given Learning Rate (LR) and Exploration Rate (ER)
        * There are two primary data outputs: stateActionOutcome and player_Q_Values
            * stateActionOutcome: dictionary of state: action results
                * state: (player hand value, dealer up card value, usable ace)
                * action {action: [games won, games played], ...}
                    * for actions: {0: stand, 1: hit, 2: double down, 3: split}
                * example: {..., (21, 10, True): {0: [3053, 3172], 1: [0, 0], 2: [0, 0], 3: [0, 0], ...}
            * player_Q_Values (developed policy for each state): dictionary of state: Q Value results
                * state: (player hand value, dealer up card value, usable ace, bet)
                * action {action: Q Value, ...}
                    * for actions: {0: stand, 1: hit, 2: double down, 3: split}
                * example: {..., (18, 5, False, 100): {0: 22.281, 1: -39.358, 2: -28.359, 3: 72.54}, ...}
    * Section 2: Development QC Tools
        * This section contains cells used to immediately visualize result from Section 1 and acts as a QC measure to make ensure results appear normal and as expected; left in notebook for future use and further development if needed
    * Section 3: Exploratory Data Analysis
        * This section was used to determine which Learning Rate and Exploration Rate (LR-ER) Combo would be used to develop the final policy (and passed through for the final run of Section 1)
        * Special attention should be taken to replicate this section as it requires a methodical, step-by-step approach since manipulation of cells in Section 1 is required at certain points.  This is because it is necessary to also include results of a random decision iteration (where only random decisions are made while using basic guidance; i.e., stand on 21, split two aces, etc...)
        
        * Steps for running through Section 3:
            * Step 1 - Once the following three items are checked/adjusted, run sections 3.01 and 3.02 for all LR-ER combos iterations
                1) Section 1.03: chooseAction() method: ensure line 173 ("if (np.random.uniform(0, 1) <= self.exp_rate*(1 - curRound/trainRound)):") **IS NOT** commented out
                    * This ensures exploration is used to develop the policy
                2) Section 1.03: chooseAction() method: ensure line 176 ("if (1 == 1):") **IS** commented out
                3) Section 1.03: play() method: ensure lines 469 through 532 **ARE** commented out for running through combos
                    * NOTE: these are only used within Section 1 and are unnecessary for Section 3 as unnecessary outputs and resources will be wasted if ran using these lines
            * Step 2 - Make the following updates - *and then run section 3.03 for the random iteration*
                1) Section 1.03: chooseAction() method: ensure line 173 ("if (np.random.uniform(0, 1) <= self.exp_rate*(1 - curRound/trainRound)):") **IS** commented out
                2) Section 1.03: chooseAction() method: ensure line 176 ("if (1 == 1):") **IS NOT** commented out
                    * This ensures exploration is NOT used to develop the policy and player decision are made using random decision (with basic guidance)
                3) Section 1.03: play() method: ensure lines 469 through 532 **REMAIN** commented out for running through combos
            * Step 3 - Continue running through cells within sections 3.04 through 3.12; section 3.12 is can be used to determine the best performing combination of LR-ER






