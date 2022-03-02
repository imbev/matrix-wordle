import os
import simplematrixbotlib as botlib
import wordle as w
import state as s

import string

if __name__ == '__main__':
    creds = botlib.Creds(
        homeserver=os.environ.get('HOMESERVER'),
        username=os.environ.get('USERNAME'),
        password=os.environ.get('PASSWORD'),
        access_token=os.environ.get('ACCESS_TOKEN')
        )
    
    bot = botlib.Bot(creds)
    prefix = os.environ.get('PREFIX', 'w!')
    wordle = w.Wordle()

    try:
        s.load_state()
    except FileNotFoundError:
        s.save_state({})

    def bot_msg_match(room, message):
        """Wrapper function to reduce repetition"""
        return botlib.MessageMatch(room, message, bot, prefix)

    @bot.listener.on_message_event
    async def help_message(room, message):
        """Display help message to user"""
        match = bot_msg_match(room, message)
        if not valid_command("help", match):
            return
        
        response = ("## matrix-wordle\n"
            "An implementation of the popular Wordle game for the Matrix Protocol.\n"
            "Commands:\n"
            "help, h - Display help message\n"
            "start, s - Start a new Wordle\n"
            "answer, a - Reveal the answer")
        await bot.api.send_markdown_message(room.room_id, response)
    
    @bot.listener.on_message_event
    @s.ensure_state
    async def start_game(room, message, state):
        """Initialize the state and game for requesting user"""
        match = bot_msg_match(room, message)
        if not valid_command("start", match):
            return
        
        user = message.sender
        state[user] = {"guesses": 0, "guessed_letters": [], "letters_remaining": list(string.ascii_uppercase)}
        response = ("Starting new Wordle game!\n"\
                    f"Guess a 5 letter word with \"{prefix}guess\"\n"\
                    "6 guesses remaining."

        )
        await bot.api.send_markdown_message(room.room_id, response)
        s.save_state(state)

    @bot.listener.on_message_event
    @s.ensure_state
    async def guess_word(room, message, state):
        """Check the word guessed by user"""
        match = bot_msg_match(room, message)
        if not valid_command("guess", match):
            return

        user = message.sender

        # Game not started yet
        if not (user in state.keys()):
            response = f"Please start a new Wordle game with \"{prefix}start\" before guessing!"
            await bot.api.send_text_message(room.room_id, response)
            return

        # Invalid guess
        if len(match.args()) != 1 or len(match.args()[0]) != 5:
            response = f"Invalid guess, please provide a valid 5 letter word with \"{prefix}guess <word>\"."
            await bot.api.send_text_message(room.room_id, response)
            return

        # Build bot's response
        result = wordle.check_guess(match.args()[0])
        response = f"{'   '.join(x for x in match.args()[0])}\n{''.join(x for x in result['space'])}"

        # Unknown word
        if not wordle.known(match.args()[0]):
            response = f"Unknown word: \"{match.args()[0]}\"; please try again."
            await bot.api.send_text_message(room.room_id, response)
            return

        # Out of guesses
        if state[user]['guesses'] > 5:
            response = f"Out of guesses!\n The answer may be revealed with \"{prefix}answer\"."
            await bot.api.send_markdown_message(room.room_id, response)
            state.pop(user)
            s.save_state(state)
            return

        # Answer guessed correctly
        if result['space'] == list(wordle.GREEN*5):
            response = f"{response}\nThe answer was {wordle.get_daily()}. You Won in {state[user]['guesses']+1} guesses!"
            await bot.api.send_text_message(room.room_id, response)
            state.pop(user)
            s.save_state(state)
            return

        # Mid-game
        state[user]['guesses'] += 1
        for letter in result['valid']:
            if letter not in state[user]['guessed_letters']:
                state[user]['guessed_letters'].append(letter)
                state[user]['guessed_letters'] = sorted(state[user]['guessed_letters'])
            if letter in state[user]['letters_remaining']:
                state[user]['letters_remaining'].remove(letter)

        for letter in result['invalid']:
            if letter in state[user]['letters_remaining']:
                state[user]['letters_remaining'].remove(letter)

        s.save_state(state)

        response = (f"{response}\n"
            f"{6 - state[user]['guesses']} guesses remaining.\n"
            f"discovered: {''.join(state[user]['guessed_letters'])}\n"
            f"remaining: {''.join(state[user]['letters_remaining'])}"
        )
        await bot.api.send_text_message(room.room_id, response)

    @bot.listener.on_message_event
    async def reveal_answer(room, message):
        """Reveal the answer to today's puzzle"""
        match = bot_msg_match(room, message)
        if not valid_command("answer", match):
            return
        response = f"The answer is {wordle.get_daily()}."
        await bot.api.send_text_message(room.room_id, response)

    def valid_command(cmd, match) -> bool:
        """Check if the bot command is expected"""
        if not match.prefix():
            return False

        cmd_start = cmd[0]
        if match.command(cmd) or match.command(cmd_start):
            return True

        return False

    bot.run()
