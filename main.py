import os
import simplematrixbotlib as botlib
import wordle as w


if __name__ == '__main__':
    creds = botlib.Creds(
        homeserver=os.environ.get('HOMESERVER'),
        username=os.environ.get('USERNAME'),
        password=os.environ.get('PASSWORD'),
        access_token=os.environ.get('ACCESS_TOKEN')
        )
    
    bot = botlib.Bot(creds)
    prefix = os.environ.get('PREFIX', 'w!')

    @bot.listener.on_message_event
    async def help_message(room, message):
        match = botlib.MessageMatch(room, message, bot, prefix)
        if not (match.prefix() and (match.command('h') or match.command('help'))):
            return
        
        response = ("## matrix-wordle\n"
            "An implementation of the popular Wordle game for the Matrix Protocol.\n"
            "Commands:\n"
            "help, h - Display help message\n")
        await bot.api.send_markdown_message(room.room_id, response)

    bot.run()