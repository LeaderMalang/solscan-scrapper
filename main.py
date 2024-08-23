from botasaurus import *
from botasaurus.browser import browser,Driver
from botasaurus.browser import Wait
from botasaurus import bt 
import time
import os 
import csv
import sys

if len(sys.argv) < 1:
    print("Usage: python main.py <Token_ADDRESS> ")
    sys.exit(1)

arg_token_address=sys.argv[1]
url=f"https://solscan.io/token/{arg_token_address}?activity_type=ACTIVITY_SPL_MINT"

#headless=True
@browser(wait_for_complete_page_load=True)
def scrape_heading_task(driver: Driver, data):
    driver.get(url)
    time.sleep(5)
   
    
    atr=None
    while True:
        time.sleep(4)
        trs=driver.select_all("tr",wait=Wait.LONG)
        next=driver.select(".anticon-right",wait=Wait.LONG).parent
        atr=next.get_attribute("disabled")
        
        
        signatures=[]
        for index,tr in enumerate(trs):
            if index==0:
                continue
            tds=tr.select_all("td")
            
            signature=tds[1].select('a').href
            signatures.append("https://solscan.io"+signature)
        
        if atr=="":
            break
        next.click()
        time.sleep(3)
    
    return signatures

@browser(wait_for_complete_page_load=True)
def get_wallet(driver: Driver,link):
    driver.get(link)
    time.sleep(3)
    # links=driver.select_all(".text-link")
    from_wallet=driver.get_element_containing_text("Signer",wait=Wait.LONG).parent.parent.select("a").text
    
    transaction={
                "mint wallet":from_wallet,
                
                "token":url.split("?")[0],
                "Dexscreener":f"https://dexscreener.com/solana/{arg_token_address}?maker={from_wallet}"

            }
    write_to_csv([transaction])
    return from_wallet

@browser(wait_for_complete_page_load=True)
def get_account_tokens(driver : Driver,from_wallet):
    account_url=f"https://solscan.io/account/{from_wallet}#portfolio"
    driver.get(account_url)
    time.sleep(2)
    tokens=driver.select_all("tr",wait=Wait.LONG)
    list_tokens=[]
    for index,token in enumerate(tokens):
        if index==0:
            continue
        tds=token.select_all('td')
        token_address=tds[1].select("a").href.split("/")[2]
        transaction={
                "mint wallet":from_wallet,
                
                "token":f"https://solscan.io/token/{token_address}",
                "Dexscreener":f"https://dexscreener.com/solana/{token_address}?maker={from_wallet}"

            }
        list_tokens.append(transaction)
    write_to_csv(list_tokens)
    return list_tokens    

def write_to_csv(filtered_transactions, filename="filtered_transactions.csv"):
    # Check if the file already exists
    file_exists = os.path.exists(filename)

    # Open the file in append mode if it exists, otherwise in write mode
    with open(filename, 'a' if file_exists else 'w', newline='') as csvfile:
        fieldnames = ["mint wallet","token","Dexscreener"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file did not previously exist
        if not file_exists:
            writer.writeheader()

        # Write the filtered transactions to the CSV file
        for transaction in filtered_transactions:
            writer.writerow(transaction)

    print(f"Successfully {'appended' if file_exists else 'written'} {len(filtered_transactions)} transactions to {filename}.")


if __name__ == "__main__":
    

    links=scrape_heading_task()
    account=get_wallet(links)
    get_account_tokens(account)
    

