# genre.py
def get_books_by_genre(genre_name):
    # Ensure genre_name is processed properly
    genre_name = genre_name.lower().strip()

    # Logic to fetch books by genre from the dataset (adjust as needed)
    filtered_books = data[data['Genre'].str.contains(genre_name, case=False, na=False)]
    
    if filtered_books.empty:
        return {"message": f"No books found for genre: {genre_name}", "books": []}

    books = filtered_books['Book-Title'].tolist()
    return {"message": f"Books found for genre: {genre_name}", "books": books}
