class Hand:
    # a hand has a state of 0, 1, 2, 3 or 4
    def __init__(self, value=1):
        self.value = value

    @property
    def is_alive(self):
        return self.value != 0

    def add(self, other):
        self.value = (self.value + other.value) % 5

    def __add__(self, other):
        if isinstance(other, Hand):
            return Hand((self.value + other.value) % 5)
        elif isinstance(other, int):
            return Hand((self.value + other) % 5)
        else:
            raise TypeError(str(type(other)) + " is invalid to add with Hand.")

    def __sub__(self, other):
        if isinstance(other, Hand):
            return Hand((self.value - other.value) % 5)
        elif isinstance(other, int):
            return Hand((self.value - other) % 5)
        else:
            raise TypeError(str(type(other)) + " is invalid to add with Hand.")

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        # return '/' * self.value
        return repr(self)


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
        self.left_hand = Hand()
        self.right_hand = Hand()

    @property
    def is_alive(self):
        return self.right_hand.is_alive or self.left_hand.is_alive

    def get_move(self, game):
        # present the state of the game to player
        print(game)
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

    def __str__(self):
        return str(self.left_hand) + " " + str(self.right_hand)

    def __repr__(self):
        return repr(self.left_hand) + " " + repr(self.right_hand)


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.seen_states = set()  # for caching

    def store_state(self):
        # compress players into a state:
        #   player 1 left hand, player 1 right hand, player 2 left hand, player 3 right hand
        state = repr(self.player1.left_hand) + repr(self.player1.right_hand) + \
                repr(self.player2.left_hand) + repr(self.player2.right_hand)
        self.seen_states.add(state)

    def main(self):
        # keep giving players turns until one dies
        attacker = self.player1
        defender = self.player2

        while self.player1.is_alive and self.player2.is_alive:
            print(f"** {attacker.name}'s turn. **")
            move = attacker.get_move(self)
            while not self.is_valid_move(attacker, move):
                print("Move cannot be made according to the game rules.")
                move = attacker.get_move(self)
            self.execute_move(attacker, defender, move)
            self.store_state()
            attacker, defender = defender, attacker

        winner = self.player1.name if self.player1.is_alive else self.player2.name
        print(f"{winner} is victorious!")

    def is_valid_move(self, player, move):
        if player not in (self.player1, self.player2):
            raise Exception("Bad player argument.")
        attacker = player
        defender = self.player1 if player == self.player2 else self.player2
        hand_choice, action = parse_move(move)
        attack_hand = attacker.left_hand if hand_choice == "left" else attacker.right_hand
        off_hand = attacker.right_hand if attack_hand == attacker.left_hand else attacker.left_hand
        if not attack_hand.is_alive:
            return False
        if (action == "left" and not defender.left_hand.is_alive) \
                or (action == "right" and not defender.right_hand.is_alive):
            return False
        if action == "split" and (attack_hand.value % 2 != 0 or off_hand.is_alive):
            return False
        return True

    def execute_move(self, attacker, defender, move):
        hand_choice, action = parse_move(move)
        attack_hand = attacker.left_hand if hand_choice == "left" else attacker.right_hand
        off_hand = attacker.right_hand if attack_hand == attacker.left_hand else attacker.left_hand
        if action == "split":
            new_value = attack_hand.value // 2
            attack_hand.value = new_value
            off_hand.value = new_value
        else:
            defend_hand = defender.left_hand if action == "left" else defender.right_hand
            defend_hand.add(attack_hand)

    def __str__(self):
        return self.player1.name + ": " + str(self.player1) + '\n'\
               + self.player2.name + ": " + str(self.player2)


def main():
    p1 = Player(input("Enter first player name: "))
    p2 = Player(input("Enter second player name: "))
    game = Game(p1, p2)
    game.main()


if __name__ == "__main__":
    main()
