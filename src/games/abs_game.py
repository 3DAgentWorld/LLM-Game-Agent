#!/usr/bin/env python 
# encoding: utf-8 
# @author: yihuai lan
# @fileName: abs_game.py 
# @date: 2024/2/18 13:14 
#
# describe:
#

from abc import abstractmethod


class Game:
    player_list = []

    def add_players(self, players: list) -> None:
        """
        add instantiated objects of agents into the game
        :param players: agents
        :return:
        """
        self.player_list.extend(players)

    @abstractmethod
    def init_game(self) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass
