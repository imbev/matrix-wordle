import csv
import datetime
import os

GREEN = '🟩'
YELLOW = '🟨'
BLACK = '⬛'

def get_daily():
    now = datetime.datetime.now()
    month, day, year = now.strftime("%b"), str(now.day).zfill(2), str(now.year)

    with open(os.path.join('resources', 'wordle_key.csv'), newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if (row[0], row[1], row[2]) == (month, day, year):
                return row[5]

def check_guess(guess: str, answer: str) -> list:
    guess = guess.upper()

    with open(os.path.join('resources', 'wordle_key.csv'), newline='') as f:
        reader = csv.reader(f, delimiter=',')
        valid = False
        for row in reader:
            if row[5] == guess:
                valid = True
        if not valid:
            return []

    check = []
    for i in range(5):
        if guess[i] == answer[i]:
            check.append(GREEN)
        elif guess[i] in answer:
            check.append(YELLOW)
        else:
            check.append(BLACK)
    return check