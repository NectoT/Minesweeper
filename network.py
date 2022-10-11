import random

import numpy
import numpy as np
import math
from main import Minesweeper


def sigmoid(z):
    return 1/(1 + np.exp(-z / 100))


def sigmoid_derivative(z):
    return sigmoid(z)*(1 - sigmoid(z))


def ReLU(x):
    return x * (x > 0)


w1 = np.random.rand(400, 20)
w2 = np.random.rand(20, 20)
w3 = np.random.rand(20, 9)

max_turns_made = 0
max_reward = -1

for i in range(10000):
    game = Minesweeper()
    turns_made = 0

    grad_w1 = np.zeros(w1.shape)
    grad_w2 = np.zeros(w2.shape)
    grad_w3 = np.zeros(w3.shape)

    reward = 1
    while not game.check_win():
        inp = np.transpose(np.array(game.get_field_info(), ndmin=2)).T
        inp = inp + 1  # -1 for hidden tiles kinda breaks things
        weighted_inp = np.dot(inp, w1)
        h1 = ReLU(weighted_inp)
        weighted_h1 = np.dot(h1, w2) + 1
        h2 = np.log(weighted_h1)
        weighted_h2 = np.dot(h2, w3)
        out = sigmoid(weighted_h2)
        decision = []

        try:
            for bit in out[0,:]:
                decision.append(math.ceil(random.random() - (1 - bit)))
        except ValueError as e:
            raise e

        turns_made += 1
        answer = 0
        for i in range(len(decision)):
            answer += decision[i] << i

        turn_successful = game.open_tile(answer)

        # backpropagation (should be here)
        descent_speed = 0.01

        chain = np.array(2 * (out - np.array(decision)) * sigmoid_derivative(weighted_h2), ndmin=2)
        grad_w3 += h2.T @ chain * descent_speed

        chain = chain @ w3.T / weighted_h1
        grad_w2 += h1.T @ chain * descent_speed

        chain = chain @ w2.T * numpy.heaviside(weighted_inp, 0)
        grad_w1 += inp.T @ chain * descent_speed

        if not turn_successful:
            reward = -1 + (numpy.e**(turns_made/200) - numpy.e**(-turns_made/200)) \
                     / (numpy.e**(turns_made/200) + numpy.e**(-turns_made/200))
            max_reward = max(max_reward, reward)
            #reward *= -1
            break

    if game.check_win():
        reward = 1
    print(turns_made)

    grad_w1 = grad_w1 / turns_made * reward
    grad_w2 = grad_w2 / turns_made * reward
    grad_w3 = grad_w3 / turns_made * reward
    w1 -= grad_w1
    w2 -= grad_w2
    w3 -= grad_w3
    max_turns_made = max(max_turns_made, turns_made)

print(max_turns_made, max_reward)

