"""This Python module contains Game class of Connected4 project.

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
from __future__ import annotations

from typing import Optional

import pygame

import components
import constants
from player import Player, EasyAIPlayer, AIPlayer


class Game:
    """A Connect Four Game object

    Instance Attributes:
    board: the Board object on which this Game is played.
    turn: the name of the player who should move
    game_over: a boolean value indicating whether this Game is over.
    player1: the human player of this Game
    player2: initially set to None, self.player2 will be set after the user selects the type of game to be played,
             that is, after the user clicks Easy Level, Hard Level, or Multi-Player.
    winner: initially set to 'NO ONE', the winner of this Game will become the player that first
            obtains a vertical, horizontal, or diagonal sequence of length CONNECT_N
    ai_mode: a boolean value indicating whether this Game is played with any AIPlayer.
    """
    players: list[Player]
    game_over: bool
    turn: int
    board: components.Board
    player1: Player
    player2: Optional[Player]
    winner: int | str
    ai_mode: bool
    winning_font: pygame.font.Font

    def __init__(self, board: components.Board) -> None:
        """Initialization of Game class"""
        self.game_over = False
        self.turn = constants.PLAYER1
        self.board = board
        self.player1 = Player(constants.PLAYER1)
        self.player2 = None
        self.winner = 'NO ONE'
        self.ai_mode = False
        pygame.init()
        self.winning_font = pygame.font.SysFont('monospace', int(constants.SQUARE_SIZE // 3))
        pygame.init()

    def draw_header(self, screen: pygame.Surface) -> None:
        """Draw header—this is the board's black bar."""
        header_bar = pygame.Rect(0, 0, screen.get_width(), constants.SQUARE_SIZE)
        pygame.draw.rect(screen, constants.BLACK, header_bar)

    def draw_hanging_circle(self, screen: pygame.Surface, event: pygame.event.Event) -> None:
        """Draw the hanging circle of player at self.turn at the beginning of each turn"""
        x_position = event.pos[0]
        if self.turn == constants.PLAYER1:
            pygame.draw.circle(screen, constants.RED, (x_position, constants.RAD), constants.RAD)
        else:
            pygame.draw.circle(screen, constants.YELLOW, (x_position, constants.RAD), constants.RAD)

    def process_player_input(self, column: int, player: Player) -> None:
        """Process player input column. If player wins after input, then update the state of this game
        accordingly and display winning message

        Preconditions:
        - column in range(self.board.side_length)
        - player in {self.player1, self.player2}
        """
        if self.board.is_valid_column(column):
            row = self.board.get_next_open_row(column)
            node = player.make_move(row, column, self.board)
            if player.is_winning_move(node):
                self.game_over, self.winner = True, player.name
                label = self.winning_font.render(f'Player {player.name} WINS!!', True, player.color)
                width = self.board.screen.get_width()
                label_rect = label.get_rect(center=(width // 2, constants.SQUARE_SIZE // 2))
                self.draw_header(self.board.screen)
                self.board.screen.blit(label, label_rect)
            if not self.board.get_valid_locations():
                self.game_over = True
                label = self.winning_font.render('TIE', True, constants.BLUE)
                width = self.board.screen.get_width()
                label_rect = label.get_rect(center=(width // 2, constants.SQUARE_SIZE // 2))
                self.board.screen.blit(label, label_rect)
        pygame.display.flip()

    def run_game(self) -> None:
        """Run this Game and print the state of this Game after the game ends"""
        # self.ask_for_board_size_and_connect_n()
        # self.board = components.Board()
        self.ask_the_level_of_difficulty()
        self.board.screen = self.board.draw()
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.MOUSEMOTION:
                    self.draw_header(self.board.screen)
                    self.draw_hanging_circle(self.board.screen, event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.draw_header(self.board.screen)
                    x_position = event.pos[0]
                    column = self.board.get_col_from_x(x_position)
                    if self.turn == constants.PLAYER1:
                        self.process_player_input(column, self.player1)
                    elif self.ai_mode is False:  # and self.turn == PLAYER2
                        self.process_player_input(column, self.player2)
                    self.turn = self.get_other_player(self.turn)
            if self.game_over:
                break

            if self.ai_mode is True and self.turn == constants.PLAYER2:
                col = self.player2.pick_best_move(self.player2.name)
                self.process_player_input(col, self.player2)
                self.turn = self.get_other_player(self.turn)
            pygame.display.flip()

        # print(self.board)
        # print(f'Player {self.winner} WINS!')
        if self.game_over:
            pygame.time.wait(3000)
        pygame.quit()

    def get_other_player(self, this_player: int) -> int:
        """Get the other player of this game

        Preconditions:
        - this_player in {PLAYER1, PLAYER2}"""

        if this_player == constants.PLAYER1:
            return constants.PLAYER2
        else:
            return constants.PLAYER1

    def ask_the_level_of_difficulty(self) -> None:
        """Ask user for level of difficulty"""
        screen = self.board.screen

        pygame.display.set_caption('Welcome to ConnectN')
        run = True
        while run:
            screen.fill('light blue')
            width, height = screen.get_width(), screen.get_height()
            center_x = width // 2
            offset = height // 4
            easy_button = components.Button('Easy Level', center_x, offset, screen)
            hard_button = components.Button('Hard Level', center_x, 2 * offset, screen)
            human_player = components.Button('Multiplayer', center_x, 3 * offset, screen)
            new_press = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if pygame.mouse.get_pressed()[0] and new_press:
                    new_press = False
                    if easy_button.check_click():
                        self.player2 = EasyAIPlayer(self.board, constants.PLAYER2)
                        self.ai_mode = True
                        run = False
                    elif hard_button.check_click():
                        self.player2 = AIPlayer(self.board, constants.PLAYER2)
                        self.ai_mode = True
                        run = False
                    elif human_player.check_click():
                        self.player2 = Player(constants.PLAYER2)
                        self.ai_mode = False
                        run = False

                if not pygame.mouse.get_pressed()[0] and not new_press:
                    new_press = True
            pygame.display.flip()


def user_config() -> int:
    """Ask user for desired board size and CONNECT_N value and return board size. Also, mutate
    constants.SQUARE_SIZE, constants.RAD to fit the board onto user's screen"""
    pygame.init()
    screen = pygame.display.set_mode((400, 400))

    pygame.display.set_caption('Welcome to Connect N')
    width, height = screen.get_width(), screen.get_height()
    center_x = width // 2
    offset = height // 4
    input1 = components.InputBox(0, offset, 100, 25, 'Enter Board Size (< 12):')
    input2 = components.InputBox(0, 2 * offset, 100, 25, 'Enter CONNECT_N:')
    run = True
    while run:
        screen.fill('gray')
        input_boxes = [input1, input2]
        button = components.Button('Play', center_x, 3 * offset, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            for box in input_boxes:
                box.handle_event(event)
        if button.check_click():
            break

        for box in input_boxes:
            box.draw(screen)

        pygame.display.flip()

    board_size = int(input1.text)
    min_dimension = min(pygame.display.get_desktop_sizes()[0])
    pygame.quit()
    board_height = (board_size + 1) * constants.SQUARE_SIZE + ((board_size + 1) * constants.OFFSET)
    while board_height > min_dimension:
        constants.SQUARE_SIZE -= 5
        constants.RAD = constants.SQUARE_SIZE // 2
        board_height = (board_size + 1) * constants.SQUARE_SIZE + ((board_size + 1) * constants.OFFSET)
    constants.CONNECT_N = int(input2.text)
    return board_size


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['components', 'player', 'pygame', 'constants', 'tkinter'],
        # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'disable': ['E1101', 'R1702', 'R0902'],
        'max-line-length': 120
    })
