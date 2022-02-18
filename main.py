import os
import simplematrixbotlib as botlib
import wordle as w
import state as s


if __name__ == '__main__':
    creds = botlib.Creds(
        homeserver=os.environ.get('HOMESERVER'),
        username=os.environ.get('USERNAME'),
        password=os.environ.get('PASSWORD'),
        access_token=os.environ.get('ACCESS_TOKEN')
        )
    
    bot = botlib.Bot(creds)
    prefix = os.environ.get('PREFIX', 'w!')

    try:
        s.load_state()
    except FileNotFoundError:
        s.save_state({})

    @bot.listener.on_message_event
    async def help_message(room, message):
        match = botlib.MessageMatch(room, message, bot, prefix)
        if not (match.prefix() and (match.command('h') or match.command('help'))):
            return
        
        response = ("## matrix-wordle\n"
            "An implementation of the popular Wordle game for the Matrix Protocol.\n"
            "Commands:\n"
            "help, h - Display help message\n"
            "start, s - Start a new Wordle")
        await bot.api.send_markdown_message(room.room_id, response)
    
    @bot.listener.on_message_event
    @s.ensure_state
    async def start_game(room, message, state):
        match = botlib.MessageMatch(room, message, bot, prefix)
        if not (match.prefix() and (match.command('start') or match.command('s'))):
            return
        
        user = message.sender
        state[user] = 0
        response = ("Starting new Wordle game!\n\n"\
                    "Guess a 5 letter word:\n\n"
                    "```- - - - -```"
        )
        await bot.api.send_markdown_message(room.room_id, response)
        s.save_state(state)

    @bot.listener.on_message_event
    @s.ensure_state
    async def guess_word(room, message, state):
        match = botlib.MessageMatch(room, message, bot, prefix)
        if not (match.prefix() and (match.command('guess') or match.command('g'))):
            return
        
        user = message.sender

        result = w.check_guess(match.args()[0], w.get_daily())
        response = f"{'   '.join(x for x in match.args()[0])}\n{''.join(x for x in result)}"
        
        
        if not (user in state.keys()):
            response = f"Please start a new Wordle game with \"{prefix}start\" before guessing!"
            await bot.api.send_text_message(room.room_id, response)
            return
        
        if not state[user] in range(0, 5):
            response = f"{response}\nOut of guesses!\n The answer may be revealed with \"{prefix}answer\"."
            await bot.api.send_markdown_message(room.room_id, response)
            state.pop(user)
            s.save_state(state)
            return
        
        if not (
            len(match.args()) == 1 and
            w.check_guess(
                match.args()[0], w.get_daily()
                )):
            response = "Invalid guess. Please guess a valid 5 letter word"
            await bot.api.send_text_message(room.room_id, response)
            return
        
        if result == list(w.GREEN*5):
            response = f"{response}\nThe answer was {w.get_daily()}. You Won in {state[user]+1} tries!"
            await bot.api.send_text_message(room.room_id, response)
            state.pop(user)
            s.save_state(state)
            return

        state[user] = state[user] + 1
        s.save_state(state)
        await bot.api.send_text_message(room.room_id, response)    

    bot.run()