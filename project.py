# ============================================
# CASINO TEXAS HOLD'EM
# RESPONSIVE GUI VERSION
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox
import random
import itertools
import math

# ============================================
# CONFIG
# ============================================

RANKS = [
    '2', '3', '4', '5', '6', '7',
    '8', '9', '10', 'J', 'Q', 'K', 'A'
]

SUITS = ['♠', '♥', '♦', '♣']

RANK_VALUES = {
    r: i for i, r in enumerate(RANKS, start=2)
}

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
    'Royal Flush'
]

TABLE_COLOR = "#0b5d1e"

STARTING_CHIPS = 2000

# ============================================
# PROFILE EMOJIS
# ============================================

PROFILE_EMOJIS = [
    '🎰', '🃏', '💎', '👑', '🏆',
    '⭐', '🤠', '🚀', '🔥', '💪'
]

OPPONENT_NAMES = [
    'The Ace', 'Shadow', 'Diamond',
    'Bluff Master', 'The Gambler',
    'Lucky Luke', 'Thunder',
    'Phantom', 'The Wolf', 'Maverick'
]

# ============================================
# CARD
# ============================================

class Card:

    def __init__(self, rank, suit):

        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __repr__(self):

        return f"{self.rank}{self.suit}"

# ============================================
# DECK
# ============================================

class Deck:

    def __init__(self):

        self.cards = [
            Card(rank, suit)
            for suit in SUITS
            for rank in RANKS
        ]

        random.shuffle(self.cards)

    def deal(self, amount=1):

        return [
            self.cards.pop()
            for _ in range(amount)
        ]

# ============================================
# PLAYER
# ============================================

class Player:

    def __init__(self, name, chips, human=False):

        self.name = name
        self.chips = chips
        self.human = human

        self.emoji = random.choice(PROFILE_EMOJIS)

        self.hand = []

        self.folded = False
        self.all_in = False

        self.current_bet = 0
        self.total_bet = 0

        self.best_hand = None
        self.hand_rank = None

    def reset_for_hand(self):

        self.hand = []

        self.folded = False
        self.all_in = False

        self.current_bet = 0
        self.total_bet = 0

        self.best_hand = None
        self.hand_rank = None

# ============================================
# HAND EVALUATION
# ============================================

def straight_high(ranks):

    unique = sorted(set(ranks), reverse=True)

    if len(unique) != 5:
        return None

    if unique == [14, 5, 4, 3, 2]:
        return 5

    if unique[0] - unique[-1] == 4:
        return unique[0]

    return None

def evaluate_five(cards):

    ranks = sorted(
        [c.value for c in cards],
        reverse=True
    )

    suits = [c.suit for c in cards]

    flush = len(set(suits)) == 1

    straight = straight_high(ranks)

    counts = {}

    for r in ranks:
        counts[r] = counts.get(r, 0) + 1

    ordered = sorted(
        counts.items(),
        key=lambda x: (-x[1], -x[0])
    )

    ordered_ranks = []

    for r, c in ordered:
        ordered_ranks.extend([r] * c)

    vals = sorted(counts.values(), reverse=True)

    if flush and straight:

        if straight == 14:
            return (9, [14])

        return (8, [straight])

    if vals == [4, 1]:
        return (7, ordered_ranks)

    if vals == [3, 2]:
        return (6, ordered_ranks)

    if flush:
        return (5, ranks)

    if straight:
        return (4, [straight])

    if vals == [3, 1, 1]:
        return (3, ordered_ranks)

    if vals == [2, 2, 1]:
        return (2, ordered_ranks)

    if vals == [2, 1, 1, 1]:
        return (1, ordered_ranks)

    return (0, ranks)

def best_hand(cards):

    best = None
    best_combo = None

    for combo in itertools.combinations(cards, 5):

        rank = evaluate_five(list(combo))

        if best is None or rank > best:
            best = rank
            best_combo = combo

    return best, best_combo

# ============================================
# AI
# ============================================

def ai_action(player, to_call, community):
    # estimate hand strength (0-9) from evaluated best hand
    if community:
        strength = best_hand(
            player.hand + community
        )[0][0]
    else:
        # simple preflop heuristic: paired or high cards count as somewhat strong
        vals = sorted([c.value for c in player.hand], reverse=True)
        if vals[0] == vals[1]:
            strength = 5
        elif vals[0] >= 11 and vals[1] >= 10:
            strength = 5
        else:
            strength = 2

    # no bet to call: sometimes bluff by raising
    if to_call == 0:
        if random.random() < 0.18 and player.chips > 0:
            raise_amount = min(player.chips, random.randint(20, 100))
            return ("raise", raise_amount)
        return ("check", 0)

    # strong hands -> prefer raising
    if strength >= 6:
        if random.random() < 0.75 and player.chips > 0:
            raise_amount = min(player.chips, max(to_call, int(player.chips * 0.2)))
            return ("raise", raise_amount)
        return ("call", 0)

    # decent hands -> call or small raise
    if strength >= 4:
        if random.random() < 0.4 and player.chips > 0:
            raise_amount = min(player.chips, int(player.chips * 0.1) + to_call)
            return ("raise", raise_amount)
        return ("call", 0)

    # weak hands: sometimes bluff/call
    if random.random() < 0.25:
        if random.random() < 0.3 and player.chips > 0:
            raise_amount = min(player.chips, random.randint(10, 80))
            return ("raise", raise_amount)
        return ("call", 0)

    return ("fold", 0)

# ============================================
# GUI
# ============================================

class CasinoGUI:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("Casino Texas Hold'em")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)

        self.root.geometry(
            f"{window_width}x{window_height}"
        )

        self.root.minsize(1000, 700)

        self.root.configure(bg=TABLE_COLOR)

        self.zoom_level = 1.0

        # =====================================
        # CANVAS
        # =====================================

        self.table_canvas = tk.Canvas(
            self.root,
            bg=TABLE_COLOR,
            highlightthickness=0
        )

        self.table_canvas.pack(
            fill="both",
            expand=True
        )

        # redraw on resize
        self.table_canvas.bind(
            "<Configure>",
            self.on_resize
        )

        # =====================================
        # CONTROLS
        # =====================================

        self.controls = tk.Frame(
            self.root,
            bg="#222",
            height=120
        )

        self.controls.pack(fill="x")

        self.info_label = tk.Label(
            self.controls,
            text="",
            fg="white",
            bg="#222",
            font=("Arial", 14)
        )

        self.info_label.pack(pady=5)

        self.raise_scale = tk.Scale(
            self.controls,
            from_=20,
            to=500,
            orient="horizontal",
            length=300,
            label="Raise Amount"
        )

        self.raise_scale.pack()

        self.button_frame = tk.Frame(
            self.controls,
            bg="#222"
        )

        self.button_frame.pack(pady=5)

        self.action = None

    # =====================================
    # RESIZE
    # =====================================

    def on_resize(self, event):

        if hasattr(self, '_last_draw_data'):

            players, community, pot, current_player, reveal_all = self._last_draw_data

            self.draw_table(
                players,
                community,
                pot,
                current_player,
                reveal_all
            )

    # =====================================
    # CLAMP
    # =====================================

    def clamp(self, value, minimum, maximum):

        return max(minimum, min(value, maximum))

    # =====================================
    # SEAT POSITIONS
    # =====================================

    def get_seat_positions(
        self,
        width,
        height,
        player_count
    ):

        cx = width / 2
        cy = height / 2 + 30

        rx = width * 0.38
        ry = height * 0.34

        positions = []

        for i in range(player_count):

            angle = (
                (2 * math.pi * i / player_count)
                - (math.pi / 2)
            )

            x = cx + math.cos(angle) * rx
            y = cy + math.sin(angle) * ry

            x = self.clamp(x, 150, width - 150)
            y = self.clamp(y, 120, height - 150)

            positions.append((x, y))

        return positions

    # =====================================
    # BUTTONS
    # =====================================

    def clear_buttons(self):

        for w in self.button_frame.winfo_children():
            w.destroy()

    def wait_for_action(self, options):

        self.action = None

        self.clear_buttons()

        def set_action(a):
            self.action = a

        for op in options:

            btn = ttk.Button(
                self.button_frame,
                text=op.upper(),
                command=lambda x=op: set_action(x)
            )

            btn.pack(side="left", padx=10)

        while self.action is None:
            self.root.update()

        return self.action

    # =====================================
    # DRAW TABLE
    # =====================================

    def draw_table(
        self,
        players,
        community,
        pot,
        current_player=None,
        reveal_all=False
    ):

        self._last_draw_data = (
            players,
            community,
            pot,
            current_player,
            reveal_all
        )

        self.table_canvas.delete("all")

        width = self.table_canvas.winfo_width()
        height = self.table_canvas.winfo_height()

        self.scale = min(
            width / 1400,
            height / 900
        )

        s = lambda v: int(v * self.scale)

        # =====================================
        # TABLE
        # =====================================

        margin_x = width * 0.12
        margin_y = height * 0.12

        self.table_canvas.create_oval(
            margin_x,
            margin_y,
            width - margin_x,
            height - margin_y,
            fill="#0d7a28",
            outline="#083f15",
            width=max(2, s(8))
        )

        # =====================================
        # POT
        # =====================================

        self.table_canvas.create_text(
            width / 2,
            height * 0.63,
            text=f"POT: {pot}",
            fill="white",
            font=(
                "Arial",
                max(12, s(22)),
                "bold"
            )
        )

        # =====================================
        # COMMUNITY CARDS
        # =====================================

        card_w = s(70)
        spacing = s(20)

        total_width = (
            len(community) * card_w
            + max(0, len(community)-1) * spacing
        )

        start_x = (width - total_width) / 2

        y = height * 0.42

        for i, card in enumerate(community):

            self.draw_card(
                start_x + i * (card_w + spacing),
                y,
                card
            )

        # =====================================
        # PLAYERS
        # =====================================

        positions = self.get_seat_positions(
            width,
            height,
            len(players)
        )

        for player, (x, y) in zip(players, positions):

            self.draw_player(
                player,
                x,
                y,
                current_player,
                reveal_all
            )

    # =====================================
    # DRAW CARD
    # =====================================

    def draw_card(
        self,
        x,
        y,
        card,
        hidden=False
    ):

        s = self.scale

        w = max(40, int(70 * s))
        h = max(60, int(100 * s))

        color = (
            "red"
            if card.suit in ['♥', '♦']
            else "black"
        )

        self.table_canvas.create_rectangle(
            x,
            y,
            x + w,
            y + h,
            fill="white",
            outline="black",
            width=max(1, int(2 * s))
        )

        if hidden:

            text = "🂠"

        else:

            text = f"{card.rank}{card.suit}"

        self.table_canvas.create_text(
            x + w / 2,
            y + h / 2,
            text=text,
            fill=color,
            font=(
                "Arial",
                max(10, int(14 * s)),
                "bold"
            )
        )

    # =====================================
    # DRAW PLAYER
    # =====================================

    def draw_player(
        self,
        player,
        x,
        y,
        current_player,
        reveal_all
    ):

        s = self.scale

        color = (
            "yellow"
            if player == current_player
            else "white"
        )

        status = ""

        if player.folded:
            status = "FOLDED"

        elif player.all_in:
            status = "ALL-IN"

        # emoji
        self.table_canvas.create_text(
            x,
            y - 70 * s,
            text=player.emoji,
            font=(
                "Arial",
                max(14, int(26 * s))
            )
        )

        # info
        self.table_canvas.create_text(
            x,
            y,
            text=(
                f"{player.name}\n"
                f"Chips: {player.chips}\n"
                f"Bet: {player.current_bet}\n"
                f"{status}"
            ),
            fill=color,
            font=(
                "Arial",
                max(10, int(13 * s)),
                "bold"
            )
        )

        # cards
        card_w = int(70 * s)

        spacing = int(card_w * 0.75)

        start_x = x - spacing / 2

        card_y = y + 50 * s

        for i, card in enumerate(player.hand):

            hidden = (
                (not player.human)
                and
                (not reveal_all)
            )

            self.draw_card(
                start_x + i * spacing,
                card_y,
                card,
                hidden
            )

# ============================================
# GAME ENGINE
# ============================================

class PokerGame:

    def __init__(
        self,
        gui,
        opponents,
        small_blind,
        big_blind
    ):

        self.gui = gui

        self.small_blind = small_blind
        self.big_blind = big_blind

        self.players = [
            Player(
                "YOU",
                STARTING_CHIPS,
                human=True
            )
        ]

        used_names = set()

        for _ in range(opponents):

            name = random.choice(OPPONENT_NAMES)

            while name in used_names:
                name = random.choice(OPPONENT_NAMES)

            used_names.add(name)

            self.players.append(
                Player(name, STARTING_CHIPS)
            )

        self.dealer = 0

        self.community = []

        self.pot = 0

    def active_players(self):

        return [
            p for p in self.players
            if not p.folded
        ]

    def reset_bets(self):

        for p in self.players:
            p.current_bet = 0

    def post_blinds(self):

        sb_index = (
            self.dealer + 1
        ) % len(self.players)

        bb_index = (
            self.dealer + 2
        ) % len(self.players)

        sb = self.players[sb_index]
        bb = self.players[bb_index]

        sb_amount = min(
            sb.chips,
            self.small_blind
        )

        bb_amount = min(
            bb.chips,
            self.big_blind
        )

        sb.chips -= sb_amount
        bb.chips -= bb_amount

        sb.current_bet = sb_amount
        bb.current_bet = bb_amount

        self.pot += sb_amount + bb_amount

    def betting_round(self, start_index):

        acted = set()

        while True:

            highest = max(
                p.current_bet
                for p in self.players
            )

            everyone_done = True

            for i in range(len(self.players)):

                idx = (
                    start_index + i
                ) % len(self.players)

                p = self.players[idx]

                if p.folded or p.all_in:
                    continue

                to_call = (
                    highest - p.current_bet
                )

                if p in acted and to_call == 0:
                    continue

                everyone_done = False

                self.gui.draw_table(
                    self.players,
                    self.community,
                    self.pot,
                    current_player=p
                )

                if p.human:

                    if to_call == 0:

                        options = [
                            "check",
                            "raise",
                            "fold"
                        ]

                    else:

                        options = [
                            "call",
                            "raise",
                            "fold"
                        ]

                    self.gui.info_label.config(
                        text=f"To Call: {to_call}"
                    )

                    action = self.gui.wait_for_action(
                        options
                    )

                    raise_amount = (
                        self.gui.raise_scale.get()
                    )

                else:

                    action, raise_amount = ai_action(
                        p,
                        to_call,
                        self.community
                    )

                if action == "fold":

                    p.folded = True

                    acted.add(p)

                elif action == "check":

                    acted.add(p)

                elif action == "call":

                    amount = min(
                        to_call,
                        p.chips
                    )

                    p.chips -= amount

                    p.current_bet += amount

                    self.pot += amount

                    acted.add(p)

                elif action == "raise":

                    total = (
                        to_call + raise_amount
                    )

                    total = min(total, p.chips)

                    p.chips -= total

                    p.current_bet += total

                    self.pot += total

                    acted = {p}

            if everyone_done:
                break

    def showdown(self):

        remaining = [
            p for p in self.players
            if not p.folded
        ]

        for p in remaining:

            p.hand_rank, p.best_hand = best_hand(
                p.hand + self.community
            )

        best_rank = max(
            p.hand_rank
            for p in remaining
        )

        winners = [
            p for p in remaining
            if p.hand_rank == best_rank
        ]

        share = self.pot // len(winners)

        for w in winners:
            w.chips += share

        self.gui.draw_table(
            self.players,
            self.community,
            self.pot,
            reveal_all=True
        )

        names = ", ".join(
            p.name for p in winners
        )

        hand_name = HAND_NAMES[
            winners[0].hand_rank[0]
        ]

        messagebox.showinfo(
            "Showdown",
            f"{names} win(s)\n\n"
            f"Hand: {hand_name}"
        )

    def play_hand(self):

        self.community = []

        self.pot = 0

        for p in self.players:
            p.reset_for_hand()

        deck = Deck()

        for _ in range(2):

            for p in self.players:

                p.hand.extend(
                    deck.deal(1)
                )

        self.post_blinds()

        preflop_start = (
            self.dealer + 3
        ) % len(self.players)

        self.betting_round(preflop_start)

        # flop
        self.reset_bets()

        self.community.extend(
            deck.deal(3)
        )

        self.betting_round(
            (self.dealer + 1)
            % len(self.players)
        )

        # turn
        self.reset_bets()

        self.community.extend(
            deck.deal(1)
        )

        self.betting_round(
            (self.dealer + 1)
            % len(self.players)
        )

        # river
        self.reset_bets()

        self.community.extend(
            deck.deal(1)
        )

        self.betting_round(
            (self.dealer + 1)
            % len(self.players)
        )

        self.showdown()

        self.dealer = (
            self.dealer + 1
        ) % len(self.players)

        return True

# ============================================
# LOBBY
# ============================================

class CasinoLobby:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("Casino Lobby")

        self.root.geometry("600x500")

        self.root.configure(bg="#111")

        self.selection = None

        tk.Label(
            self.root,
            text="CASINO LOBBY",
            fg="gold",
            bg="#111",
            font=("Arial", 28, "bold")
        ).pack(pady=40)

        tables = [
            ("Heads-Up", 1, 10, 20),
            ("3 Players", 2, 25, 50),
            ("6-Max", 5, 50, 100),
        ]

        for name, opps, sb, bb in tables:

            btn = tk.Button(
                self.root,
                text=f"{name}\nBlinds {sb}/{bb}",
                width=30,
                height=3,
                font=("Arial", 14),
                command=lambda o=opps,
                s=sb,
                b=bb:
                self.choose(o, s, b)
            )

            btn.pack(pady=10)

        self.root.mainloop()

    def choose(self, opponents, sb, bb):

        self.selection = (
            opponents,
            sb,
            bb
        )

        self.root.destroy()

# ============================================
# MAIN
# ============================================

def main():

    lobby = CasinoLobby()

    if not lobby.selection:
        return

    opponents, sb, bb = lobby.selection

    gui = CasinoGUI()

    game = PokerGame(
        gui,
        opponents,
        sb,
        bb
    )

    while True:

        cont = game.play_hand()

        if not cont:
            break

if __name__ == "__main__":
    main()

