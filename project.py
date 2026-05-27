# ============================================
# CASINO TEXAS HOLD'EM
# Full GUI Poker Table Version
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox
import random
import itertools

# ============================================
# CONFIG
# ============================================

RANKS = ['2', '3', '4', '5', '6', '7', '8',
         '9', '10', 'J', 'Q', 'K', 'A']

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
    'Royal Flush'
]

TABLE_COLOR = "#0b5d1e"

STARTING_CHIPS = 2000

# ============================================
# PROFILE EMOJIS
# ============================================

PROFILE_EMOJIS = [
    '🎰', '🃏', '💎', '👑', '🏆', '⭐', '🤠', '🚀', '🔥', '💪',
    '🎭', '🤡', '👹', '🤬', '🎮', '🎲', '🤔', '🏅', '💰', '🤑',
    '😎', '🤐', '🧠', '💯', '❤️‍🔥', '👻', '🔮', '🎁', '🎉', '🌟',
    '✨', '🫠', '🐦‍🔥', '⚡', '🔔', '😜', '🤓', '😈', '🧐', '🥱',
    '🦁', '🐯', '🦅', '💩', '🤖', '👾', '🎰', '💸', '☠️', '💳'
]

OPPONENT_NAMES = [
    'The Ace', 'Shadow', 'Diamond', 'Bluff Master', 'The Gambler',
    'Lucky Luke', 'Thunder', 'Phantom', 'The Wolf', 'Maverick',
    'Iron Fist', 'Silent Storm', 'Cash King', 'The Tiger', 'Poker Face',
    'High Roller', 'The Shark', 'Fortune Seeker', 'The Legend', 'Royal Flush',
    'Quick Draw', 'The Sphinx', 'Chip Leader', 'The Dealer', 'Midnight Rider'
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
        return [self.cards.pop() for _ in range(amount)]

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

    ranks = sorted([c.value for c in cards], reverse=True)

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

def evaluate_preflop(hand):

    vals = sorted([c.value for c in hand], reverse=True)

    pair = vals[0] == vals[1]

    suited = hand[0].suit == hand[1].suit

    connected = abs(vals[0] - vals[1]) == 1

    if pair:
        if vals[0] >= 11:
            return 9
        return 7

    if vals[0] >= 14 and vals[1] >= 11:
        return 8

    if suited and connected:
        return 6

    if suited:
        return 5

    if vals[0] >= 12:
        return 4

    return 2

def ai_action(player, to_call, community):

    if community:
        strength = best_hand(
            player.hand + community
        )[0][0]
    else:
        strength = evaluate_preflop(player.hand)

    # Don't fold easily on all-ins if we have reasonable chips
    if to_call == player.chips and player.chips > 0:
        # Has decent hand - call the all-in
        if strength >= 3:
            return ("call", 0)
        # Bluff/gamble occasionally even with weak hands
        if random.random() < 0.4:
            return ("call", 0)
        return ("fold", 0)

    # Strong hand - aggressive play
    if strength >= 8:
        if random.random() < 0.4 and player.chips > to_call + 100:
            return ("raise", random.randint(75, 150))
        return ("call", 0)

    if strength >= 6:
        if random.random() < 0.3 and player.chips > to_call + 50:
            return ("raise", 50)
        return ("call", 0)

    if strength >= 4:
        if to_call <= 50:
            return ("call", 0)
        # Bluff occasionally with mid-strength hands
        if random.random() < 0.25:
            return ("raise", min(50, player.chips))
        if random.random() < 0.35:
            return ("call", 0)
        return ("fold", 0)

    if strength == 3:
        # Bluff on low-strength hands sometimes
        if to_call == 0:
            if random.random() < 0.2:
                return ("raise", random.randint(20, 50))
            return ("check", 0)
        if random.random() < 0.2:
            return ("call", 0)
        return ("fold", 0)

    if to_call == 0:
        # Free check with weak hand
        if random.random() < 0.1:
            return ("raise", random.randint(20, 40))
        return ("check", 0)

    if random.random() < 0.15:
        return ("call", 0)

    return ("fold", 0)

# ============================================
# GUI
# ============================================

class CasinoGUI:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("Casino Texas Hold'em")

        self.root.geometry("1400x900")

        self.root.configure(bg=TABLE_COLOR)

        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0

        self.table_canvas = tk.Canvas(
            self.root,
            bg=TABLE_COLOR,
            highlightthickness=0
        )

        self.table_canvas.pack(fill="both", expand=True)

        # Bind zoom events
        self.table_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.table_canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.table_canvas.bind("<Button-5>", self.on_mouse_wheel)
        self.root.bind("<plus>", self.zoom_in)
        self.root.bind("<equal>", self.zoom_in)
        self.root.bind("<minus>", self.zoom_out)
        self.root.bind("<Control-plus>", self.zoom_in)
        self.root.bind("<Control-equal>", self.zoom_in)
        self.root.bind("<Control-minus>", self.zoom_out)

        # action controls

        self.controls = tk.Frame(
            self.root,
            bg="#222"
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

        self.zoom_label = tk.Label(
            self.controls,
            text=f"Zoom: {int(self.zoom_level * 100)}%",
            fg="lightblue",
            bg="#222",
            font=("Arial", 10)
        )

        self.zoom_label.pack()

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

        self.button_frame.pack(pady=10)

        self.action = None

        self.seat_positions = []

    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom events."""
        if event.num == 5 or event.delta < 0:
            self.zoom_out()
        elif event.num == 4 or event.delta > 0:
            self.zoom_in()

    def zoom_in(self, event=None):
        """Increase zoom level."""
        self.zoom_level = min(self.zoom_level + 0.1, self.max_zoom)
        self.zoom_label.config(text=f"Zoom: {int(self.zoom_level * 100)}%")
        # Redraw if we're currently showing a table
        if hasattr(self, '_last_draw_data'):
            players, community, pot, current_player, reveal_all = self._last_draw_data
            self.draw_table(players, community, pot, current_player, reveal_all)

    def zoom_out(self, event=None):
        """Decrease zoom level."""
        self.zoom_level = max(self.zoom_level - 0.1, self.min_zoom)
        self.zoom_label.config(text=f"Zoom: {int(self.zoom_level * 100)}%")
        # Redraw if we're currently showing a table
        if hasattr(self, '_last_draw_data'):
            players, community, pot, current_player, reveal_all = self._last_draw_data
            self.draw_table(players, community, pot, current_player, reveal_all)

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

    def draw_table(
        self,
        players,
        community,
        pot,
        current_player=None,
        reveal_all=False
    ):

        # Store draw data for redrawing on zoom
        self._last_draw_data = (players, community, pot, current_player, reveal_all)

        self.table_canvas.delete("all")

        # Use actual canvas size for responsive layout; ensure sensible defaults
        width = max(1400, self.table_canvas.winfo_width())
        height = max(850, self.table_canvas.winfo_height())

        # Apply zoom level to scaling
        self.scale_x = float(width) / 1400.0 * self.zoom_level
        self.scale_y = float(height) / 850.0 * self.zoom_level

        sx = lambda v: int(v * self.scale_x)
        sy = lambda v: int(v * self.scale_y)

        self.reveal_all = reveal_all

        # table (scaled)
        self.table_canvas.create_oval(
            sx(150),
            sy(100),
            sx(1250),
            sy(700),
            fill="#0d7a28",
            outline="#083f15",
            width=max(1, int(10 * self.scale_x))
        )

        # pot label (scaled)
        self.table_canvas.create_text(
            sx(700),
            sy(260),
            text=f"POT: {pot}",
            fill="white",
            font=("Arial", max(10, int(24 * self.scale_y)), "bold")
        )

        # community cards (scaled positions)
        x = sx(520)

        for card in community:
            self.draw_card(x, sy(320), card)
            x += int(90 * self.scale_x)

        # draw pot chips just below the river/community cards (raised slightly)
        # moved up a bit to avoid overlapping with player cards
        self.draw_chips(sx(700), sy(450), pot)

        # shift player anchor positions slightly upward to avoid overlap
        positions = [
            (700, 610),
            (250, 460),
            (1150, 460),
            (350, 140),
            (1050, 140),
            (700, 40)
        ]

        for i, player in enumerate(players):
            px, py = positions[i]
            self.draw_player(player, sx(px), sy(py), current_player)

    def draw_card(self, x, y, card, hidden=False):
        # scale card size with canvas
        sx = getattr(self, 'scale_x', 1)
        sy = getattr(self, 'scale_y', 1)

        w = max(20, int(70 * sx))
        h = max(30, int(100 * sy))

        color = "red" if card.suit in ['♥', '♦'] else "black"

        self.table_canvas.create_rectangle(
            x,
            y,
            x + w,
            y + h,
            fill="white",
            outline="black",
            width=max(1, int(3 * sx))
        )

        if hidden:
            self.table_canvas.create_text(
                x + w // 2,
                y + h // 2,
                text="🂠",
                font=("Arial", max(8, int(24 * sy)))
            )
        else:
            self.table_canvas.create_text(
                x + w // 2,
                y + h // 2,
                text=f"{card.rank}{card.suit}",
                fill=color,
                font=("Arial", max(8, int(12 * sy)), "bold")
            )

    def draw_chips(self, x, y, amount, max_stack=5):
        """Draw a small stack of chips and an amount label."""
        # Determine number of visible chips (1..max_stack)
        if amount <= 0:
            return
        # Responsive sizes
        sx = getattr(self, 'scale_x', 1)
        sy = getattr(self, 'scale_y', 1)

        chip_radius = max(6, int(10 * ((sx + sy) / 2)))
        spacing = max(3, int(6 * sy))

        # Determine total visual chips (max 3 stacks * max_stack)
        max_total = max_stack * 3
        ratio = min(10.0, amount / max(1, STARTING_CHIPS))
        total_visual = min(max_total, max(1, int(ratio * max_total)))

        # distribute across up to 3 stacks
        stacks = 3
        base = total_visual // stacks
        rem = total_visual % stacks
        counts = [base + (1 if i < rem else 0) for i in range(stacks)]

        # draw stacks side by side
        stack_spacing = chip_radius * 3
        start_x = x - int(stack_spacing)
        for s_idx, cnt in enumerate(counts):
            cx = start_x + s_idx * stack_spacing
            for i in range(cnt):
                cy = y - (i * spacing)
                self.table_canvas.create_oval(
                    cx - chip_radius,
                    cy - chip_radius,
                    cx + chip_radius,
                    cy + chip_radius,
                    fill="#e63946",
                    outline="#2b2b2b",
                    width=1
                )

        # amount label to the right
        label_x = x + chip_radius + int(28 * sx)
        label_y = y - ((max(counts) - 1) * spacing) / 2
        self.table_canvas.create_text(
            label_x,
            label_y,
            text=f"{amount}",
            fill="white",
            font=("Arial", max(8, int(12 * sy)), "bold")
        )

    def draw_player(self, player, x, y, current_player):

        color = "yellow" if player == current_player else "white"

        status = ""

        if player.folded:
            status = "FOLDED"

        elif player.all_in:
            status = "ALL-IN"

        # scaled emoji above name
        sx = getattr(self, 'scale_x', 1)
        sy = getattr(self, 'scale_y', 1)

        self.table_canvas.create_text(
            x,
            y - int(65 * sy),
            text=player.emoji,
            font=("Arial", max(10, int(28 * sy)))
        )

        self.table_canvas.create_text(
            x,
            y,
            text=f"{player.name}\nChips: {player.chips}\nBet: {player.current_bet}\n{status}",
            fill=color,
            font=("Arial", max(8, int(14 * sy)), "bold")
        )

        # draw player's chip stack to the right of the player info
        self.draw_chips(x + int(120 * sx), y, player.chips)

        start_x = x - int(50 * sx)

        for i, card in enumerate(player.hand):

            # Hide AI cards during play unless reveal_all is set
            hidden = (not player.human) and (not getattr(self, 'reveal_all', False))

            self.draw_card(
                start_x + i * int(65 * sx),
                y + int(60 * sy),
                card,
                hidden=hidden
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
            Player("YOU", STARTING_CHIPS, human=True)
        ]

        # Use random opponent names
        used_names = set()
        for i in range(opponents):
            name = random.choice(OPPONENT_NAMES)
            while name in used_names:
                name = random.choice(OPPONENT_NAMES)
            used_names.add(name)
            self.players.append(
                Player(
                    name,
                    STARTING_CHIPS
                )
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

        sb_index = (self.dealer + 1) % len(self.players)
        bb_index = (self.dealer + 2) % len(self.players)

        sb = self.players[sb_index]
        bb = self.players[bb_index]

        sb_amount = min(sb.chips, self.small_blind)
        bb_amount = min(bb.chips, self.big_blind)

        sb.chips -= sb_amount
        bb.chips -= bb_amount

        sb.current_bet = sb_amount
        bb.current_bet = bb_amount

        sb.total_bet = sb_amount
        bb.total_bet = bb_amount

        self.pot += sb_amount + bb_amount

    def betting_round(self, start_index):

        acted = set()

        while True:

            highest = max(p.current_bet for p in self.players)

            everyone_done = True

            for i in range(len(self.players)):

                idx = (start_index + i) % len(self.players)

                p = self.players[idx]

                if p.folded or p.all_in:
                    continue

                to_call = highest - p.current_bet

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
                            "allin",
                            "fold"
                        ]
                    else:
                        options = [
                            "call",
                            "raise",
                            "allin",
                            "fold"
                        ]

                    self.gui.info_label.config(
                        text=f"Your turn — To Call: {to_call}"
                    )

                    action = self.gui.wait_for_action(options)

                    raise_amount = self.gui.raise_scale.get()

                else:

                    action, raise_amount = ai_action(
                        p,
                        to_call,
                        self.community
                    )

                if action == "fold":

                    p.folded = True

                    acted.add(p)

                    continue

                elif action == "check":

                    acted.add(p)

                elif action == "call":

                    amount = min(to_call, p.chips)

                    p.chips -= amount

                    p.current_bet += amount
                    p.total_bet += amount

                    self.pot += amount

                    if p.chips == 0:
                        p.all_in = True

                    acted.add(p)

                elif action == "raise":

                    total = to_call + raise_amount

                    total = min(total, p.chips)

                    p.chips -= total

                    p.current_bet += total
                    p.total_bet += total

                    self.pot += total

                    if p.chips == 0:
                        p.all_in = True

                    acted = {p}

                elif action == "allin":

                    amount = p.chips

                    p.chips = 0

                    p.current_bet += amount
                    p.total_bet += amount

                    self.pot += amount

                    p.all_in = True

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

        remainder = self.pot % len(winners)

        for i, w in enumerate(winners):

            payout = share

            if i < remainder:
                payout += 1

            w.chips += payout

        names = ", ".join(
            p.name for p in winners
        )

        hand_name = HAND_NAMES[
            winners[0].hand_rank[0]
        ]

        # Draw final table with all cards revealed (responsive)
        self.gui.draw_table(
            self.players,
            self.community,
            self.pot,
            reveal_all=True
        )

        messagebox.showinfo(
            "Showdown",
            f"{names} win(s)\n\n"
            f"Hand: {hand_name}\n"
            f"Pot: {self.pot}"
        )

    def remove_broke_players(self):

        self.players = [
            p for p in self.players
            if p.chips > 0
        ]

    def play_hand(self):

        if len(self.players) <= 1:

            messagebox.showinfo(
                "Game Over",
                "You won the table!"
            )

            return False

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
            (self.dealer + 3)
            % len(self.players)
        )

        self.betting_round(preflop_start)

        if len(self.active_players()) == 1:

            winner = self.active_players()[0]

            winner.chips += self.pot

            messagebox.showinfo(
                "Hand Over",
                f"{winner.name} wins uncontested!"
            )

            self.dealer = (
                self.dealer + 1
            ) % len(self.players)

            return True

        # FLOP

        self.reset_bets()

        self.community.extend(
            deck.deal(3)
        )

        self.betting_round(
            (self.dealer + 1)
            % len(self.players)
        )

        # TURN

        self.reset_bets()

        self.community.extend(
            deck.deal(1)
        )

        self.betting_round(
            (self.dealer + 1)
            % len(self.players)
        )

        # RIVER

        self.reset_bets()

        self.community.extend(
            deck.deal(1)
        )

        self.betting_round(
            (self.dealer + 1)
            % len(self.players)
        )

        self.showdown()

        self.remove_broke_players()

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
            ("Heads-Up Table", 1, 10, 20),
            ("3 Player Table", 2, 25, 50),
            ("6-Max Table", 5, 50, 100),
            ("High Roller Table", 5, 100, 200),
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

        human = game.players[0]

        if human.chips < game.big_blind:

            messagebox.showinfo(
                "Busted",
                "You are out of chips!"
            )

            break

        cont = game.play_hand()

        if not cont:
            break

if __name__ == "__main__":
    main()