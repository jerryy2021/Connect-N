"""This Python module contains required constants defined for Connect4 project.

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

OFFSET = 5
PLAYER1 = 1
PLAYER2 = 2
EMPTY = 0
VERTICAL = 'Vertical'
HORIZ = 'Horizontal'
TOP_RIGHT = 'Top-right bottom-left'
TOP_LEFT = 'Top-left bottom-right'
UPPER_RIGHT = 'Upper-right'
LOWER_LEFT = 'Lower-left'
UPPER_LEFT = 'Upper-left'
LOWER_RIGHT = 'Lower-right'
SQUARE_SIZE = 100
CONNECT_N = 4
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
RAD = SQUARE_SIZE // 2



if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
