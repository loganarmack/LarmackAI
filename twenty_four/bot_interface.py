async def on_round_end(ctx, data, game_over_callback):
    await ctx.send(data)

async def on_wrong_answer(ctx, reason):
    await ctx.send(reason)
