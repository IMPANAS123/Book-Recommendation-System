from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import sys
import ratings  # Import ratings.py
import genre  # Import genre.py

# Add path to ratings.py to make sure it can be imported
sys.path.append(r"C:\Users\Ananya\OneDrive\Documents\Mini project")


# Initialize Flask app
app = Flask(__name__)

# Load the datasets
Genres = pd.read_excel("Genre_books.xlsx", engine="openpyxl")
data = pd.read_excel("Books.xlsx", engine="openpyxl")

# Feature engineering for the logistic regression model
label_encoder = LabelEncoder()
data["Author_Encoded"] = label_encoder.fit_transform(data["Book-Author"])
data["Publisher_Encoded"] = label_encoder.fit_transform(data["Publisher"])

scaler = MinMaxScaler()
data["Year_Normalized"] = scaler.fit_transform(data[["Year-Of-Publication"]])

# Create a synthetic target column ('recommend')
data["recommend"] = (data["Year-Of-Publication"] > 1980).astype(int)

# Feature matrix (X) and target vector (y) for the entire dataset
X = data[["Author_Encoded", "Publisher_Encoded", "Year_Normalized"]]
y = data["recommend"]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train the Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Save the model and scaler
joblib.dump(model, "book_recommendation_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

# Load Genre dataset (Book_Title and Genre)
genre_data = pd.read_excel("Genre_books.xlsx", engine="openpyxl")


@app.route("/", methods=["GET", "POST"])
def recommend_books():
    if request.method == "GET":
        # Get the number of books from query parameters
        number_of_books = request.args.get("num_books", type=int)

        if number_of_books is None:
            # If num_books is not provided, render the index.html page
            return render_template("index.html")

        # Get top and bottom books based on user input for number of books
        top_books = ratings.ratings(
            ["top"], number_of_books
        )  # Get the top N books from ratings.py
        bottom_books = ratings.ratings(
            ["bottom"], number_of_books
        )  # Get the bottom N books from ratings.py

        return render_template(
            "index.html", top_books=top_books, bottom_books=bottom_books
        )

    if request.method == "POST":
        user_input = (
            request.form["user_input"].strip().lower()
        )  # Convert user input to lowercase
        message = ""
        user_input = user_input.lower()
        try:
            if "hello" in user_input:
                message = "Hello! How can I assist you today?"
            elif "top" in user_input and "bottom" in user_input:
                # Look for both top and bottom numbers in the input
                numbers = [int(word) for word in user_input.split() if word.isdigit()]
                if len(numbers) == 2:
                    top_books_num, bottom_books_num = numbers
                elif len(numbers) == 1:
                    top_books_num = numbers[0]
                    bottom_books_num = numbers[0]

                top_books = ratings.ratings(["top"], top_books_num)
                bottom_books = ratings.ratings(["bottom"], bottom_books_num)

                message = (
                    f"Top Books ({top_books_num}):\n" + "\n".join(top_books) + "\n\n"
                )
                message += f"Bottom Books ({bottom_books_num}):\n" + "\n".join(
                    bottom_books
                )

            elif "top" in user_input:  # Top X books request
                number_of_books = [
                    int(word) for word in user_input.split() if word.isdigit()
                ]
                number_of_books = number_of_books[0] if number_of_books else 5
                top_books = ratings.ratings(["top"], number_of_books)
                message = "\n".join(top_books)

            elif "bottom" in user_input:  # Bottom X books request
                number_of_books = [
                    int(word) for word in user_input.split() if word.isdigit()
                ]
                number_of_books = number_of_books[0] if number_of_books else 5
                bottom_books = ratings.ratings(["bottom"], number_of_books)
                message = f"Bottom Books ({number_of_books}):\n" + "\n".join(
                    bottom_books
                )

            elif "author" in user_input:  # Author-based recommendations
                author_name = user_input.split("author")[-1].strip()
                author_name_cleaned = " ".join(
                    [word for word in author_name.split() if word.lower() != "books"]
                )
                filtered_data = data[
                    data["Book-Author"].str.contains(
                        author_name_cleaned, case=False, na=False
                    )
                ].copy()

                if filtered_data.empty:
                    message = f"No books found for the author: {author_name_cleaned}"
                else:
                    X_filtered = filtered_data[
                        ["Author_Encoded", "Publisher_Encoded", "Year_Normalized"]
                    ]
                    filtered_data["predicted_recommend"] = model.predict(X_filtered)
                    recommended_books = filtered_data[
                        filtered_data["predicted_recommend"] == 1
                    ]

                    if recommended_books.empty:
                        message = (
                            f"No books recommended for author: {author_name_cleaned}"
                        )
                    else:
                        message = (
                            f"Recommended Books for Author: {author_name_cleaned}\n"
                        )
                        for _, book in recommended_books.iterrows():
                            message += (
                                f"{book['Book-Title']} by {book['Book-Author']}\n"
                            )

            elif "genre" in user_input:  # Genre-based recommendations
                genre_name = user_input.split("genre")[-1].strip().lower()
                # Match only the genre name, without "books" or extra text
                genre_name_cleaned = " ".join(
                    [word for word in genre_name.split() if word not in ["books"]]
                )

                # Search the data for the genre, matching case-insensitively
                genre_books = genre_data[
                    genre_data["Genre"].str.contains(
                        genre_name_cleaned, case=False, na=False
                    )
                ]

                if genre_books.empty:
                    message = (
                        f"No books found for genre: {genre_name_cleaned.capitalize()}"
                    )
                else:
                    message = f"Recommended Books for Genre: {genre_name_cleaned.capitalize()}\n"
                    for _, book in genre_books.iterrows():
                        message += f"{book['Book_Title']} - {book['Genre']}\n"

            else:
                message = "Invalid input. Please enter a valid request (e.g., 'top 5 books', 'bottom 5 books', or 'recommend books by <author>')."

        except Exception as e:
            message = f"Error processing the request: {str(e)}"

        return jsonify({"message": message})  # Return message as JSON


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
