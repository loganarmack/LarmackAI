from game import SubstrGame

class GameManager:
    def __init__(self, user_id, channel_id, other_user_ids, open_game):
        self.game = SubstrGame()
        self.channel_id = channel_id
        self.host_id = user_id
        self.other_user_ids = other_user_ids
        self.open_game = open_game

    def includes_user(self, user_id):
        return self.open_game \
            or user_id == self.host_id \
            or str(user_id) in self.other_user_ids
