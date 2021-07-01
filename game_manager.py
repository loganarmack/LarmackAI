from game import SubstrGame

class GameManager:
    def __init__(self, user_id, channel_id):
        self.game = SubstrGame()
        self.channel_id = channel_id
        self.user_id = user_id
