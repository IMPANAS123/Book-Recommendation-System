import pandas as pd
import sys
import os

# Check if the CSV file exists
if not os.path.exists("Books_Data_Clean.csv"):
    print("Error: The file 'Books_Data_Clean.csv' is missing.")
    sys.exit(1)

# Load the CSV file
Ratings = pd.read_csv("Books_Data_Clean.csv")

# Sort the books by rating in descending order
Ratings_sorted = Ratings.sort_values(by="Book_average_rating", ascending=False)


# Function to display books in a structured way
def displaying(Rate):
    result = []
    index = 1
    for row in Rate["Book_Name"]:
        result.append(f"{index}. {row}")
        index += 1
    return result


# Determine the basis of the hierarchy (top or bottom)
def ratings(hierarchy, Number):
    result = []
    if "top" in hierarchy:
        result.append(f"Top {Number} books are")
        Top_Ratings = Ratings_sorted.head(Number)
        result.extend(displaying(Top_Ratings))  # Add top books to the result list

    if "bottom" in hierarchy:
        result.append(f"Bottom {Number} books are")
        Bottom_Ratings = Ratings_sorted.tail(Number)
        result.extend(displaying(Bottom_Ratings))  # Add bottom books to the result list

    return result if result else ["Invalid hierarchy. Please choose 'top' or 'bottom'."]


# Main function for executing based on command line args
if __name__ == "__main__":
    if len(sys.argv) > 2:
        hierarchy = sys.argv[1].split(
            ","
        )  # Accepting both top and bottom separated by comma
        try:
            number = int(sys.argv[2])  # number of books
            if hierarchy and number > 0:
                books = ratings(hierarchy, number)
                # Print each book name on a new line
                for book in books:
                    print(book)
            else:
                print("Invalid number of books.")
        except ValueError:
            print("Invalid number provided.")
    else:
        print("Usage: python ratings.py <top/bottom> <number>")
