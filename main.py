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
            "start, s - Start a new Wordle game")
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
                    "```         ```"
        )
        await bot.api.send_markdown_message(room.room_id, response)
        s.save_state(state)

    bot.run()