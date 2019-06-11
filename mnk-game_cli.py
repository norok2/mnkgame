import ast
from Board import Board
from BoardGravity import BoardGravity
from GameAiRandom import GameAiRandom
from GameAiSearchTree import GameAiSearchTree

board_ = Board(3, 3, 3)
# board_ = BoardGravity(6, 7, 4)


def handle_endgame(
        board,
        text,
        ask):
    result = True
    print('\n', board, sep='')
    board.reset()
    print(text)
    if ask:
        choice = input('Play a new game ([Y]/n)? ')
        if choice.strip().lower() == 'n':
            result = False
    return result


def handle_move(
        board,
        coord,
        is_computer,
        ask_continue=True):
    if is_computer:
        print('Computer Move is: ', coord)
    board.do_move(coord)
    if board.winner(board.turn) == board.turn:
        result = handle_endgame(
            board,
            'YOU LOST!\n' if is_computer else 'Congratulations! You WIN!\n',
            ask_continue)
    elif board.is_full():
        result = handle_endgame(
            board, 'The game ended in draw.\n', ask_continue)
    else:
        result = True
    return result


def get_human_move():
    is_valid = False
    coord = None
    print('Available Moves: ', sorted(board_.avail_moves()))
    while not is_valid:
        try:
            coord = ast.literal_eval(input('What is your move? ').strip())
            is_valid = \
                board_.is_valid_move(coord) and board_.is_avail_move(coord)
        except (TypeError, SyntaxError, ValueError):
            pass
    return coord


computer_plays = False
continue_game = True
while continue_game:
    print('\n', board_, sep='')
    coord_ = GameAiSearchTree().get_best_move(board_, 2.0, max_depth=-1) \
        if computer_plays else get_human_move()
    continue_game = handle_move(board_, coord_, computer_plays)
    computer_plays = not computer_plays
