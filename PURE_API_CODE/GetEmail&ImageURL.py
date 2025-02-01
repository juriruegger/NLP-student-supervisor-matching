import csv
import requests

# API configuration
API_KEY = "7624b829-efa4-4b7f-8e3d-4fcb295bd819"
BASE_URL = "https://pure.itu.dk/ws/api"

# Input and output file paths
input_file = "merged_embeddings_with_org_units_and_uuid.csv"
output_file = "output.csv"

# Function to get researcher details from the API
def get_researcher_details(uuid):
    url = f"{BASE_URL}/persons/{uuid}"
    headers = {
        "accept": "application/json", 
        "api-key": API_KEY,
    }
    params = {
        "fields": "name,staffOrganizationAssociations,profilePhotos",
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Fetching details for UUID: {uuid}")
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()

        # Extract email
        email = "Unknown"
        associations = data.get("staffOrganizationAssociations", [])
        for association in associations:
            emails = association.get("emails", [])
            if emails:
                email = emails[0].get("value", "Unknown")
                break

        # Extract profile photo URL
        profile_photos = data.get("profilePhotos", [])
        image_url = profile_photos[0].get("url", "No Image Available") if profile_photos else ""

        return email, image_url
    except Exception as e:
        print(f"Error fetching details for UUID {uuid}: {e}")
        return "Unknown", "No Image Available"

# Read input CSV and fetch details for each researcher
output_data = []
with open(input_file, mode="r", newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    # Remove spaces and converting to lowercase
    reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
    fieldnames = reader.fieldnames + ["researcher_email", "image_url"]  # Add new columns

    for row in reader:
        # Normalize row keys for consistent access
        row = {key.strip().lower(): value for key, value in row.items()}
        print(f"Processing row: {row}")  # Debugging: Print row to verify structure

        uuid = row.get("researcher_uuid", "").strip()
        if not uuid:
            print(f"Missing UUID for row: {row}")
            row["researcher_email"] = "Missing UUID"
            row["image_url"] = "Missing UUID"
        else:
            email, image_url = get_researcher_details(uuid)
            row["researcher_email"] = email
            row["image_url"] = image_url
        output_data.append(row)

# Write the output data to the csv file
with open(output_file, mode="w", newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_data)

print(f"Data saved to {output_file}")