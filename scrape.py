import csv
import os
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

URL = "https://www.psacard.com/pop/tcg-cards/2001/pokemon-japanese-vs/63661"
CSV_FILE = "psa_data.csv"

def main():
    # Fetch the page with a desktop viewport to prevent PSA's mobile layout from collapsing the table
    page = StealthyFetcher.fetch(URL)
    
    # 1. Locate the correct Population Report table 
    tables = page.css('table')
    target_table = None
    headers = []
    
    for table in tables:
        th_elements = table.css('thead th')
        th_texts = [th.xpath('string(.)').get(default="").strip().upper() for th in th_elements]
        # Make sure we are looking at the card list table, not the aggregate summary table
        if any(h in ["SUBJECT", "NAME", "CARD NAME", "CARD NO", "NO"] for h in th_texts):
            target_table = table
            headers = th_texts
            break
            
    if not target_table:
        print("Error: Could not find the main population table.")
        return

    # 2. Dynamically map column positions based on the headers
    idx_num, idx_name, idx_9, idx_10, idx_total = -1, -1, -1, -1, -1
    for i, h in enumerate(headers):
        if "NO" in h and "CARD" in h: idx_num = i
        elif "SUBJECT" in h or "NAME" in h: idx_name = i
        elif h == "9": idx_9 = i
        elif h == "10": idx_10 = i
        elif "TOTAL" in h or "TOT" in h: idx_total = i

    rows = target_table.css('tbody tr')
    today = datetime.now().strftime('%Y-%m-%d')
    new_data = []
    
    for row in rows:
        tds = row.css('td')
        if len(tds) < 3:
            continue
            
        # 3. Use xpath('string(.)') to pull all text, bypassing nested tags/links
        card_num = tds[idx_num].xpath('string(.)').get(default="").strip() if idx_num != -1 else ""
        card_name = tds[idx_name].xpath('string(.)').get(default="").strip() if idx_name != -1 else ""
        
        card_num = " ".join(card_num.split())
        card_name = " ".join(card_name.split())
        
        # Skip weird separator/variety rows that lack names
        if not card_num and not card_name:
            continue
            
        psa_9 = tds[idx_9].xpath('string(.)').get(default="0").strip() if idx_9 != -1 else "0"
        psa_10 = tds[idx_10].xpath('string(.)').get(default="0").strip() if idx_10 != -1 else "0"
        total = tds[idx_total].xpath('string(.)').get(default="0").strip() if idx_total != -1 else "0"
        
        # PSA sometimes places a dash instead of a zero
        if psa_9 == "-": psa_9 = "0"
        if psa_10 == "-": psa_10 = "0"
        
        new_data.append([today, card_num, card_name, total, psa_10, psa_9])
    
    # 4. Write data
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Date', 'Card Number', 'Card Name', 'Total Pop', 'PSA 10', 'PSA 9'])
        writer.writerows(new_data)

if __name__ == "__main__":
    main()
