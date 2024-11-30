import joblib
import pandas as pd

# Load the pre-fitted LabelEncoder
label_encoder = joblib.load(
    "C:/Users/Ananya/OneDrive/Documents/Mini project/label_encoder.pkl"
)

# Load the pre-fitted scaler (if needed for normalization)
scaler = joblib.load("C:/Users/Ananya/OneDrive/Documents/Mini project/scaler.pkl")

# Load the saved model
model = joblib.load(
    "C:/Users/Ananya/OneDrive/Documents/Mini project/model/Booksnames.pkl"
)  # Ensure the path is correct

# Load the new data for prediction
new_data = pd.read_excel("Books.xlsx", engine="openpyxl")

# Apply the same transformations (encoding and normalization) to the new data
new_data["Author_Encoded"] = label_encoder.transform(new_data["Book-Author"])
new_data["Publisher_Encoded"] = label_encoder.transform(
    new_data["Publisher"]
)  # Similarly for Publisher

# Normalize the "Year-Of-Publication" column using the pre-fitted scaler
new_data["Year_Normalized"] = scaler.transform(new_data[["Year-Of-Publication"]])

# Prepare the feature matrix for prediction
X_new = new_data[["Author_Encoded", "Publisher_Encoded", "Year_Normalized"]]

# Make predictions
predictions = model.predict(X_new)

# Display the predictions
print("Predictions:", predictions)
