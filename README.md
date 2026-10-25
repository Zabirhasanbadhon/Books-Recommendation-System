# ZaBir | Book Recommendation System

A desktop-based **Book Recommendation System** built with Python and Tkinter. It loads book records from a CSV dataset instead of relying on a manually written book list.

The app provides a searchable book catalog, genre filtering, sorting, book details, content-based recommendations, a temporary reading list, and a top-rated books view.

## Features

- **CSV dataset integration** — loads book records from your own `.csv` file.
- **Search books** — search across book titles, authors, genres, descriptions, and keywords.
- **Filter by genre** — choose a genre from the dropdown.
- **Sort the catalog** — sort by recommended order, highest rating, title (A–Z), or newest publication year.
- **Book details** — view a selected book's author, genre, rating, publication year, and description.
- **Similar-book recommendations** — recommends books using text similarity and a small bonus for matching genres.
- **Top-rated books** — quickly view the six highest-rated books in the dataset.
- **Reading list** — save books during the current app session and remove them later.
- **Dark-themed Tkinter interface** — a desktop GUI with search and filtering controls.

## Requirements

- Python 3.9 or newer recommended
- Tkinter (usually included with standard Python installations)
- A CSV dataset containing book information

**No third-party Python packages are required.** The code uses Python's built-in `csv`, `re`, and `pathlib` modules.


Your CSV filename can be different, as long as you update the path in the Python file.

## Setup and Run

### 1. Download or clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace the example repository URL with your own GitHub repository URL.

### 2. Add your CSV dataset

Place your dataset in the project folder, or keep it elsewhere on your computer.

### 3. Update the CSV path

Open `Books Recommendation Syatem.py` and find this line near the top:

```python
CSV_PATH = Path(r"C:\Users\YourName\Downloads\books.csv")
```

Change the path to the actual location of your dataset. For example, if `books.csv` is in the same folder as the Python file, you can use:

```python
CSV_PATH = Path("books.csv")
```

On Windows, a raw string path is also fine:

```python
CSV_PATH = Path(r"D:\Datasets\books.csv")
```

Save the file after changing the path.

### 4. Run the application

Open a terminal in the project folder and run:

```bash
Books Recommendation System.py
```

If your system uses `python3` to run Python, use:

```bash
Books Recommendation System.py
```

## CSV Dataset Format

The CSV file must have a header row and a book-title column. The loader accepts several common names for supported fields.

| Information | Recognized column names (examples) |
|---|---|
| Book title (**required**) | `title`, `book title`, `name` |
| Author | `authors`, `author`, `book author` |
| Genre | `genre`, `genres`, `category`, `categories`, `subject`, `subjects`, `book genre` |
| Rating | `average_rating`, `average rating`, `rating`, `book rating`, `score` |
| Publication year/date | `year`, `publication year`, `original publication year`, `published year`, `publication_date`, `published date` |
| Description | `description`, `book description`, `summary`, `synopsis`, `overview`, `about` |
| Keywords | `keywords`, `tags`, `subjects`, `categories`, `genre`, `genres` |

Column names are normalized, so underscores and spaces are generally treated equivalently. The CSV should use a standard comma-separated format with column names in the first row.

### Example CSV

```csv
title,authors,genre,average_rating,year,description,keywords
The Hobbit,J.R.R. Tolkien,Fantasy,4.8,1937,A fantasy adventure about a hobbit's journey,fantasy adventure dragons journey
Pride and Prejudice,Jane Austen,Classic,4.6,1813,A novel about manners and relationships,classic romance society relationships
```

This is only an example of the expected structure. You can use a larger dataset, including one from Kaggle, provided its column names and data are compatible.

## How Recommendations Work

The program creates a text representation of each book using its title, author, genre, description, and keywords. It tokenizes the text and calculates **Jaccard similarity** between two books. A bonus is added when both books have the same genre.

Recommendations therefore depend on the information available in your CSV. Datasets with useful genre labels, descriptions, and keywords generally support more informative recommendations.

> This is a lightweight content-based recommendation method. It does not train a machine-learning model or learn from user ratings and reading history.

## Data Handling Notes

- Rows without a title are skipped.
- Duplicate titles are skipped because the GUI uses titles as identifiers.
- Missing author values are displayed as `Unknown`.
- Missing genre values are displayed as `Other`.
- Missing ratings default to `0`; ratings from 0 to 10 are converted to a 0-to-5 scale, and values are limited to that range.
- The year is extracted from a recognizable four-digit year in the publication year/date field. If none is found, it defaults to `0`.
- Missing descriptions receive a placeholder message.
- The reading list exists only while the application is running; it is not saved to disk.

## Troubleshooting

### `FileNotFoundError`

Check that `CSV_PATH` points to the correct CSV file. Make sure the file exists and that the filename and extension are correct.

### The application says no books were loaded

Confirm that your CSV has a header row and a title column named `title`, `book title`, or `name`. Also check that the title cells are not all blank.

### Genre filtering or recommendations are not useful

Your dataset may not contain genre, description, or keyword information. Check the column names against the supported fields above, or choose a dataset with richer book metadata.

### Tkinter is unavailable

Use a standard Python installation that includes Tkinter. On some Linux distributions, Tkinter may need to be installed through the operating system's package manager.

## Possible Improvements

- Add persistent reading-list storage.
- Support multiple genres per book.
- Improve recommendations with TF-IDF or a trained recommendation model.
- Add unit tests and dataset validation.
- Add pagination for very large datasets.

## License

Choose a license for your repository before publishing (for example, MIT). If you use a third-party dataset, review and follow that dataset's license and attribution requirements separately.

---

**Built with Python and Tkinter.**
