from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime 

def log_progress(message):
    ''' This function logs the mentioned message of a given stage of the
    code execution to a log file. Function returns nothing'''

    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    
    with open("./code_log.txt","a") as f: 
        f.write(timestamp + ' : ' + message + '\n')    



def extract(url, table_attribs):
    page = requests.get(url).text
    data = BeautifulSoup(page,'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    heading = data.find('span', {'id': 'By_market_capitalization'})
    target_tables = heading.find_next('table')
    tables = target_tables.find_all('tbody')[0]
    rows = tables.find_all('tr')

    for row in rows:
            col = row.find_all('td')
            if len(col) != 0:
                ancher_data = col[1].find_all('a')[1]
                if ancher_data is not None:
                    data_dict = {
                        'Name': ancher_data.contents[0],
                        'MC_USD_Billion': col[2].contents[0]
                    }
                    df1 = pd.DataFrame(data_dict, index = [0])
                    df = pd.concat([df, df1], ignore_index = True)
    USD_list = list(df['MC_USD_Billion'])
    USD_list = [float(''.join(x.split('\n'))) for x in USD_list]
    df['MC_USD_Billion'] = USD_list

    return df



def transform(df, csv_path):
    csvfile = pd.read_csv(exchange_rate_path)

    # i made here the content for currenct is the keys and the content of 
    # the rate is the values to the crossponding keys
    dict = csvfile.set_index('Currency').to_dict()['Rate']

    df['MC_GBP_Billion'] = [np.round(x * dict['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x * dict['INR'],2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x * dict['EUR'],2) for x in df['MC_USD_Billion']]

    return df

def load_to_csv(df, output_path):
    df.to_csv(output_path)
    ''' This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing.'''

def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists = 'replace', index = False)

    ''' This function saves the final data frame to a database
    table with the provided name. Function returns nothing.'''

def run_query(query_statement, sql_connection):
    for query in query_statements:
        print(query)
        print(pd.read_sql(query, sql_connection), '\n')
    ''' This function runs the query on the database table and
    prints the output on the terminal. Function returns nothing. '''

''' Here, you define the required entities and call the relevant
functions in the correct order to complete the project. Note that this
portion is not inside any function.'''



url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
exchange_rate_path = 'exchange_rate.csv'
output_csv_path = 'Largest_banks_data.csv'
db_name = 'Banks.db'
conn = sqlite3.connect(db_name)
table_name = 'Largest_banks'
query_statements = [
        'SELECT * FROM Largest_banks',
        'SELECT AVG(MC_GBP_Billion) FROM Largest_banks',
        'SELECT Name from Largest_banks LIMIT 5'
    ]


log_progress('Preliminaries complete. Initiating ETL process')

df = extract(url, table_attribs)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df, exchange_rate_path)
log_progress('Data transformation complete. Initiating loading process.')

load_to_csv(df, output_csv_path)
log_progress('Data saved to CSV file.')

log_progress('SQL Connection initiated.')


load_to_db(df, conn, table_name)
log_progress('Data loaded to Database as table. Running the query.')

run_query(query_statements, conn)
conn.close()
log_progress('Process Complete.')








'''
df = transform(df)

log_progress('Data transformation complete. Initiating loading process')

load_to_csv(df, csv_path)

log_progress('Data saved to CSV file')

sql_connection = sqlite3.connect('World_Economies.db')

log_progress('SQL Connection initiated.')

load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')

query_statement = f"SELECT * from {table_name} WHERE GDP_USD_billions >= 100"
run_query(query_statement, sql_connection)

log_progress('Process Complete.')

sql_connection.close()'''