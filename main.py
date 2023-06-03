"""This Python module allows playing the our Connect4 game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of TA's
responsible for grading works of the CSC111 students at the University
of Toronto St. George campus. All forms of distribution of this code,
whether as given or with any changes, are expressly prohibited. For
more information on copyright for Connect N materials, please consult
one of our team members eaither face-to-face or via email.

EMAILS:
Ahmad Abugharbieh: ahmad.abugharbieh@mail.utoronto.ca
Jerry YAN: jerryzhixi.yan@mail.utoronto.ca
Burak UNAT: burak.unat@mail.utoronto.ca
Tim Shen: shutian.shen@mail.utoronto.ca

This file is Copyright (c) 2023 Jerry Yan, Burak Unat, Ahmad Abugharbieh
and Tim Shen.
"""
from components import Board
from game import Game, user_config


if __name__ == '__main__':
    side_length = user_config()
    board = Board(side_length)
    Game(board).run_game()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['game', 'components'],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
