import pandas as pd
from sklearn.model_selection import train_test_split  # to split the dataset
from sklearn.linear_model import LogisticRegression  # model
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import joblib

# Load the dataset with corrected file path and ensure openpyxl is used
data = pd.read_excel("Books.xlsx", engine="openpyxl")

# Feature engineering
# Encode categorical columns
label_encoder = LabelEncoder()
data["Author_Encoded"] = label_encoder.fit_transform(data["Book-Author"])
data["Publisher_Encoded"] = label_encoder.fit_transform(data["Publisher"])

# Normalize the year of publication
scaler = MinMaxScaler()
data["Year_Normalized"] = scaler.fit_transform(data[["Year-Of-Publication"]])

# Create a synthetic target column ('recommend')
# For demonstration, recommend books published after 1980
data["recommend"] = (data["Year-Of-Publication"] > 1980).astype(int)

# Input for filtering books by a specific author
author = input("Enter the author name: ")

# Filter the dataset for the given author
filtered_data = data[
    data["Book-Author"].str.contains(author, case=False, na=False)
].copy()  # Create a copy

if filtered_data.empty:
    print("No books found for the given author.")
else:
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

    # Features for prediction from the filtered data (same transformations applied)
    X_filtered = filtered_data[
        ["Author_Encoded", "Publisher_Encoded", "Year_Normalized"]
    ]

    # Predict recommendations for the filtered data
    filtered_data["predicted_recommend"] = model.predict(X_filtered)

    # Get only recommended books
    recommended_books = filtered_data[filtered_data["predicted_recommend"] == 1]

    if recommended_books.empty:
        print("No books recommended for this author.")
    else:
        # Display recommended books in list format
        print(f"\nRecommended Books for Author: {author.title()}")
        counter = 1  # Initialize counter to 1
        for _, book in recommended_books.iterrows():
            print(f"{counter}. {book['Book-Title']}")
            counter += 1  # Increment the counter for each book
