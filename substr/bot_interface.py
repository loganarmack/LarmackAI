import substr.constant as const

def _game_update_message(data):
    message = "```ml\n"

    #previous round result
    if data.get('result'):
        message += f"{data['result']}\n"

    if data.get('remaining_letters'):
        message += f"Letters to bonus: {data['remaining_letters']}\n"

    #lives
    if data.get('lives') is not None and data.get('delta_lives'):
        message += f"Lives: {data['lives'] - data['delta_lives']} -> {data['lives']}\n"
    elif data.get('lives') is not None:
        message += f"Lives: {data['lives']}\n"

    #score
    if data.get('points'):
        message += f"Score: {data['points']}\n"

    #substring
    if data.get('substr') and data['substr'] != const.GAME_OVER:
        message += f"Enter a word containing '{data['substr']}' (time: {data['guess_time']}s)\n"
    elif data.get('substr'):
        message += "GAME OVER\n"

    message += "```"

    if data.get('turn'):
        message += f"<@{data['turn']}>"

    if data.get('eliminated'):
        message += f"<@{data['eliminated']}> has been eliminated."

    if data.get('winner'):
        message += f"\nGG, the winner is <@{data['winner']}>!"


    return message

async def on_round_end(ctx, data, game_over_callback):
    await ctx.send(_game_update_message(data))
    
    if data.get('winner') or data.get('substr') == const.GAME_OVER:
        game_over_callback(ctx, data)

async def on_wrong_answer(ctx, reason):
    await ctx.send(reason)
