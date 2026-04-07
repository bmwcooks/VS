import csv
import os
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

URL = "https://www.psacard.com/pop/tcg-cards/2001/pokemon-japanese-vs/63661"
CSV_FILE = "psa_data.csv"

def main():
    page = StealthyFetcher.fetch(URL)
    
    tables = page.css('table')
    target_table = None
    headers = []
    
    for table in tables:
        th_elements = table.css('thead th')
        th_texts = [" ".join(th.css('::text').getall()).strip().upper() for th in th_elements]
        if any(h in ["SUBJECT", "NAME", "CARD NAME", "CARD NO", "NO"] for h in th_texts):
            target_table = table
            headers = th_texts
            break
            
    if not target_table:
        return

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
            
        # CARD NUMBER
        num_texts = [t.strip() for t in tds[idx_num].css('::text').getall() if t.strip()]
        card_num = num_texts[0] if num_texts else ""
        
        # CARD NAME
        name_texts = [t.strip() for t in tds[idx_name].css('::text').getall() if t.strip()]
        # Remove the affiliate link text
        name_texts = [t for t in name_texts if "Shop with Affiliates" not in t]
        card_name = " ".join(name_texts)
        
        if not card_num and not card_name:
            continue
            
        # NUMBERS - Helper function to grab ONLY the top number
        def get_top_number(td_index):
            if td_index == -1: return "0"
            # Get all text pieces, ignore blanks
            texts = [t.strip() for t in tds[td_index].css('::text').getall() if t.strip()]
            # Grab the first piece of text (the top row)
            val = texts[0] if texts else "0"
            # If PSA puts a dash instead of a zero, fix it
            return "0" if val == "-" else val
            
        psa_9 = get_top_number(idx_9)
        psa_10 = get_top_number(idx_10)
        total = get_top_number(idx_total)
        
        new_data.append([today, card_num, card_name, total, psa_10, psa_9])
    
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Date', 'Card Number', 'Card Name', 'Total Pop', 'PSA 10', 'PSA 9'])
        writer.writerows(new_data)

if __name__ == "__main__":
    main()
