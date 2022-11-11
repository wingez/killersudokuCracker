from collections import Counter
import random

NUM_SQUARES = 40

GO = 0
A1 = 1
CC1 = 2
A2 = 3
T1 = 4
R1 = 5
B1 = 6
CH1 = 7
B2 = 8
B3 = 9
JAIL = 10
C1 = 11
U1 = 12
C2 = 13
C3 = 14
R2 = 15
D1 = 16
CC2 = 17
D2 = 18
D3 = 19
FP = 20
E1 = 21
CH2 = 22
E2 = 23
E3 = 24
R3 = 25
F1 = 26
F2 = 27
U2 = 28
F3 = 29
G2J = 30
G1 = 31
G2 = 32
CC3 = 33
G3 = 34
R4 = 35
CH3 = 36
H1 = 37
T2 = 38
H2 = 39

LEN_CHANCE = 10


def main(iterations, counter):
    position = GO
    doubles_count = 0

    community_chest = list(range(16))
    random.shuffle(community_chest)
    chance = list(range(16))
    random.shuffle(chance)

    community_counter = 0
    chance_counter = 0

    for i in range(iterations):

        counter[position] += 1

        dice1, dice2 = random.randint(1, 4), random.randint(1, 4)

        if dice1 == dice2:
            doubles_count += 1
        else:
            doubles_count = 0

        if doubles_count == 3:
            doubles_count = 0
            position = JAIL
            continue

        moves = dice1 + dice2
        position = (position + moves) % NUM_SQUARES

        if position == G2J:
            position = JAIL
            continue

        if position in (CC1, CC2, CC3):
            action = community_chest[community_counter]
            community_counter = (community_counter + 1) % len(community_chest)

            if action == 0:
                position = GO
            elif action == 1:
                position = JAIL
            continue

        if position in (CH1, CH2, CH3):
            action = chance[chance_counter]
            chance_counter = (chance_counter + 1) % len(chance)

            if action == 0:
                position = GO
            elif action == 1:
                position = JAIL
            elif action == 2:
                position = C1
            elif action == 3:
                position = E3
            elif action == 4:
                position = H2
            elif action == 5:
                position = R1
            elif action in (6, 7):
                while position not in (R1, R2, R3, R4):
                    position = (position + 1) % NUM_SQUARES
            elif action == 8:
                while position not in (U1, U2):
                    position = (position + 1) % NUM_SQUARES
            elif action == 9:
                position = (position - 3) % NUM_SQUARES

            continue


if __name__ == '__main__':
    counter = Counter()

    for i in range(100):

        main(100000, counter)

    print(counter.most_common(5))
