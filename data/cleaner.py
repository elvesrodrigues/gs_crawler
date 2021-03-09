from glob import glob
import json
import re 

import pandas as pd 
from bs4 import BeautifulSoup

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
def clean_title(title: str) -> str:
    s = BeautifulSoup(title, 'lxml').getText()
    s = re.sub(CLEANR, '', s)
    s = s.replace('       ', ' ')
    return s

def get_query(title: str, first_author_last_name: str) -> str:
    return f'{title} {first_author_last_name}'.capitalize()

def process_dataframe(df, filename: str, title: str, save_df_as_csv: bool = True):
    if 'ID' not in df:
        df['ID'] = range(1, df.shape[0] + 1)

    with open('queries.jsonl', 'a') as f:
        for _, row in df.iterrows():
            first_author_last_name = row.NOMEPARACITACAO.split('|')[0].split(',')[0]
            pub_title = clean_title(row[title])
            query = get_query(pub_title, first_author_last_name)
            sid = row.ID

            f.write(json.dumps({
                'source': filename, 
                'sid': sid, 
                'query': query, 
                'title': pub_title
            }) + '\n')

    if save_df_as_csv:
        df.to_csv(f'csv/{filename}.csv')

def process_files(files: list):
    with open('raw/titles.json') as f:
        titles = json.loads(f.read())

        for file in files:
            filename = file.split('/')[-1].split('.')[0] 

            df = pd.read_excel(file)
            process_dataframe(df, filename, titles[filename])

if __name__ == '__main__':
    files = glob('raw/*.xls*')
    process_files(files)
