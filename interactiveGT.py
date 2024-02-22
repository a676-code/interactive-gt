import numpy as np
import nashpy as nash
import axelrod as axl
import matplotlib.pyplot as plt

numStrats1 = int(input("Enter the number of strategies for player 1: "))
numStrats2 = int(input("Enter the number of strategies for player 2: "))

L1 = []
for i in range(numStrats1):
    l = []
    for i in range(numStrats2):
        payoff = int(input("Enter a payoff for player 1: "))
        l.append(payoff)
    L1.append(l)
print(L1)

inputValidated = False
while(not inputValidated):
    inp = input("Would you like to enter payoffs for player 2? (y or n) ").lower()
    if inp == "y" or inp == "yes":
        L2 = []
        for i in range(numStrats1):
            l = []
            for i in range(numStrats2):
                payoff = int(input("Enter a payoff for player 2: "))
                l.append(payoff)
            L2.append(l)
        print(L2)
        
        G = nash.Game(L1, L2)
        print(G)

        print("Equilibria: ")
        eqs = G.support_enumeration()
        print(list(eqs))
    elif inp == "n" or inp == "no":
        G = nash.Game(L1)
        print(G)

        print("Equilibria: ")
        eqs = G.support_enumeration()
        print(list(eqs))
    else:
        print("Invalid input")
    
print("Expected Utilities: ")
probU = int(inp("Enter the probability that player 1 chooses U"))
probD = int(inp("Enter the probability that player 1 chooses D"))
sigma_r = np_array([probU, probD])

probL = int(inp("Enter the probability that player 2 chooses L"))
probR= int(inp("Enter the probability that player 2 chooses R"))
sigma_c = np_array([probL, probR])

print(G[sigma_r, sigma_c])