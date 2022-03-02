"""Wordle game logic"""
import csv
import datetime
import os

class Wordle:
    """Game class for interacting with the known words"""
    GREEN = '🟩'
    YELLOW = '🟨'
    BLACK = '⬛'

    def __init__(self):
        """Initialize and read in the words database"""
        self.word_day = 0
        self.word_db = []
        self.word_of_the_day = ""

        # Read the words into the database
        with open(os.path.join('resources', 'wordle_key.csv'),
            newline='', encoding='ascii'
        ) as fhandle:
            reader = csv.reader(fhandle, delimiter=',')
            for row in reader:
                self.word_db.append(row[5])
        self.get_daily()

    def check_guess(self, guess: str) -> list:
        """Check how correct the user guess is

        results = {
            "space": "[green][black][black][yellow][black]",
            "valid": ['c', 'h'],
            "invalid": ['a', 's']
        }
        """
        results = {"space": [], "valid": [], "invalid": []}
        guess = guess.upper()

        if not self.known(guess):
            return results

        for i in range(5):
            if guess[i] == self.word_of_the_day[i]:
                results['space'].append(self.GREEN)
                if guess[i] not in results['valid']:
                    results['valid'].append(guess[i])
            elif guess[i] in self.word_of_the_day:
                results['space'].append(self.YELLOW)
                if guess[i] not in results['valid']:
                    results['valid'].append(guess[i])
            else:
                results['space'].append(self.BLACK)
                if guess[i] not in results['invalid']:
                    results['invalid'].append(guess[i])

        return results

    def get_daily(self) -> str:
        """Check the last retrieval date and get today's word if needed."""
        now = datetime.datetime.now()
        month, day, year = now.strftime("%b"), str(now.day).zfill(2), str(now.year)

        if self.word_day == 0 or self.word_day != day:
            self.word_day = day
            self.get_todays_word(month, day, year)

        return self.word_of_the_day

    def get_todays_word(self, month: str, day: str, year: str):
        """Retrieve the day's word from the CSV"""
        with open(os.path.join('resources', 'wordle_key.csv'),
            newline='', encoding='ascii'
        ) as fhandle:
            reader = csv.reader(fhandle, delimiter=',')
            for row in reader:
                if (row[0], row[1], row[2]) == (month, day, year):
                    self.word_of_the_day = row[5]
                    break

    def known(self, guess: str) -> bool:
        """Check if the guessed word is known by the bot"""
        guess = guess.upper()

        return guess in self.word_db
