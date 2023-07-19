import pytest

from chess import (
    Board, Bishop, Color, Pawn, Rook, King, Knight, InvalidMoveError
)


def test_black_pawn_moves():
    piece = Pawn(Color.Black)
    board = Board({
        (3, 1): piece,
        (2, 2): Pawn(Color.White),
        (4, 2): Pawn(Color.White)
    }) 
    moves = piece.possible_moves((3, 1), board)
    assert set(moves) == {(3, 2), (3, 3), (2, 2), (4, 2)}


def test_white_pawn_moves():
    piece = Pawn(Color.White)
    board = Board({
        (3, 6): piece,
        (2, 5): Pawn(Color.Black),
        (4, 5): Pawn(Color.Black)
    })
    moves = piece.possible_moves((3, 6), board)
    assert set(moves) == {(3, 5), (3, 4), (2, 5), (4, 5)}


@pytest.mark.parametrize("color", [Color.White, Color.Black])
def test_blocked_pawn(color):
    piece = Pawn(Color.Black)
    board = Board({
        (3, 1): piece,
        (3, 2): Pawn(color),
    })
    assert [] == piece.possible_moves((3, 1), board)


# TODO: Parametrize
def test_move_pawn():
    board = Board({(2, 6): Pawn(Color.White)})
    board = board.move(Color.White, "c3")
    assert board.get_piece_at((2, 5)) == Pawn(Color.White)
    assert board.get_piece_at((2, 6)) == None


def test_record_moves():
    board = Board({(2, 6): Pawn(Color.White)})
    move_len = len(board.moves)
    board = board.move(Color.White, "c3")
    assert len(board.moves) == move_len + 1


def test_move_rook():
    board = Board({(0, 0): Rook(Color.Black)})
    board = board.move(Color.Black, "Re8")
    assert board.get_piece_at((4, 0)) == Rook(Color.Black)
    board = board.move(Color.Black, "Re1")
    assert board.get_piece_at((4, 7)) == Rook(Color.Black)


def test_blocked_rook():
    board = Board({
        (0, 0): Rook(Color.Black),
        (3, 0): Pawn(Color.Black),
        (0, 4): Rook(Color.White)
    })
    with pytest.raises(InvalidMoveError):
        board.move(Color.Black, "Re8")
    with pytest.raises(InvalidMoveError):
        board.move(Color.Black, "Ra1")


def test_rook_capture():
    board = Board({
        (0, 0): Rook(Color.Black),
        (0, 6): Pawn(Color.White),
    })
    board = board.move(Color.Black, "Ra2")
    assert board.get_piece_at((0, 6)) == Rook(Color.Black)


@pytest.mark.parametrize("start, move", [
    ((1, 0), "Na6"),
    ((1, 0), "Nc6"),
    ((2, 2), "Nb8"),
    ((2, 2), "Nd8"),
    ((2, 2), "Na7"),
    ((2, 2), "Na5"),
    ((2, 2), "Ne7"),
    ((2, 2), "Ne5"),
    ((2, 2), "Nb4"),
    ((2, 2), "Nd4"),
])
def test_knight_move(start, move):
    board = Board({ start: Knight(Color.Black) })
    board.move(Color.Black, move)


def test_blocked_knight():
    board = Board({
        (1, 0): Knight(Color.Black),
        (3, 1): Pawn(Color.Black) 
    })

    with pytest.raises(InvalidMoveError):
        board.move(Color.Black, "Nd7")


@pytest.mark.parametrize("start, move", [
    ((2, 2), "Ba8"),
    ((2, 2), "Bd5"),
])
def test_bishop(start, move):
    board = Board({ start: Bishop(Color.Black) })
    board.move(Color.Black, move)


def test_castling():
    board = Board({
        (0, 0): Rook(Color.Black),
        (4, 0): King(Color.Black),
        (7, 0): Rook(Color.Black),
    })
    kingside = board.move(Color.Black, "0-0")
    assert kingside.get_piece_at((2, 0)) == King(Color.Black)
    assert kingside.get_piece_at((3, 0)) == Rook(Color.Black)
    queenside = board.move(Color.Black, "0-0-0")
    assert queenside.get_piece_at((6, 0)) == King(Color.Black)
    assert queenside.get_piece_at((5, 0)) == Rook(Color.Black)


def test_castling_not_available():
    board = Board({
        (0, 0): Rook(Color.Black),
        (4, 0): King(Color.Black),
    })
    moved_rook = board.move(Color.Black, "Ra7")\
        .move(Color.Black, "Ra8")
    with pytest.raises(InvalidMoveError):
        moved_rook.move(Color.Black, "0-0")

@pytest.mark.parametrize("color", [Color.Black, Color.White])
def test_castling_blocked_by_piece(color):
    board = Board({
        (0, 0): Rook(Color.Black),
        (1, 0): Bishop(color),
        (4, 0): King(Color.Black),
    })
    with pytest.raises(InvalidMoveError):
        board.move(Color.Black, "0-0")
    
@pytest.mark.parametrize("position", [(7, 2), (7, 3), (7, 4)])
def test_castling_blocked_by_attack(position):
    board = Board({
        (0, 0): Rook(Color.Black),
        (4, 0): King(Color.Black),
        position: Rook(Color.White),
    })
    with pytest.raises(InvalidMoveError):
        board.move(Color.Black, "0-0")
