import requests
from bs4 import BeautifulSoup
import csv
import time

# Initialize list to store data
data = []

# Base URL
base_url = "https://police.byu.edu/police-beat-list?00000182-aebd-d773-a387-ffff44970000-page="

# Number of pages to scrape (1 to 64)
start_page = 1
end_page = 64

# Loop through all pages
for page_num in range(start_page, end_page + 1):
    url = f"{base_url}{page_num}"
    print(f"Scraping page {page_num}...")
    
    try:
        # Make request with timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all police beat entries
        entries = soup.find_all('div', class_='PromoImageSmall')
        
        if not entries:
            print(f"No entries found on page {page_num}")
            continue
        
        # Loop through each entry
        for entry in entries:
            # Get the date
            date_span = entry.find('span', class_='date')
            date = date_span.text.strip() if date_span else "Date not found"
            
            # Get the description div
            description_div = entry.find('div', class_='PromoImageSmall-description')
            if description_div:
                # First check if there are list items
                incidents_li = description_div.find_all('li')
                
                if incidents_li:  # If there are <li> tags
                    for li in incidents_li:
                        incident_text = li.get_text(strip=True)
                        data.append({
                            'date': date,
                            'description': incident_text
                        })
                else:  # If no <li> tags, split by double <br>
                    description_text = str(description_div)
                    incidents = description_text.split('<br/><br/>')
                    
                    for incident in incidents:
                        incident_soup = BeautifulSoup(incident, 'html.parser')
                        incident_text = incident_soup.get_text(strip=True)
                        facebook_text = "Follow us on Facebookfor additional updates"
                        cleaned_text = incident_text.replace(facebook_text, "").strip()
                        if cleaned_text and '<ul>' not in incident:
                            data.append({
                                'date': date,
                                'description': cleaned_text
                            })
    
    except requests.exceptions.RequestException as e:
        print(f"Error scraping page {page_num}: {e}")
        continue
    
    # Add delay between requests (2 seconds)
    time.sleep(2)

# Print the results
for item in data:
    print(f"Date: {item['date']}")
    print(f"Description: {item['description']}")
    print("-" * 50)

# Save to CSV
with open('police_beat_data_all_pages.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['date', 'description'])
    writer.writeheader()
    writer.writerows(data)

print(f"Scraping complete. Total incidents collected: {len(data)}")
