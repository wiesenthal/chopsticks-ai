# a hand is an int either 0, 1, 2, 3, 4
def is_alive(hand):
    return hand != 0


def add(hand1, hand2):
    return (hand1 + hand2) % 5


def is_valid_input(move):
    if move.count(' ') != 1:
        return False
    chosen_hand, action = parse_move(move)
    if chosen_hand not in ("left", "right"):
        return False
    if action not in ("left", "right", "split"):
        return False
    return True


def parse_move(move):
    return move.split(' ')


class Player:
    def __init__(self, name):
        self.name = name
        self.left_hand = 1
        self.right_hand = 1

    @property
    def is_alive(self):
        return is_alive(self.left_hand) or is_alive(self.right_hand)

    def get_move(self, game):
        # present the state of the game to player
        prompt = "Make a move. Enter either left or right to select your hand, then a space, then left or " \
                 "right to select which of your opponents hands to attack. Instead of stating which opponent " \
                 "hand you may instead put split, to split your selected hand in half (so long as it is your " \
                 "only hand, and it is even).\n"
        move = input(prompt)
        while not is_valid_input(move):
            # input should be in the format of left/right left/right/split
            print("Invalid input.")
            move = input(prompt)
        return move

    def set_hand(self, hand, value):
        if hand == "left":
            self.left_hand = value
        else:
            self.right_hand = value

    def get_hand(self, hand):
        return self.left_hand if hand == "left" else self.right_hand

    def copy(self):
        new_player = Player(self.name)
        new_player.left_hand = self.left_hand
        new_player.right_hand = self.right_hand
        return new_player

    def __str__(self):
        return str(self.left_hand) + " " + str(self.right_hand)

    def __repr__(self):
        return repr(self.left_hand) + " " + repr(self.right_hand)


def get_possible_moves(attacker, defender):
    possible_moves = []
    if is_alive(attacker.left_hand):
        if is_alive(defender.left_hand):
            possible_moves.append("left left")
        if is_alive(defender.right_hand):
            possible_moves.append("left right")
    elif attacker.right_hand % 2 == 0:
        possible_moves.append("right split")
    if is_alive(attacker.right_hand):
        if is_alive(defender.left_hand):
            possible_moves.append("right left")
        if is_alive(defender.right_hand):
            possible_moves.append("right right")
    elif attacker.left_hand % 2 == 0:
        possible_moves.append("left split")
    return possible_moves


WON_STATES = {}
LOST_STATES = {}
DEPTH_LIMIT = 10


def maximize(game, my_name, opponent_name, depth=0):
    winner = game.get_winner()
    if winner is not None:
        return ("", 1) if winner == my_name else ("", -1)
    best_move = "empty"
    max_value = -2
    all_moves = get_possible_moves(game.get_player(my_name), game.get_player(opponent_name))
    for potential_move in all_moves:
        # only copy attacker if splitting
        temp_game = game.copy()
        temp_game.execute_move(my_name, opponent_name, potential_move)
        if depth > DEPTH_LIMIT or temp_game.is_loop():
            my_value = 0
        else:
            temp_game.store_state()
            opponent_move, opponents_value = maximize(temp_game, opponent_name, my_name, depth + 1)
            my_value = opponents_value * -1
        if my_value == 1:
            return potential_move, my_value
        if my_value > max_value:
            max_value = my_value
            best_move = potential_move

    return best_move, max_value


class AI(Player):
    def get_move(self, game):
        opponent = game.player1 if game.player2 == self else game.player2
        my_move, value = maximize(game, self.name, opponent.name)
        return my_move


def compress_state(p1_left_hand, p1_right_hand, p2_left_hand, p2_right_hand):
    return repr(p1_left_hand) + repr(p1_right_hand) + \
           repr(p2_left_hand) + repr(p2_right_hand)


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.seen_states = set()  # for caching

    def store_state(self):
        states = self.compress_all()
        self.seen_states.update(states)

    def main(self):
        # keep giving players turns until one dies
        attacker = self.player1
        defender = self.player2

        while self.player1.is_alive and self.player2.is_alive:
            print(f"** {attacker.name}'s turn. **")
            print(self)
            move = attacker.get_move(self)
            while not self.is_valid_move(attacker, move):
                print("Move cannot be made according to the game rules.")
                move = attacker.get_move(self)
            self.execute_move(attacker.name, defender.name, move)
            self.store_state()
            attacker, defender = defender, attacker

        winner = self.get_winner()
        print(f"{winner} is victorious!")

    def get_winner(self):
        if self.player1.is_alive and self.player2.is_alive:
            return None
        return self.player1.name if self.player1.is_alive else self.player2.name

    def compress(self):
        return compress_state(self.player1.left_hand, self.player1.right_hand, self.player2.left_hand,
                              self.player2.right_hand)

    def is_loop(self):
        return self.compress() in self.seen_states

    def is_valid_move(self, player, move):
        if player not in (self.player1, self.player2):
            raise Exception("Bad player argument.")
        attacker = player
        defender = self.player1 if player == self.player2 else self.player2
        hand_choice, action = parse_move(move)
        attack_hand = attacker.left_hand if hand_choice == "left" else attacker.right_hand
        off_hand = attacker.right_hand if hand_choice == "left" else attacker.left_hand
        if not is_alive(attack_hand):
            return False
        if (action == "left" and not is_alive(defender.left_hand)) \
                or (action == "right" and not is_alive(defender.right_hand)):
            return False
        if action == "split" and (attack_hand % 2 != 0 or is_alive(off_hand)):
            return False
        return True

    def get_player(self, name):
        return self.player1 if name == self.player1.name else self.player2

    def copy(self):
        new_game = Game(self.player1.copy(), self.player2.copy())
        new_game.seen_states = self.seen_states.copy()
        return new_game

    def execute_move(self, attacker_name, defender_name, move):
        hand_choice, action = parse_move(move)
        attacker = self.get_player(attacker_name)
        defender = self.get_player(defender_name)
        attack_hand = attacker.get_hand(hand_choice)
        off_hand = "right" if hand_choice == "left" else "left"
        if action == "split":
            new_value = attack_hand // 2
            attacker.set_hand(hand_choice, new_value)
            attacker.set_hand(off_hand, new_value)
        else:
            defend_hand = defender.get_hand(action)
            defender.set_hand(action, add(defend_hand, attack_hand))

    def compress_all(self):
        equivalent_states = {compress_state(self.player1.left_hand, self.player1.right_hand,
                                            self.player2.left_hand, self.player2.right_hand),
                             compress_state(self.player1.left_hand, self.player1.right_hand,
                                            self.player2.right_hand, self.player2.left_hand),
                             compress_state(self.player1.right_hand, self.player1.left_hand,
                                            self.player2.left_hand, self.player2.right_hand),
                             compress_state(self.player1.right_hand, self.player1.left_hand,
                                            self.player2.right_hand, self.player2.left_hand),
                             compress_state(self.player2.left_hand, self.player2.right_hand,
                                            self.player1.left_hand, self.player1.right_hand),
                             compress_state(self.player2.left_hand, self.player2.right_hand,
                                            self.player1.right_hand, self.player1.left_hand),
                             compress_state(self.player2.right_hand, self.player2.left_hand,
                                            self.player1.left_hand, self.player1.right_hand),
                             compress_state(self.player2.right_hand, self.player2.left_hand,
                                            self.player1.right_hand, self.player1.left_hand)}
        return equivalent_states

    def __str__(self):
        return self.player1.name + ": " + str(self.player1) + '\n' \
               + self.player2.name + ": " + str(self.player2)


def main():
    # Names must be unique
    name1 = input("Enter first player name: ")
    name2 = input("Enter second player name: ")
    while name1 == name2:
        print("Try again. Names must be distinct.")
        name1 = input("Enter first player name: ")
        name2 = input("Enter second player name: ")
    p1 = AI(name1)
    p2 = Player(name2)
    game = Game(p1, p2)
    game.main()


if __name__ == "__main__":
    main()
