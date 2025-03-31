import pandas as pd
import re

def extract_incident_type(description):
    """
    Extract the incident type from the beginning of the description.
    Handles cases where there's no space between incident type and description.
    """
    if pd.isna(description):
        return "Other"
    
    # Common incident types based on your data
    common_types = [
        "Unsecured Door", "Trespassing", "Lost Property", "Medical", "Suspicious Person",
        "Welfare Check", "Accident", "Alarm", "Traffic Offense", "Theft", "Fire Alarm",
        "Criminal Mischief", "Property Damage", "Sick Person", "Suspicious", "Found Property",
        "Information", "Sex Offense", "Suspicious Circumstance", "Escort", "Glass Break",
        "Drugs", "Missing Child", "Citizen Assist", "Animal Problem", "Overdose", 
        "Fire", "Fraud", "Abandoned Vehicle", "Pursuit", "Agency Assist", "Citizen Contact",
        "Keep the Peace", "Domestic Violence", "Vehicle Theft", "Public Peace - Noise Complaint",
        "Report of Smoke - Fire", "Gas Smell", "Assault", "Extortion", "Trauma", "Threatening", "Unconscious", "Trespass", "Harassment", "Skateboarding", "BYU EMS", "Damage", "Disorderly",
        "Disturbance","Fall", "DUI", "Fireworks", "Fire Alarm", "Robbery Alarm", "Suicide Attempt", "Fire Alarms"
    ]
    
    # Create regex pattern for common types, looking for cases with and without spaces
    prefixes = "(" + "|".join([re.escape(t) for t in common_types]) + ")"
    pattern = f"^{prefixes}(?=\\s|[A-Z])"
    
    match = re.search(pattern, description)
    if match:
        return match.group(1)
    
    # If no match with known types, try a more general approach
    # This tries to identify the incident type based on capitalization patterns, and em dashes.
    pattern = r'^([A-Z][a-zA-Z\s\-–—]+?)(?=[A-Z][a-z]|$)'
    match = re.search(pattern, description)
    if match:
        incident_type = match.group(1).strip()
        # Handle special cases with em dashes and other similar characters
        incident_type = incident_type.split('–')[0].split('—')[0].strip()
        return incident_type
    
    return "Uncategorized"  # Default if no pattern is found

def clean_description(row):
    """
    Remove the incident type from the beginning of the description.
    Handles cases where there's no space between incident type and description.
    """
    if pd.isna(row['description']) or pd.isna(row['incident_type']) or row['incident_type'] == "Uncategorized":
        return row['description']
    
    # Find the first occurrence of the incident type and remove it
    incident_type = row['incident_type']
    description = row['description']
    
    # Check if there's a space after the incident type
    if description.startswith(incident_type + " "):
        cleaned = description[len(incident_type) + 1:]
    # Check if the incident type is directly followed by the description (no space)
    elif description.startswith(incident_type):
        cleaned = description[len(incident_type):]
    else:
        cleaned = description
    
    # Remove any leading dash or separator
    cleaned = re.sub(r'^[\s\-–—]+', '', cleaned)
    
    return cleaned.strip()

def process_police_reports_csv(input_file, output_file):
    """
    Process a CSV file containing police reports.
    Extracts incident types and cleans descriptions.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the output CSV file
    
    Returns:
        DataFrame: The processed data
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully loaded CSV with {len(df)} rows and columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None
    
    # Check if 'description' column exists
    if 'description' not in df.columns:
        print("Error: CSV file must contain a 'description' column")
        print(f"Available columns: {', '.join(df.columns)}")
        return None
    
    # Extract incident types
    df['incident_type'] = df['description'].apply(extract_incident_type)
    
    # Clean descriptions by removing the incident type
    df['clean_description'] = df.apply(clean_description, axis=1)
    
    # Save to CSV
    try:
        df.to_csv(output_file, index=False)
        print(f"Successfully saved cleaned data to {output_file}")
    except Exception as e:
        print(f"Error saving CSV: {e}")
    
    return df

if __name__ == "__main__":
    input_file = "police_beat_data_all_pages.csv"
    output_file = "Cleaned_police_beat_data.csv"
    
    # Process the data
    processed_df = process_police_reports_csv(input_file, output_file)
    
    # Display a sample of the processed data
    if processed_df is not None:
        print("\nSample of processed data:")
        print(processed_df[['incident_type', 'clean_description']].head(3))
        
        # Count the unique incident types for verification
        incident_counts = processed_df['incident_type'].value_counts()
        print(f"\nFound {len(incident_counts)} unique incident types.")
        print("Top 10 incident types:")
        print(incident_counts.head(10))