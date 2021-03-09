'''Código responsável por processar as planilhas e gerar uma entrada padrão para o coletor a partir das diferentes fontes.
'''

from glob import glob
import json
import re 

import pandas as pd 
from pandas.core.frame import DataFrame
from bs4 import BeautifulSoup

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
def clean_title(title: str) -> str:
    '''Realiza o parsing do título do artigo como html e remove alguns outros ruídos
    Args:
        - title: Título do artigo.
    
    Returns:
        Retorna o título do artigo com a remoção de ruídos.
    '''
    s = BeautifulSoup(title, 'lxml').getText()
    s = re.sub(CLEANR, '', s)
    s = s.replace('       ', ' ')
    return s.capitalize()

def get_query(title: str, first_author_last_name: str) -> str:
    '''Retorna uma consulta padronizada
    Args:
        - title: Título do artigo.
        - first_author_last_name: Sobrenome do primeiro autor.
    
    Returns:
        Retorna a consulta a ser coletada. 

    '''
    return f'{title} {first_author_last_name}'.capitalize()

def process_dataframe(df: DataFrame, filename: str, title: str, save_df_as_csv: bool = True):
    '''Responsável por criar as consultas padronizadas para o coletor, a partir das planilhas.
    
    Args:
        - df: Dataframe com os dados a serem processados.
        - filename: Nome do arquivo fonte.
        - title: Variável que representa qual é o título do artigo.
        - save_df_as_csv: Se é para salvar o dataframe como csv (default True)
    
    '''
    
    if 'ID' not in df:
        df['ID'] = range(1, df.shape[0] + 1)

    with open('queries.jsonl', 'w') as f:
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
    '''Organiza as diversas planilhas para serem processadas.

    Args:
        - files: Lista com o caminho da planilha.

    '''
    with open('raw/titles.json') as f:
        titles = json.loads(f.read())

        for file in files:
            filename = file.split('/')[-1].split('.')[0] 

            df = pd.read_excel(file)
            process_dataframe(df, filename, titles[filename])

if __name__ == '__main__':
    files = glob('raw/*.xls*')
    process_files(files)
