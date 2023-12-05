import socket
import struct
import json
import random
import numpy as np

from muzero import create_model

def convert_move_for_server(move, color):
    # Dummy conversion for demonstration purposes
    col = color
    message = {"from": position(move[0], move[1]), "to": position(move[2], move[3]), "turn": col}
    return json.dumps(message)

def is_white(color):
    if color.upper() in ["WHITE", "W", "w", "white", "White"]:
        return True
    return False

def is_black(color):
    if color.upper() in ["BLACK", "B", "b", "black", "Black"]:
        return True
    return False

def is_empty(cell):
    if cell.upper() in ["empty", "EMPTY", "Empty", "E"]:
        return True
    return False

def get_valid_moves(matrix, row_curr, col_curr, color):
    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    empty_cells = []

    for d_row, d_col in directions:
        row, col = row_curr + d_row, col_curr + d_col

        while is_valid_cell(row, col):
            if is_empty(matrix[row][col]):
                if (row, col) in citadels() and (row_curr, col_curr) not in citadels():
                    break
                if is_white(color):
                    if (row, col) not in citadels():
                        empty_cells.append((row, col))
                else:
                    if (row, col) not in citadels() or citadels(True, row, col, row_curr, col_curr):
                        empty_cells.append((row, col))
                row += d_row
                col += d_col
            else:
                break

    return empty_cells

def is_valid_cell(row= 0, col= 0):
    if col >= 0 and col < 9 and row >= 0 and row < 9:
        return True
    else:
        return False

def citadels(is_black= False, row= -1, col= -1, pawn_row= -1, pawn_col= -1):
    #citadel I4 I5 I6 H5 D1 E1 F1 E2 A4 A5 A6 B5 D9 E9 F9 E8
    section1 = [(8, 3), (8, 4), (8, 5), (7, 4)]
    section2 = [(3, 0), (4, 0), (5, 0), (4, 1)]
    section3 = [(0, 3), (0, 4), (0, 5), (1, 4)]
    section4 = [(3, 8), (4, 8), (5, 8), (4, 7)]
    alls = section1 + section2 + section3 + section4
    if is_black:
        if (pawn_row, pawn_col) in section1 and (row, col) in section1:
            return True
        elif (pawn_row, pawn_col) in section2 and (row, col) in section2:
            return True
        elif (pawn_row, pawn_col) in section3 and (row, col) in section3:
            return True
        elif (pawn_row, pawn_col) in section4 and (row, col) in section4:
            return True
        else:
            return False
    else:
        return alls

def position(row, col):
    alphabets = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    return str(alphabets[int(col)]) + str(int(row) + 1)

#random player for now
def my_ai_logic(board_state, color):
    # Convert the board state string to a 2D list (if necessary)
    board = board_state

    # Lists to keep track of valid pawns and moves
    valid_pawns = []
    valid_moves = []

    # Collect valid pawns
    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):
            if (is_white(color) and is_white(cell)) or (is_black(color) and is_black(cell)):
                valid_pawns.append((row_index, col_index))

    # If no valid pawns were found, return no move
    if not valid_pawns:
        return None

    row, col = 0, 0
    # Select a random pawn
    while len(valid_moves) == 0:
        selected_pawn = random.choice(valid_pawns)
        row, col = selected_pawn

        # Check all possible directions and collect valid moves
        valid_moves = get_valid_moves(board_state, row, col, color)


    # Select a random valid move for the chosen pawn
    selected_move = random.choice(valid_moves)

    # Convert board positions to the server's format
    from_position = position(row, col)
    to_position = position(*selected_move)

    return [from_position, to_position]


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        except ConnectionResetError:
            print("Connection was closed by the server.")
            return None
    return data

def change_board(board, color):
	vecC = {"WHITE": 1, "KING": 2, "EMPTY": 0, "BLACK": -1, "THRONE": 0}

	return np.array([[vecC[char] for char in sublist] for sublist in board])



def main(player_name, color, timeout= 60, host = 'localhost'):
    
    port = 5800 if is_white(color) else 5801

    model = create_model()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))

        # Send player name to the server
        sock.sendall(struct.pack('>i', len(player_name)))
        sock.sendall(player_name.encode())

        while True:
            # Receive current state from the server
            len_bytes = recvall(sock, 4)
            if len_bytes is None:
                print("Connection closed by the server or recvall error.")
                break  # Exit the loop if recvall returned None

            # Ensure we have received 4 bytes before unpacking
            if len(len_bytes) == 4:
                message_length = struct.unpack('>i', len_bytes)[0]
                state_json_bytes = recvall(sock, message_length)
                if state_json_bytes is None:
                    print("Connection closed by the server or recvall error.")
                    break  # Exit the loop if recvall returned None

                state_json = state_json_bytes.decode('utf-8')
                game_state = json.loads(state_json)

                # Check whose turn it is
                current_turn = game_state['turn']
                if (is_white(color) and not is_white(current_turn)) or (is_black(color) and not is_black(current_turn)):
                    continue

                # Get the board state and calculate the next move
                board_state = game_state['board']
                newBoard = change_board(board_state, color)
                move = model.make_move(position=newBoard, player=color)

                # Convert the move to the server's format and send it
                move_for_server = convert_move_for_server(move, color)
                sock.sendall(struct.pack('>i', len(move_for_server)))
                sock.sendall(move_for_server.encode())

            else:
                print("Did not receive enough data for message length.")
                break

    print("Exiting the game...")
    sock.close()



