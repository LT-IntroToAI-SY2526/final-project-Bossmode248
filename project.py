import itertools
import random

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
RANK_VALUES = {r: i for i, r in enumerate(RANKS, start=2)}
HAND_NAMES = [
    'High Card',
    'One Pair',
    'Two Pair',
    'Three of a Kind',
    'Straight',
    'Flush',
    'Full House',
    'Four of a Kind',
    'Straight Flush',
    'Royal Flush',
]

CASINO_START_CHIPS = 1000
MIN_ANTE = 50
MAX_OPPONENTS = 3


class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit}"

    def to_ascii(self) -> list[str]:
        rank = self.rank.rjust(2)
        return [
            '┌─────────┐',
            f'|{rank}       |',
            '|         |',
            f'|    {self.suit}    |',
            '|         |',
            f'|       {rank}|',
            '└─────────┘',
        ]


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, count: int = 1) -> list[Card]:
        return [self.cards.pop() for _ in range(count)]


class Player:
    def __init__(self, name: str, chips: int = CASINO_START_CHIPS):
        self.name = name
        self.chips = chips
        self.hand: list[Card] = []
        self.best_hand: list[Card] = []

    def __repr__(self) -> str:
        return f"{self.name} ({self.chips} chips)"

    def adjust_chips(self, amount: int) -> None:
        self.chips += amount


def _is_consecutive(ranks: list[int]) -> bool:
    unique_ranks = sorted(set(ranks), reverse=True)
    if len(unique_ranks) != 5:
        return False
    if unique_ranks == [14, 5, 4, 3, 2]:
        return True
    return unique_ranks[0] - unique_ranks[-1] == 4 and len(unique_ranks) == 5


def evaluate_five_card_hand(cards: list[Card]) -> tuple[int, list[int]]:
    ranks = sorted([card.value for card in cards], reverse=True)
    suits = [card.suit for card in cards]
    is_flush = len(set(suits)) == 1
    is_straight = _is_consecutive(ranks)

    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
    counts = sorted(rank_counts.values(), reverse=True)
    sorted_by_count = sorted(rank_counts.items(), key=lambda item: (-item[1], -item[0]))
    ordered_ranks = [rank for rank, count in sorted_by_count for _ in range(count)]

    if is_flush and is_straight:
        if ranks == [14, 13, 12, 11, 10]:
            return 9, ranks
        return 8, ranks
    if counts == [4, 1]:
        return 7, ordered_ranks
    if counts == [3, 2]:
        return 6, ordered_ranks
    if is_flush:
        return 5, ranks
    if is_straight:
        return 4, ranks
    if counts == [3, 1, 1]:
        return 3, ordered_ranks
    if counts == [2, 2, 1]:
        return 2, ordered_ranks
    if counts == [2, 1, 1, 1]:
        return 1, ordered_ranks
    return 0, ranks


def best_hand_of_seven(cards: list[Card]) -> tuple[tuple[int, list[int]], tuple[Card, ...]]:
    best_rank = (-1, [])
    best_combo: tuple[Card, ...] | None = None
    for combo in itertools.combinations(cards, 5):
        rank = evaluate_five_card_hand(list(combo))
        if rank > best_rank:
            best_rank = rank
            best_combo = combo
    return best_rank, best_combo or tuple(cards[:5])


def format_hand(cards: list[Card]) -> str:
    return ' '.join(str(card) for card in cards)


def print_cards(cards: list[Card]) -> None:
    ascii_lines = [''] * 7
    for card in cards:
        shape = card.to_ascii()
        for i, line in enumerate(shape):
            ascii_lines[i] += line + ' '
    print('\n'.join(ascii_lines))


def compare_hands(rank_a: tuple[int, list[int]], rank_b: tuple[int, list[int]]) -> str:
    if rank_a > rank_b:
        return 'Player'
    if rank_b > rank_a:
        return 'Dealer'
    return 'Tie'


def prompt_choice(prompt: str, options: dict[str, str]) -> str:
    print(prompt)
    for number, option in options.items():
        print(f'{number}. {option}')
    while True:
        choice = input('> ').strip()
        if choice in options:
            return choice
        print('Invalid choice, try again.')


def prompt_integer(prompt: str, minimum: int, maximum: int) -> int:
    while True:
        try:
            value = int(input(f'{prompt} '))
            if minimum <= value <= maximum:
                return value
        except ValueError:
            pass
        print(f'Please enter a number between {minimum} and {maximum}.')


def ask_keep_positions() -> set[int]:
    keep = input('\nEnter card positions to keep (e.g. 1 3 5), or press Enter to draw all: ').strip()
    keep_positions: set[int] = set()
    if keep:
        for pos in keep.split():
            if pos.isdigit() and 1 <= int(pos) <= 5:
                keep_positions.add(int(pos) - 1)
    return keep_positions


def opponent_draw_positions(hand: list[Card]) -> set[int]:
    rank_counts = {card.value: sum(c.value == card.value for c in hand) for card in hand}
    keep_values = {value for value, count in rank_counts.items() if count >= 2}
    keep_positions = {idx for idx, card in enumerate(hand) if card.value in keep_values}
    if len(keep_positions) == 0:
        keep_positions = {idx for idx in range(2)}
    return keep_positions


def settle_pot(player: Player, opponents: list[Player], player_rank: tuple[int, list[int]], opponent_ranks: list[tuple[int, list[int]]], pot: int) -> None:
    winners: list[Player] = []
    best_rank = player_rank
    for rank in opponent_ranks:
        if rank > best_rank:
            best_rank = rank
    if player_rank == best_rank:
        winners.append(player)
    for rank, opponent in zip(opponent_ranks, opponents):
        if rank == best_rank:
            winners.append(opponent)

    share = pot // len(winners)
    for winner in winners:
        winner.adjust_chips(share)

    if player in winners:
        if len(winners) == 1:
            print(f'You win {share - MIN_ANTE} chips!')
        else:
            print(f'You split the pot and receive {share} chips!')
    else:
        print('You lost the round.')

    print(f'Pot was {pot} chips. {len(winners)} winner(s) split it.')


def play_five_card_draw(player: Player, opponents: list[Player]) -> None:
    deck = Deck()
    player.hand = deck.deal(5)
    for opponent in opponents:
        opponent.hand = deck.deal(5)

    print('\n--- Five-Card Draw ---')
    print('\nYour hand:')
    print_cards(player.hand)

    keep_positions = ask_keep_positions()
    player_draw_count = 5 - len(keep_positions)
    player.hand = [card for idx, card in enumerate(player.hand) if idx in keep_positions] + deck.deal(player_draw_count)

    for opponent in opponents:
        opponent_keep = opponent_draw_positions(opponent.hand)
        opponent.hand = [card for idx, card in enumerate(opponent.hand) if idx in opponent_keep]
        opponent.hand += deck.deal(5 - len(opponent.hand))

    player_rank = evaluate_five_card_hand(player.hand)
    opponent_ranks = [evaluate_five_card_hand(opponent.hand) for opponent in opponents]

    print('\nFinal player hand:')
    print_cards(player.hand)
    print(f'{HAND_NAMES[player_rank[0]]}: {format_hand(player.hand)}')

    for opponent, rank in zip(opponents, opponent_ranks):
        print(f'\n{opponent.name} hand:')
        print_cards(opponent.hand)
        print(f'{HAND_NAMES[rank[0]]}: {format_hand(opponent.hand)}')

    round_players = 1 + len(opponents)
    pot = MIN_ANTE * round_players
    player.adjust_chips(-MIN_ANTE)
    for opponent in opponents:
        opponent.adjust_chips(-MIN_ANTE)

    settle_pot(player, opponents, player_rank, opponent_ranks, pot)


def play_texas_holdem(player: Player, opponents: list[Player]) -> None:
    deck = Deck()
    player.hand = deck.deal(2)
    for opponent in opponents:
        opponent.hand = deck.deal(2)

    community_cards: list[Card] = []
    print('\n--- Texas Hold\'em ---')
    print('\nYour pocket cards:')
    print_cards(player.hand)

    for stage, count in [('Flop', 3), ('Turn', 1), ('River', 1)]:
        input(f'Press Enter to deal the {stage}...')
        community_cards += deck.deal(count)
        print(f'\nCommunity cards after the {stage}:')
        print_cards(community_cards)

    player_rank, player_best = best_hand_of_seven(player.hand + community_cards)
    opponent_ranks = []
    for opponent in opponents:
        opponent_rank, opponent_best = best_hand_of_seven(opponent.hand + community_cards)
        opponent_ranks.append(opponent_rank)
        opponent.best_hand = opponent_best

    print('\nYour best hand:')
    print(f'{HAND_NAMES[player_rank[0]]}: {format_hand(player_best)}')
    for opponent, rank in zip(opponents, opponent_ranks):
        print(f'\n{opponent.name} best hand:')
        print(f'{HAND_NAMES[rank[0]]}: {format_hand(opponent.best_hand)}')

    round_players = 1 + len(opponents)
    pot = MIN_ANTE * round_players
    player.adjust_chips(-MIN_ANTE)
    for opponent in opponents:
        opponent.adjust_chips(-MIN_ANTE)

    settle_pot(player, opponents, player_rank, opponent_ranks, pot)


def enter_casino() -> Player:
    print('Welcome to the Casino!')
    print(f'You receive {CASINO_START_CHIPS} chips to play with.')
    return Player('You', CASINO_START_CHIPS)


def choose_opponents() -> int:
    print('\nChoose how many opponents you want at the table:')
    return prompt_integer(f'Enter a number between 1 and {MAX_OPPONENTS}:', 1, MAX_OPPONENTS)


def main() -> None:
    player = enter_casino()

    while player.chips >= MIN_ANTE:
        print(f'\nCurrent chips: {player.chips}')
        choice = prompt_choice('\nChoose a game mode:', {
            '1': 'Five-Card Draw',
            '2': 'Texas Hold\'em',
            '3': 'Quit',
        })
        if choice == '3':
            break

        opponents = [Player(f'Opponent {i + 1}') for i in range(choose_opponents())]

        if player.chips < MIN_ANTE:
            print('Not enough chips to continue.')
            break

        if choice == '1':
            play_five_card_draw(player, opponents)
        else:
            play_texas_holdem(player, opponents)

        if player.chips < MIN_ANTE:
            print('\nYou are out of chips. Casino tables are closed for you.')
            break

    print('\nThanks for playing!')


if __name__ == '__main__':
    main()
