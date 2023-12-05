import pathlib
import numpy
import torch

import self_play
from games.tablut import Game, MuZeroConfig


class MuZero:

    def __init__(self, game, config):
        # Load the game and the config from the module with the game name
        self.Game = game
        self.config = config
        self.checkpoint = None

        # Fix random generator seed
        numpy.random.seed(self.config.seed)
        torch.manual_seed(self.config.seed)

    def make_move(
        self, position, player
    ):
        self_play_worker = self_play.SelfPlay(self.checkpoint, self.Game, self.config, numpy.random.randint(10000))
        if player == 'WHITE':
            return self_play_worker.make_move(position, 1 if player == 'WHITE' else -1)
        if player == 'BLACK':
            return self_play_worker.make_move(position, 1 if player == 'WHITE' else -1)
        print('bad player name!\n' * 100)

    def load_model(self, checkpoint_path):
        """
        Load a model

        Args:
            checkpoint_path (str): Path to model.checkpoint or model.weights.
        """
        # Load checkpoint
        checkpoint_path = pathlib.Path(checkpoint_path)
        self.checkpoint = torch.load(checkpoint_path)


def create_model():
    muzero = MuZero(game=Game, config=MuZeroConfig())
    muzero.load_model(checkpoint_path='/home/tablut/tablut/myTablut/tablut/model.checkpoint')
    return muzero


