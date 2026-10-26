# 📚 ZaBir HaSan | Book Recommendation System

A desktop-based **Book Recommendation System** developed using Python and Tkinter. The application allows users to explore books, search by title or author, filter by genre, sort books, discover similar recommendations, and maintain a personal reading list.

The application loads book information from a CSV dataset and uses content-based similarity matching to recommend books.

## ✨ Features

- **📖 Book Catalog:** Browse books with their titles, authors, genres, ratings, and publication years.
- **🔍 Search Books:** Search using book titles, authors, genres, descriptions, and keywords.
- **🏷️ Genre Filtering:** Filter books by genre.
- **↕️ Sorting Options:** Sort books by recommended order, highest rating, title (A–Z), or newest publication year.
- **🤖 Book Recommendations:** Discover similar books using keyword matching and genre similarity.
- **⭐ Top-Rated Books:** View the six highest-rated books in the dataset.
- **📚 Reading List:** Add books to your reading list and remove saved books when needed.
- **📝 Book Details:** View author information, genre, rating, publication year, and description.
- **🎨 Cream White Theme:** A clean desktop interface with a warm, modern color scheme.
- **🕒 Live Clock:** Display the current date and time.
- **📂 CSV Dataset Support:** Load book information from an external CSV file.

## 🛠️ Technologies Used

- **Python** — Core programming language.
- **Tkinter** — Desktop graphical user interface.
- **ttk** — Styled interface components.
- **CSV** — Dataset loading and processing.
- **Regular Expressions (`re`)** — Text processing and keyword matching.
- **Pathlib** — File path management.

No third-party Python packages are required.

## 📋 Requirements

- Python 3.9 or later recommended.
- A compatible Windows, Linux, or macOS environment with Tkinter installed.
- A book dataset in CSV format.

## 📊 Dataset Format

The application supports common CSV column names for book information.

| Column | Description |
|---|---|
| `title` | Book title |
| `authors` | Author name or names |
| `genre` | Book genre or category |
| `average_rating` | Average book rating |
| `year` | Publication year |
| `description` | Book description or summary |
| `keywords` | Keywords, tags, or related subjects |

The loader recognizes several alternative column names. Missing optional fields receive default values, and duplicate book titles are skipped.

**Note:** The CSV file must contain a recognizable title column, such as `title`, `book title`, or `name`.

## 🧠 Recommendation Method

The system uses a simple content-based recommendation approach.

1. It extracts words from each book's title, author, genre, description, and keywords.
2. It calculates **Jaccard similarity** between the selected book and other books.
3. It adds a bonus for books that share the same genre.
4. It ranks the candidates by similarity and rating.
5. It displays up to six recommendations.

This approach does not require user accounts, training data, or a machine-learning model.

## ⚠️ Limitations

- Recommendations depend on the information available in the CSV dataset.
- The recommendation algorithm uses text and genre similarity rather than a trained machine-learning model.
- Reading-list entries are stored in memory and are not saved after the application closes.
- Book descriptions, ratings, and publication years depend on the quality and completeness of the dataset.

## 👨‍💻 Developer

**ZaBir HaSan**

*Book Recommendation System — Python Desktop Application*
