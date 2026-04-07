import csv
import os
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

URL = "https://www.psacard.com/pop/tcg-cards/2001/pokemon-japanese-vs/63661"
CSV_FILE = "psa_data.csv"

def main():
    # StealthyFetcher bypasses Cloudflare protections automatically
    page = StealthyFetcher.fetch(URL)
    
    rows = page.css('table tbody tr')
    
    today = datetime.now().strftime('%Y-%m-%d')
    new_data = []
    
    for row in rows:
        tds = row.css('td')
        if len(tds) > 10:
            card_num = tds[0].css('::text').get(default="").strip()
            card_name = tds[1].css('::text').get(default="").strip()
            # Index positions may need adjustment based on the live table layout
            psa_9 = tds[11].css('::text').get(default="0").strip()
            psa_10 = tds[12].css('::text').get(default="0").strip()
            total = tds[-1].css('::text').get(default="0").strip()
            
            new_data.append([today, card_num, card_name, total, psa_10, psa_9])
    
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Date', 'Card Number', 'Card Name', 'Total Pop', 'PSA 10', 'PSA 9'])
        writer.writerows(new_data)

if __name__ == "__main__":
    main()
