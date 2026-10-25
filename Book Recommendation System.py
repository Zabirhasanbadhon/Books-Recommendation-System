import tkinter as tk
from tkinter import ttk, messagebox
import re

# ============================================================
# BOOK RECOMMENDATION SYSTEM
# Built with Python + Tkinter (no third-party packages needed)
# ============================================================

BG = "#10172A"
CARD = "#19243B"
CARD_DARK = "#141E33"
TEXT = "#F3F6FC"
MUTED = "#AAB7D0"
ACCENT = "#35D0BA"
ACCENT_DARK = "#168F87"
PURPLE = "#8B7CFF"
ORANGE = "#FFB454"
RED = "#FF647C"
ENTRY_BG = "#F7F9FD"
ENTRY_FG = "#17233B"

# ============================================================
# LOAD BOOKS FROM YOUR CSV DATASET
# Change ONLY CSV_PATH to the location of your .csv file.
# ============================================================
import csv
from pathlib import Path

CSV_PATH = Path(r"")  # <-- CHANGE THIS PATH


def _clean_column_name(name):
    """Make CSV column names easier to match, e.g. average_rating -> average rating."""
    return re.sub(r"[^a-z0-9]+", " ", str(name or "").strip().lower()).strip()


def _get_csv_value(row, aliases, default=""):
    """Return the first non-empty value found under any supported column name."""
    normalized = {_clean_column_name(key): value for key, value in row.items() if key is not None}
    for alias in aliases:
        value = normalized.get(_clean_column_name(alias), "")
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _parse_number(value, default=0.0):
    try:
        cleaned = str(value).strip().replace(",", "")
        return float(cleaned) if cleaned else default
    except (TypeError, ValueError):
        return default


def _parse_year(value):
    match = re.search(r"(?:18|19|20|21)\d{2}", str(value or ""))
    return int(match.group()) if match else 0


def load_books(csv_path):
    """Load CSV rows into the field names used by the existing Tkinter app."""
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Could not find the books CSV file:\n{csv_path}\n\n"
            "Update CSV_PATH near the top of this file to your actual CSV location."
        )

    books = []
    seen_titles = set()  # The GUI uses book titles as row IDs, so titles must be unique.
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("The CSV file is empty or does not contain a header row.")

        for row in reader:
            title = _get_csv_value(row, ["title", "book title", "name"])
            if not title or title.casefold() in seen_titles:
                continue
            seen_titles.add(title.casefold())

            author = _get_csv_value(row, ["authors", "author", "book author"], "Unknown")
            genre = _get_csv_value(
                row, ["genre", "genres", "category", "categories", "subject", "subjects", "book genre"],
                "Other"
            )
            rating = _parse_number(
                _get_csv_value(row, ["average_rating", "average rating", "rating", "book rating", "score"]),
                0.0
            )
            # Most book datasets rate books from 0 to 5. Convert 0-10 ratings to 0-5.
            if rating > 5 and rating <= 10:
                rating = rating / 2
            rating = max(0.0, min(5.0, rating))

            year_text = _get_csv_value(
                row, ["year", "publication year", "original publication year", "published year", "publication_date", "published date"]
            )
            year = _parse_year(year_text)
            description = _get_csv_value(
                row, ["description", "book description", "summary", "synopsis", "overview", "about"]
            )
            keywords = _get_csv_value(
                row, ["keywords", "tags", "subjects", "categories", "genre", "genres"]
            )
            if not keywords:
                keywords = f"{title} {author} {genre}"

            books.append({
                "title": title,
                "author": author,
                "genre": genre,
                "rating": rating,
                "year": year,
                "description": description or "No description is available in this dataset.",
                "keywords": keywords,
            })

    if not books:
        raise ValueError(
            "No books were loaded. Check that your CSV has a title column "
            "(for example: title, book title, or name)."
        )

    return books


BOOKS = load_books(CSV_PATH)
GENRES = ["All Genres"] + sorted({book["genre"] for book in BOOKS if book["genre"]})


def tokenize(text):
    """Simple tokenization for content-based matching."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def book_text(book):
    return f'{book["title"]} {book["author"]} {book["genre"]} {book["description"]} {book["keywords"]}'


def similarity(book_a, book_b):
    """Jaccard similarity between book text features, plus genre weighting."""
    words_a = tokenize(book_text(book_a))
    words_b = tokenize(book_text(book_b))
    union = words_a | words_b
    score = len(words_a & words_b) / len(union) if union else 0.0
    if book_a["genre"] == book_b["genre"]:
        score += 0.25
    return score


class BookRecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZaBir HaSan | Book Recommendation System")
        self.root.geometry("1360x820")
        self.root.minsize(1050, 680)
        self.root.configure(bg=BG)

        self.search_var = tk.StringVar()
        self.genre_var = tk.StringVar(value="All Genres")
        self.sort_var = tk.StringVar(value="Recommended")
        self.status_var = tk.StringVar(value="Welcome! Select a book to explore recommendations.")
        self.selected_book = None
        self.reading_list = []

        self.configure_styles()
        self.build_ui()
        self.populate_books()
        self.update_clock()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", padding=7, fieldbackground=ENTRY_BG,
                        background=ENTRY_BG, foreground=ENTRY_FG,
                        arrowcolor=ACCENT_DARK)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)])
        style.configure("Treeview", background=CARD_DARK, foreground=TEXT,
                        fieldbackground=CARD_DARK, rowheight=29,
                        borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#263653", foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", ACCENT_DARK)],
                  foreground=[("selected", "white")])

    def make_card(self, parent, title, subtitle=None):
        card = tk.Frame(parent, bg=CARD, padx=14, pady=12,
                        highlightthickness=1, highlightbackground="#2A3855")
        tk.Label(card, text=title, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(card, text=subtitle, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 9), wraplength=500,
                     justify="left").pack(anchor="w", pady=(3, 9))
        return card

    def make_button(self, parent, text, command, color=ACCENT_DARK):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         activebackground=color, activeforeground="white",
                         font=("Segoe UI", 10, "bold"), bd=0, relief="flat",
                         padx=12, pady=9, cursor="hand2")

    def build_ui(self):
        header = tk.Frame(self.root, bg="#17233B", padx=22, pady=15)
        header.pack(fill="x", padx=16, pady=(16, 12))
        tk.Label(header, text="✦✦  ZaBir | ReadWise  ✦✦", bg="#17233B", fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(header, text="Book Recommendation System", bg="#17233B", fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Label(header, text="Discover your next favorite read • Search • Explore • Save",
                 bg="#17233B", fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

        toolbar = tk.Frame(self.root, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(toolbar, text="SEARCH", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        search_entry = tk.Entry(toolbar, textvariable=self.search_var, bg=ENTRY_BG,
                                fg=ENTRY_FG, insertbackground=ENTRY_FG, bd=0,
                                font=("Segoe UI", 11), width=28)
        search_entry.pack(side="left", ipady=8, padx=(0, 12))
        search_entry.bind("<KeyRelease>", lambda _event: self.populate_books())

        tk.Label(toolbar, text="GENRE", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        genre_box = ttk.Combobox(toolbar, textvariable=self.genre_var,
                                 values=GENRES, state="readonly", width=17)
        genre_box.pack(side="left", padx=(0, 12))
        genre_box.bind("<<ComboboxSelected>>", lambda _event: self.populate_books())

        tk.Label(toolbar, text="SORT", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        sort_box = ttk.Combobox(toolbar, textvariable=self.sort_var,
                                values=("Recommended", "Highest Rated", "Title A-Z", "Newest"),
                                state="readonly", width=15)
        sort_box.pack(side="left", padx=(0, 12))
        sort_box.bind("<<ComboboxSelected>>", lambda _event: self.populate_books())
        self.make_button(toolbar, "Reset Filters", self.reset_filters, "#5269C9").pack(side="left")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=3)
        body.grid_rowconfigure(0, weight=1)

        catalog_card = self.make_card(body, "Book Catalog", "Select any book to view its details.")
        catalog_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        catalog_card.grid_rowconfigure(1, weight=1)
        catalog_card.grid_columnconfigure(0, weight=1)

        # Use a dedicated content frame: make_card() packs its heading labels,
        # so the table must use grid() inside a different parent frame.
        catalog_content = tk.Frame(catalog_card, bg=CARD)
        catalog_content.pack(fill="both", expand=True, pady=(5, 0))
        catalog_content.grid_rowconfigure(0, weight=1)
        catalog_content.grid_columnconfigure(0, weight=1)

        columns = ("title", "author", "genre", "rating", "year")
        self.tree = ttk.Treeview(catalog_content, columns=columns, show="headings",
                                 selectmode="browse")
        for col, heading, width in [
            ("title", "BOOK TITLE", 245), ("author", "AUTHOR", 150),
            ("genre", "GENRE", 115), ("rating", "RATING", 70), ("year", "YEAR", 60)
        ]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=55,
                             anchor="w" if col in ("title", "author", "genre") else "center")
        scrollbar = ttk.Scrollbar(catalog_content, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_book_select)
        self.tree.bind("<Double-1>", lambda _event: self.recommend_selected())

        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        details = self.make_card(right, "Book Details", "Choose a book from the catalog.")
        details.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.detail_title = tk.Label(details, text="No book selected", bg=CARD, fg=ACCENT,
                                      font=("Segoe UI", 15, "bold"), wraplength=370,
                                      justify="left")
        self.detail_title.pack(anchor="w", pady=(8, 4))
        self.detail_author = tk.Label(details, text="Author: —", bg=CARD, fg=TEXT,
                                      font=("Segoe UI", 10))
        self.detail_author.pack(anchor="w", pady=2)
        self.detail_meta = tk.Label(details, text="Genre: —  |  Rating: —  |  Year: —",
                                    bg=CARD, fg=MUTED, font=("Segoe UI", 9))
        self.detail_meta.pack(anchor="w", pady=2)
        self.detail_description = tk.Label(details, text="Book description will appear here.",
                                           bg=CARD, fg=TEXT, font=("Segoe UI", 10),
                                           wraplength=370, justify="left", anchor="nw")
        self.detail_description.pack(fill="x", anchor="w", pady=(8, 10))
        action_row = tk.Frame(details, bg=CARD)
        action_row.pack(fill="x")
        self.make_button(action_row, "Recommend Similar", self.recommend_selected, PURPLE).pack(
            side="left", padx=(0, 7))
        self.make_button(action_row, "Add to Reading List", self.add_to_reading_list, ACCENT_DARK).pack(
            side="left")

        recommendations = self.make_card(right, "Recommended for You",
                                          "Recommendations are based on genre and matching keywords.")
        recommendations.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Keep grid-managed widgets inside a child frame because make_card()
        # uses pack() for its title and subtitle labels.
        recommendation_content = tk.Frame(recommendations, bg=CARD)
        recommendation_content.pack(fill="both", expand=True, pady=(5, 0))
        recommendation_content.grid_rowconfigure(0, weight=1)
        recommendation_content.grid_columnconfigure(0, weight=1)
        self.recommendation_list = tk.Listbox(
            recommendation_content, bg=CARD_DARK, fg=TEXT, selectbackground=ACCENT_DARK,
            selectforeground="white", font=("Segoe UI", 10), bd=0,
            highlightthickness=0, activestyle="none"
        )
        self.recommendation_list.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.recommendation_list.bind("<Double-1>", self.open_recommendation)
        self.make_button(recommendation_content, "Show Top Rated Books", self.show_top_rated,
                         "#5269C9").grid(row=1, column=0, sticky="ew")

        bottom = tk.Frame(self.root, bg="#17233B", padx=16, pady=9)
        bottom.pack(fill="x", padx=16, pady=(0, 14))
        tk.Label(bottom, textvariable=self.status_var, bg="#17233B", fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        self.clock_label = tk.Label(bottom, text="", bg="#17233B", fg=ACCENT,
                                    font=("Segoe UI", 9, "bold"))
        self.clock_label.pack(side="right")
        self.make_button(bottom, "View Reading List", self.show_reading_list, "#5269C9").pack(
            side="right", padx=(0, 12))

    def populate_books(self):
        query = self.search_var.get().strip().lower()
        genre = self.genre_var.get()
        results = [
            book for book in BOOKS
            if (genre == "All Genres" or book["genre"] == genre)
            and (not query or query in book_text(book).lower()
                 or query in str(book["year"]))
        ]
        sort = self.sort_var.get()
        if sort == "Highest Rated":
            results.sort(key=lambda b: b["rating"], reverse=True)
        elif sort == "Title A-Z":
            results.sort(key=lambda b: b["title"].lower())
        elif sort == "Newest":
            results.sort(key=lambda b: b["year"], reverse=True)
        else:
            results.sort(key=lambda b: (-b["rating"], b["title"].lower()))

        self.tree.delete(*self.tree.get_children())
        for index, book in enumerate(results):
            self.tree.insert("", "end", iid=book["title"],
                             values=(book["title"], book["author"], book["genre"],
                                     f'{book["rating"]:.1f} ★', book["year"]))
        self.status_var.set(f"Showing {len(results)} of {len(BOOKS)} books.")
        self.recommendation_list.delete(0, tk.END)
        if results:
            self.recommendation_list.insert(tk.END, "Select a book, then click Recommend Similar.")
        else:
            self.recommendation_list.insert(tk.END, "No books match your search.")

    def on_book_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        title = selection[0]
        book = next((item for item in BOOKS if item["title"] == title), None)
        if not book:
            return
        self.selected_book = book
        self.detail_title.config(text=book["title"])
        self.detail_author.config(text=f'Author: {book["author"]}')
        self.detail_meta.config(text=f'Genre: {book["genre"]}  |  Rating: {book["rating"]:.1f}/5  |  Year: {book["year"]}')
        self.detail_description.config(text=book["description"])
        self.status_var.set(f'Selected "{book["title"]}".')

    def recommend_selected(self):
        if not self.selected_book:
            messagebox.showinfo("Select a book", "Please select a book from the catalog first.")
            return
        source = self.selected_book
        candidates = [book for book in BOOKS if book["title"] != source["title"]]
        candidates.sort(key=lambda book: (similarity(source, book), book["rating"]), reverse=True)
        top = candidates[:6]
        self.recommendation_list.delete(0, tk.END)
        for book in top:
            score = similarity(source, book)
            self.recommendation_list.insert(
                tk.END, f'{book["title"]}  |  {book["genre"]}  |  ★ {book["rating"]:.1f}  |  Match {score * 100:.0f}%'
            )
        self.status_var.set(f'Showing books similar to "{source["title"]}".')

    def open_recommendation(self, _event=None):
        selection = self.recommendation_list.curselection()
        if not selection:
            return
        line = self.recommendation_list.get(selection[0])
        title = line.split("  |  ")[0]
        book = next((item for item in BOOKS if item["title"] == title), None)
        if book:
            self.selected_book = book
            self.detail_title.config(text=book["title"])
            self.detail_author.config(text=f'Author: {book["author"]}')
            self.detail_meta.config(text=f'Genre: {book["genre"]}  |  Rating: {book["rating"]:.1f}/5  |  Year: {book["year"]}')
            self.detail_description.config(text=book["description"])
            for item in self.tree.selection():
                self.tree.selection_remove(item)
            if self.tree.exists(book["title"]):
                self.tree.selection_set(book["title"])
                self.tree.see(book["title"])
            self.status_var.set(f'Opened recommendation "{book["title"]}".')

    def add_to_reading_list(self):
        if not self.selected_book:
            messagebox.showinfo("Select a book", "Please select a book first.")
            return
        title = self.selected_book["title"]
        if title in self.reading_list:
            messagebox.showinfo("Already saved", f'"{title}" is already in your reading list.')
            return
        self.reading_list.append(title)
        self.status_var.set(f'Added "{title}" to your reading list.')

    def show_reading_list(self):
        window = tk.Toplevel(self.root)
        window.title("My Reading List")
        window.geometry("560x420")
        window.configure(bg=BG)
        tk.Label(window, text="My Reading List", bg=BG, fg=TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(18, 5))
        tk.Label(window, text="Your saved books are kept while this app is open.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(0, 12))
        listing = tk.Listbox(window, bg=CARD_DARK, fg=TEXT, selectbackground=ACCENT_DARK,
                             font=("Segoe UI", 11), bd=0, highlightthickness=0)
        listing.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        for title in self.reading_list:
            book = next(b for b in BOOKS if b["title"] == title)
            listing.insert(tk.END, f'{book["title"]} — {book["author"]}')
        if not self.reading_list:
            listing.insert(tk.END, "Your reading list is empty.")
        buttons = tk.Frame(window, bg=BG)
        buttons.pack(fill="x", padx=18, pady=(0, 18))

        def remove_selected():
            idx = listing.curselection()
            if not idx or not self.reading_list:
                return
            del self.reading_list[idx[0]]
            listing.delete(0, tk.END)
            for title in self.reading_list:
                book = next(b for b in BOOKS if b["title"] == title)
                listing.insert(tk.END, f'{book["title"]} — {book["author"]}')
            if not self.reading_list:
                listing.insert(tk.END, "Your reading list is empty.")
            self.status_var.set("Reading list updated.")

        self.make_button(buttons, "Remove Selected", remove_selected, RED).pack(side="left")
        self.make_button(buttons, "Close", window.destroy, "#5269C9").pack(side="right")

    def show_top_rated(self):
        top = sorted(BOOKS, key=lambda book: book["rating"], reverse=True)[:6]
        self.recommendation_list.delete(0, tk.END)
        for book in top:
            self.recommendation_list.insert(
                tk.END, f'{book["title"]}  |  {book["genre"]}  |  ★ {book["rating"]:.1f}  |  {book["year"]}'
            )
        self.status_var.set("Showing the six highest-rated books in the sample catalog.")

    def reset_filters(self):
        self.search_var.set("")
        self.genre_var.set("All Genres")
        self.sort_var.set("Recommended")
        self.populate_books()
        self.selected_book = None
        self.detail_title.config(text="No book selected")
        self.detail_author.config(text="Author: —")
        self.detail_meta.config(text="Genre: —  |  Rating: —  |  Year: —")
        self.detail_description.config(text="Book description will appear here.")
        self.status_var.set("Filters reset.")

    def update_clock(self):
        from datetime import datetime
        self.clock_label.config(text=datetime.now().strftime("%d %b %Y  •  %I:%M:%S %p"))
        self.root.after(1000, self.update_clock)


if __name__ == "__main__":
    root = tk.Tk()
    app = BookRecommendationApp(root)
    root.mainloop()
