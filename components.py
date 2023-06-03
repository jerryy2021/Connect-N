"""This Python module contains the component objects for Game in game.py.

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

import player
import constants


class Board:
    """The game board object made up of nodes

    Instance Attributes:
     - side_length: the number of nodes this Board has along each side (this Board is a square)
     - nodes: a dictionary containing the (x, y) coordinates of the nodes as keys and the corresponding
              Node objects as values.
     - temp_mode: a boolean value indicating whether this Board should be created without the pygame.Surface
       object as the Board.screen attribute. This is useful for the deepcopy function used for the AIPlayer
       where deepcopy cannot pickle pygame.Surface objects.
     - width: an integer representing the width in pixels of this Board.
     - height: an integer representing the height in pixels of this Board.
     - screen: a pygame.Surface object displaying this board with GUI.
     - columns: the dictionary mapping each column to its pixels range on the screen.

     Representation Invariants:
        - self.side_length >= CONNECT_N
     """
    side_length: int
    nodes: dict[tuple[int, int], Node]
    temp_mode: bool = False
    width: int
    height: int
    screen: pygame.Surface
    columns: dict[int: range]

    def __init__(self, side_length: int, temp_mode: bool = False) -> None:
        """ Initialization of Board class"""
        self.side_length = side_length
        self.nodes = {}
        self.temp_mode = temp_mode
        self.width = (self.side_length * constants.SQUARE_SIZE) + (self.side_length + 1) * constants.OFFSET
        self.height = (self.side_length + 1) * constants.SQUARE_SIZE + ((self.side_length + 1) * constants.OFFSET)
        self.screen = pygame.display.set_mode((self.width, self.height))

        k = self.side_length
        for row in range(0, k):  # Add horizontal neighbours
            for col in range(0, k - 1):
                self.add_edge((row, col), (row, col + 1))

        for row in range(0, k):  # Add vertical neighbours
            for col in range(0, k - 1):
                self.add_edge((col, row), (col + 1, row))
                # Now add diagonal neighbours
                if row >= 1:  # and col < k - 1
                    self.add_edge((row, col), (row - 1, col + 1))  # Add upper-right neighbour
                if row >= 1 and col >= 1:
                    self.add_edge((row, col), (row - 1, col - 1))  # Add upper-left neighbour
                if row < k - 1:  # and col < k - 1
                    self.add_edge((row, col), (row + 1, col + 1))  # Add bottom-right neighbour
                if row < k - 1 and col >= 1:
                    self.add_edge((row, col), (row + 1, col - 1))  # Add bottom-left neighbour
        if not self.temp_mode:
            self.screen = self.draw()
        self.columns = {node.col: node.span for node in self.nodes.values() if node.row == 0}

    def __repr__(self) -> str:
        """ Representation of Board class"""
        board = ''
        for coordinate in self.nodes:
            board += f'\tNode({coordinate}, {self.nodes[coordinate].fill})'
            if coordinate[1] == self.side_length - 1:
                board += '\n'
        return board

    def get_nodes_fill_for_column(self, column: int) -> list[int]:
        """Return the nodes' fill attributes of given column from bottom-up order"""
        nodes_fill_so_far = []
        for row in range(self.side_length - 1, -1, -1):
            nodes_fill_so_far.append(self.nodes[(row, column)].fill)
        return nodes_fill_so_far

    def get_nodes_fill_for_row(self, row: int) -> list[int]:
        """Return the nodes' fill attributes of given row from left-to-right order"""
        nodes_fill_so_far = []
        for col in range(self.side_length):
            nodes_fill_so_far.append(self.nodes[(row, col)].fill)
        return nodes_fill_so_far

    def get_valid_locations(self) -> list:
        """Return the possible locations where a piece can be dropped.
        """
        valid_locations = []
        for col in range(self.side_length):
            if self.is_valid_column(col):
                valid_locations.append(col)
        return valid_locations

    def get_positive_diagonal(self, row: int, col: int, visited: set) -> list[int]:
        """Return the given coordinate (row, col) and its corresponding
        node's diagonal CONNECT_N - 1 nodes' fill attributes in the positive direction i.e.
         the line f(x) = x going from left to right.

        Note that the sequence returned includes the given node at (row, col) as the first element.
        So, the length of the returned list is CONNECT_N

        Preconditions:
        - (row - CONNECT_N + 1, col + CONNECT_N - 1) in self.nodes
        """
        given_node = self.nodes[(row, col)]
        nodes_fill_so_far = [given_node.fill]
        visited.add(given_node)
        for u in given_node.neighbours:
            if u not in visited and len(visited) < constants.CONNECT_N and given_node.is_direction_neighbour(
                    u, constants.UPPER_RIGHT, constants.PLAYER2, check_fill=False
            ):
                nodes_fill_so_far.extend(self.get_positive_diagonal(u.row, u.col, visited))
        return nodes_fill_so_far

    def get_negative_diagonal(self, row: int, col: int, visited: set) -> list[int]:
        """Return the given coordinate (row, col)'s corresponding
        node and its diagonal CONNECT_N - 1 nodes' fill attributes in the negative direction i.e.
         the line f(x) = -x going from left to right.

        Note that the sequence returned includes the given node at (row, col) as the first element.
        So, the length of the returned list is CONNECT_N

        Preconditions:
        - (row + CONNECT_N - 1, col + CONNECT_N - 1) in self.nodes
        """
        given_node = self.nodes[(row, col)]
        nodes_fill_so_far = [given_node.fill]
        visited.add(given_node)
        for u in given_node.neighbours:
            if u not in visited and len(visited) < constants.CONNECT_N and given_node.is_direction_neighbour(
                    u, constants.LOWER_RIGHT, constants.PLAYER2, check_fill=False
            ):
                nodes_fill_so_far.extend(self.get_negative_diagonal(u.row, u.col, visited))
        return nodes_fill_so_far

    def is_valid_column(self, col: int) -> bool:
        """Return whether col still has empty slots"""
        coord = (0, col)
        if coord in self.nodes:
            return self.nodes[coord].fill == constants.EMPTY
        return False

    def get_next_open_row(self, col: int) -> int | None:
        """Return the next available row, or None if there are no more rows available"""
        for row in range(self.side_length - 1, -1, -1):
            if self.nodes[(row, col)].is_empty():
                return row
        return None

    def add_node(self, coordinate: tuple[int, int]) -> Node:
        """Add a new node with the given coordinate to this board and return it"""
        node = Node(coordinate)
        self.nodes[coordinate] = node
        return node

    def add_edge(self, coord1: tuple[int, int], coord2: tuple[int, int]) -> None:
        """Add an edge between the two nodes with the given coordinates—coord1 and coord2.
        If a given coordinate does not correspond to a node on this board, then first create a new node
        for thatt coordinate

        Preconditions:
            - coord1 != coord2
        """
        if coord1 not in self.nodes:
            self.add_node(coord1)
        if coord2 not in self.nodes:
            self.add_node(coord2)
        node1, node2 = self.nodes[coord1], self.nodes[coord2]
        node1.neighbours.add(node2)
        node2.neighbours.add(node1)

    def get_neighbours_dict(self) -> dict[tuple[int, int], set[tuple[int, int]]]:
        """Return a dictionary containing the adjacency relationships for every node on this board.

        In the returned dictionary:
            - Each key is a coordinate of a node on this board.
            - The corresponding value is the set of coordinates of the nodes that are adjacent to
                the corresponding key's node on this board.
        """
        adjacencies_so_far = {}

        for address, node in self.nodes.items():
            adjacencies_so_far[address] = {neighbour.coordinate for neighbour in node.neighbours}

        return adjacencies_so_far

    def get_col_from_x(self, x_position: int) -> int | None:
        """Return the column that the given x_position belongs to on the board;
        if x_position does not correspond to any column, then return None. This is possible in two cases:

        1. When user clicked in an area defined by OFFSET—the area between the nodes on the board
        2. When user clicked outside of the pygame window.
        """
        colums_dict = self.columns
        for col in colums_dict:
            if x_position in colums_dict[col]:
                return col
        return

    def draw(self) -> pygame.Surface:
        """Draw this board on Pygame window"""

        screen = self.screen
        rect = pygame.Rect((0, constants.SQUARE_SIZE), (self.width, self.height - constants.SQUARE_SIZE))
        radius = constants.RAD

        pygame.draw.rect(screen, constants.BLUE, rect)
        x_position, y_position = radius + constants.OFFSET, constants.SQUARE_SIZE + radius + constants.OFFSET
        for coord in self.nodes:
            _, col = coord
            center = (x_position, y_position)
            self.nodes[coord].draw(screen, center, radius)
            if col == self.side_length - 1:
                y_position += 2 * radius + constants.OFFSET
                x_position = radius + constants.OFFSET
            else:
                x_position += 2 * radius + constants.OFFSET
            # pygame.display.flip()
        return screen


class Button:
    """Button class used by connect_four.game.Game

    Instance Attributes:
    - text: the text within this Button.
    - x_pos: the x position in pixels of the center of this Button.
    - y_pos: the y position in pixels of the center of this Button.
    - rect: the pygame.Rect area of this button used for self.check_click.
    - screen: the pygame.Surface object displaying this Button on GUI.
    - button_text_font: the text font of this button
    """
    text: str
    x_pos: int
    y_pos: int
    rect: Optional[pygame.Rect]
    screen: pygame.Surface
    button_text_font: pygame.font.Font

    def __init__(self, text: str, pos_x: int, pos_y: int, screen: pygame.Surface) -> None:
        """ Initialization of Button class"""
        self.text = text
        self.x_pos = pos_x
        self.y_pos = pos_y
        self.rect = None
        self.screen = screen
        self.button_text_font = pygame.font.Font("freesansbold.ttf", 18)
        self.draw()

    def draw(self) -> None:
        """Draw this Button"""
        button_text = self.button_text_font.render(self.text, True, 'black')
        button_text_rect = button_text.get_rect(center=(self.x_pos, self.y_pos))
        self.rect = pygame.rect.Rect((self.x_pos, self.y_pos), (100, 25))
        self.rect.center = (self.x_pos, self.y_pos)
        if self.check_click():
            pygame.draw.rect(self.screen, 'dark gray', self.rect, 0, 5)
        else:
            pygame.draw.rect(self.screen, 'light gray', self.rect, 0, 5)
        pygame.draw.rect(self.screen, 'pink', self.rect, 2, 5)
        self.screen.blit(button_text, button_text_rect)

    def check_click(self) -> bool:
        """Check whether this button is clicked."""
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        # button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (100, 25))
        if left_click and self.rect.collidepoint(mouse_pos):
            return True
        else:
            return False


class Node:
    """A node that represents a coordinate on the game board

    Instance Attributes:
    - coordinate: the (x, y) coordinate of this Node
    - neighbours: the nodes connected to this Node. The neighbour nodes are its immediately adjacent nodes
      vertically and diagonally, regardless of their Node.fill attribute—this is useful for the AIPlayer
      to evaluate sequences of four nodes recursively and determine where to move.
    - fill: the fill of this node that is either PLAYER1, PLAYER2, or EMPTY
    - row: this Node's x-coordinate used for concise, easy access
    - col: this Node's y-coordinate used for consise, easy access
    - radius: an integer representing the radius of this Node's circle
    - span: a range representing the span of this Node from its left-most side to the right-most side. This is
      useful for determining which column the user selected. When this Node is not yet drawn,
      its span is defaulted to range(1)
    - rect: a pygame.Rect object assigned to this Node after drawing it on the screen, and it is initially
      assigned to None

    Representation Invariants:
    - self not in self.neighbours
    - all(self in u.neighbours for u in self.neighbours)
    """
    coordinate: tuple[int, int]
    neighbours: set[Node]
    row: int
    col: int
    fill: int = constants.EMPTY
    radius: int
    span: range
    rect: Optional[pygame.Rect]

    def __init__(self, coordinate: tuple[int, int]) -> None:
        """ Initialization of Node class"""
        self.neighbours = set()
        self.coordinate = coordinate
        self.fill = constants.EMPTY
        self.row = coordinate[0]
        self.col = coordinate[1]
        self.span = range(2)  # placeholder value as this Node's span will be set when the Board is drawn
        self.rect = None

    def draw(self, screen: pygame.Surface, center: tuple[int, int], radius: int,
             color: tuple = constants.BLACK) -> None:
        """Draw this node on the pygame screen"""
        self.rect = pygame.draw.circle(screen, color, center, radius)
        self.span = range(self.rect.left, self.rect.right)

    def is_empty(self) -> bool:
        """Return whether this node is unfilled"""
        return self.fill == constants.EMPTY

    def __repr__(self) -> str:
        """ Representation of Node class"""
        return f'({self.coordinate}, {self.fill})'

    def find_sequence(self, player_i: player.Player, direction: str, visited: set) -> list[tuple[int, int]]:
        """Find and return the sequences of the given player's nodes in the given direction

        Note that the returned sequence does not need to be in order since we only care about its length
        """
        sequence = [self.coordinate]
        visited.add(self)
        for u in self.neighbours:
            if u not in visited and self.is_direction_neighbour(u, direction, player_i.name):
                u_sequence = u.find_sequence(player_i, direction, visited)
                sequence.extend(u_sequence)
        return sequence

    def is_direction_neighbour(self, node: Node, direction: str, player_name: int, check_fill: bool = True) -> bool:
        """Return whether node is a neighbour of this Node in the given direction for player

        if check_fill=False, then this method will not restrict the neighbour node's fill to player_name;
        additionally, more specific directions will be taken into account"""
        if check_fill is True:
            if node.fill == player_name:
                if node.col == self.col and direction == constants.VERTICAL:
                    return True
                elif node.row == self.row and direction == constants.HORIZ:
                    return True
                elif ((node.col > self.col and node.row < self.row) or (
                        node.col < self.col and node.row > self.row)) and direction == constants.TOP_RIGHT:
                    return True
                elif ((node.col < self.col and node.row < self.row) or (
                        node.col > self.col and node.row > self.row)) and direction == constants.TOP_LEFT:
                    return True
            return False
        else:
            if node.col == self.col and direction == constants.VERTICAL:
                return True
            elif node.row == self.row and direction == constants.HORIZ:
                return True
            elif (node.col > self.col and node.row < self.row) and direction == constants.UPPER_RIGHT:
                return True
            elif node.col < self.col and node.row > self.row and direction == constants.LOWER_LEFT:
                return True
            elif (node.col < self.col and node.row < self.row) and direction == constants.TOP_LEFT:
                return True
            elif node.col > self.col and node.row > self.row and direction == constants.LOWER_RIGHT:
                return True
        return False


class InputBox:
    """The InputBox object.

    Instance Attributes:
    - rect: the pygame.Rect object representing the area this InputBox occupies.
    - color: the current RGB tuple color of this InputBox's peripherals and text.
    - label_text: the label text above this InputBox
    - font: the font of the text using system default font.
    - txt_surface: a pygame surface that is the actual input box inside which the text displays.
    - active: a boolean value indicating whether this box is active.
    """
    rect: pygame.Rect
    color: tuple[int, int, int]
    label_text: str
    text: str = ''
    font: pygame.font.Font
    txt_surface: pygame.Surface
    active: bool

    def __init__(self, x_position: int, y_position: int, width: int, height: int, label_text: str) -> None:
        self.rect = pygame.Rect(x_position, y_position, width, height)
        self.color = constants.LIGHT_BLUE
        self.label_text = label_text
        self.text = ''
        self.font = pygame.font.Font(None, height)
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame event"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = constants.BLUE if self.active else constants.LIGHT_BLUE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw this InputBox and its text as well as its label"""
        # Blit the text.
        label = self.font.render(self.label_text, True, constants.YELLOW)
        screen.blit(self.txt_surface, (self.rect.x, self.rect.y))
        screen.blit(label, (self.rect.x, self.rect.y - self.rect.h))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['player', 'constants', 'pygame'],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'disable': ['R1710', 'E1101', 'R0913'],
        'max-line-length': 120
    })
