import re
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

class InvalidMoveError(Exception):
    pass

Position = tuple[int, int]

class Color(Enum):
    Black = "Black"
    White = "White"

    def opponent(self):
        return Color.Black if self == Color.White else Color.White

@dataclass
class Move:
    name: str
    dest: Position

@dataclass
class Castle:
    kingside: bool


class Piece(ABC):
    color: Color
    name: str

    def __init__(self, color: Color):
        self.color = color

    @abstractmethod
    def possible_moves(self, position, board):
        raise NotImplementedError()

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.color == other.color and self.name == other.name

@dataclass
class Board:
    pieces: dict[Position, Piece]
    moves: list[tuple[Color, Move]]

    def __init__(self, pieces=None, moves=None):
        self.moves = moves or []
        self.pieces: dict[Position, Piece] = pieces or {
            (0, 0): Rook(Color.Black),
            (1, 0): Knight(Color.Black),
            (2, 0): Bishop(Color.Black),
            (3, 0): Queen(Color.Black),
            (4, 0): King(Color.Black),
            (5, 0): Knight(Color.Black),
            (6, 0): Bishop(Color.Black),
            (7, 0): Rook(Color.Black),
            (0, 1): Pawn(Color.Black),
            (1, 1): Pawn(Color.Black),
            (2, 1): Pawn(Color.Black),
            (3, 1): Pawn(Color.Black),
            (4, 1): Pawn(Color.Black),
            (5, 1): Pawn(Color.Black),
            (6, 1): Pawn(Color.Black),
            (7, 1): Pawn(Color.Black),
            (0, 6): Pawn(Color.Black),
            (1, 6): Pawn(Color.White),
            (2, 6): Pawn(Color.White),
            (3, 6): Pawn(Color.White),
            (4, 6): Pawn(Color.White),
            (5, 6): Pawn(Color.White),
            (6, 6): Pawn(Color.White),
            (7, 6): Pawn(Color.White),
            (0, 7): Rook(Color.White),
            (1, 7): Knight(Color.White),
            (2, 7): Bishop(Color.White),
            (3, 7): Queen(Color.White),
            (4, 7): King(Color.White),
            (5, 7): Knight(Color.White),
            (6, 7): Bishop(Color.White),
            (7, 7): Rook(Color.White),
        }

    def __str__(self):
        rows = []
        for y in range(8):
            row = []
            for x in range(8):
                if piece := self.get_piece_at((x, y)):
                    name = piece.name
                    if piece.color == Color.White:
                        name = name.lower()
                    row.append(name)
                else:
                    row.append(".")
            rows.append("".join(row))
        return "\n".join(rows)

#     @classmethod
#     def from_str(string):
#         for row in string.split("\n"):
#             for c in row:
#                 if c == ""

    def get_piece_at(self, position: Position):
        return self.pieces.get(position)

    def is_blocked(self, color, position):
        if piece := self.get_piece_at(position):
            if piece.color == color:
                return True
        return False

    def is_attacked_by(self, color, position):
        for (pos, piece) in self.pieces.items():
            if piece.color == color:
                if position in piece.possible_moves(pos, self):
                    return True
        return False

    def can_castle(self, color, kingside) -> bool:
        rank = 0 if color.Black else 7
        free_files = [5, 6] if kingside else [1, 2, 3]
        for file in free_files:
            if self.get_piece_at((file, rank)):
                return False
        not_attacked_files = [4, 5, 6, 7] if kingside else [0, 1, 2, 3, 4]
        for file in not_attacked_files:
            if self.is_attacked_by(color.opponent(), (file, rank)):
                return False
        # NOTE: We check whether castling is possible by checking if
        # neither king nor rook has moved. Since there are two rooks,
        # and they can move back to their original positions we check
        # if the rook is in its original position *and* that no piece
        # has moved *to* that position.
        original_rook_position = (7 if kingside else 0, rank)
        if self.get_piece_at(original_rook_position) != Rook(Color.Black):
            return False
        for color, move in self.moves:
            if color == color:
                if move.name == "K":
                    return False
                if move.dest == original_rook_position:
                    return False
        return True

    @classmethod
    def move_piece(cls, pieces, src, dest):
        updated_pieces = dict(pieces)
        updated_pieces[dest] = updated_pieces.pop(src)
        return updated_pieces

    def castle(self, color: Color, move: Castle):
        kingside = move.kingside
        if not self.can_castle(color, kingside):
            raise InvalidMoveError("Can't castle from this position")
        rank = 0 if color.Black else 7
        original_rook_position = (7 if kingside else 0, rank)
        original_king_position = (4, rank)
        new_rook_position = (5 if kingside else 3, rank)
        new_king_position = (6 if kingside else 2, rank)
        pieces = Board.move_piece(self.pieces, original_king_position, new_king_position)
        pieces = Board.move_piece(pieces, original_rook_position, new_rook_position)
        return Board(pieces=pieces, moves=self.moves + [(color, move)])

    # TODO: Move disambiguation
    def move(self, color: Color, move: str):
        m = parse_move(move)
        if isinstance(m, Castle):
            return self.castle(color, m)
        matching_positions: list[Position] = []
        for (pos, piece) in self.pieces.items():
            if piece.color == color and piece.name == m.name:
                if m.dest in piece.possible_moves(pos, self):
                    matching_positions.append(pos)
        if not matching_positions:
            raise InvalidMoveError("No matching piece found")
        if not len(matching_positions) == 1:
            raise InvalidMoveError("Ambiguous move")
        [pos] = matching_positions
        pieces = Board.move_piece(self.pieces, pos, m.dest)
        return Board(pieces=pieces, moves=self.moves + [(color, m)])


class Pawn(Piece):
    name = "P"

    # TODO: En passant captures
    # TODO: Promotion

    # NB: Whether a pawn has moved can be determined by checking if
    # it's still in its starting rank
    def has_moved(self, position):
        if self.color == Color.Black and position[1] == 1:
            return False
        elif position[1] == 6:
            return False
        return True

    def possible_moves(self, position, board):
        direction = 1 if self.color == Color.Black else -1
        moves = []
        x, y = position[0], position[1]
        if not board.get_piece_at((x, y + direction)):
            moves.append((x, y + direction))
            if not self.has_moved(position):
                moves.append((x, y + direction * 2))
        capture_moves = [
            (x + direction, y + direction),
            (x - direction, y + direction),
        ]
        for m in capture_moves:
            if piece := board.get_piece_at(m):
                if piece.color != self.color:
                    moves.append(m)
        return moves

straight_moves = [
    lambda i: (+i, 0),
    lambda i: (-i, 0),
    lambda i: (0, +i),
    lambda i: (0, -i),
]

diagonal_moves = [
    lambda i: (+i, +i),
    lambda i: (+i, -i),
    lambda i: (-i, +i),
    lambda i: (-i, -i),
]

def filter_moves(position, color, direction_fns, board):
    moves = []
    for df in direction_fns:
        for d in map(df, range(8)):
            pos = position[0] + d[0], position[1] + d[1]
            if pos == position or is_out_of_bounds(pos):
                continue
            if piece := board.get_piece_at(pos):
                if piece.color != color:
                    moves.append(pos)
                break
            else:
                moves.append(pos)
    return moves

class Rook(Piece):
    name = "R"

    def possible_moves(self, position, board):
        return filter_moves(position, self.color, straight_moves, board)
        # x, y = position[0], position[1]
        # directions = [
        #     [(x + i, y) for i in range(x, 8)],
        #     [(x - i, y) for i in range(8 - x, 8)],
        #     [(x, y + i) for i in range(y, 8)],
        #     [(x, y - i) for i in range(8 - y, 8)],
        # ]
        # moves = []
        # for d in directions:
        #     for pos in d:
        #         if pos == position:
        #             continue
        #         if piece := board.get_piece_at(pos):
        #             if piece.color != self.color:
        #                 moves.append(pos)
        #             break
        #         else:
        #             moves.append(pos)
        # return moves

def is_out_of_bounds(position: Position):
    for i in range(2):
        if not 0 <= position[i] < 8:
            return True
    return False


class Knight(Piece):
    name = "N"

    def possible_moves(self, position, board):
        x, y = position[0], position[1]
        all_moves = [
            (x - 1, y - 2),
            (x + 1, y - 2),
            (x + 2, y - 1),
            (x + 2, y + 1),
            (x + 1, y + 2),
            (x - 1, y + 2),
            (x - 2, y - 1),
            (x - 2, y + 1),
        ]
        moves = []
        for m in all_moves:
            if not is_out_of_bounds(m) and not board.is_blocked(self.color, m):
                moves.append(m)
        return moves


class Bishop(Piece):
    name = "B"

    def possible_moves(self, position, board):
        return filter_moves(position, self.color, diagonal_moves, board)


class King(Piece):
    name = "K"

    def possible_moves(self, position, board):
        x, y = position[0], position[1]
        moves = []
        for fn in straight_moves + diagonal_moves:
            dx, dy = fn(1)
            m = (x + dx, y + dy)
            if not is_out_of_bounds(m) and not board.is_blocked(self.color, m):
                moves.append(m)
        return moves


class Queen(Piece):
    name = "Q"

    def possible_moves(self, position, board):
        move_fns = diagonal_moves + straight_moves
        return filter_moves(position, self.color, move_fns, board)


# TODO: Disambiguating moves
# TODO: Promotion
# TODO: Castling
def parse_move(move: str):
    if move == "0-0" or move == "0-0-0":
        return Castle(kingside=move == "0-0")
    piece = "Q|R|N|B|K"
    files = "87654321"
    ranks = "abcdefgh"
    match = re.match("(" + piece + "?)x?([a-h])([1-8])", move)
    if not match:
        raise InvalidMoveError(f"Invalid move: {move}")
    dest = (
        ranks.index(match.group(2)),
        files.index(match.group(3)),
    )
    return Move(name=match.group(1) or "P", dest=dest)
