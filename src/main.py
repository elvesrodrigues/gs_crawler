import os
import json 
import random
import time 

import distance

from stem import Signal
from stem.control import Controller

from scholarly import ProxyGenerator, scholarly

TOR_PASSWORD = 'scholarly_password'

# Número máximo de vezes que se irá tentar realizar uma coleta.
MAX_ATTEMPTS = 30

# Número máximo de resultados da pesquisa. (10 corresponderia a primeira página)
MAX_NUM_RESULTS = 10

LOG_PATH = '../log/'
PROCESSEDS_PATH = LOG_PATH + 'processeds.txt'
ERROR_PATH = LOG_PATH + 'errors.txt'
DUMP_PATH = '../dump/'

def renew_tor_ip() -> None:
    '''Altera o IP do Tor. 
    '''

    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=TOR_PASSWORD)
        controller.signal(Signal.NEWNYM)

    # Espera um tempo aleatório para que a mudança de IP surta efeito. 
    time.sleep(random.randint(5, 17))

def get_queries_to_crawl() -> list:
    '''Retorna as queries que não foram processadas.

    Returns:
        Retorna uma lista de consultas a serem coletadas.
    '''
    processeds = set()

    if os.path.exists(PROCESSEDS_PATH):
        with open(PROCESSEDS_PATH) as f:
            for line in f.readlines():
                processeds.add(line.replace('\n', ''))

    queries = list()
    with open('../data/queries.jsonl') as f:
        for line in f.readlines():
            data = json.loads(line)
            key = f'{data["source"]}:{data["sid"]}' 
            
            if key not in processeds:
                queries.append((data['source'], data['title'], data['sid'], data['query']))
            
            else:
                print(f'{key} já foi coletado.')
    
    return queries 

def create_folders():
    '''Cria as pastas básicas para salvamentos dos arquivos de logs e coleta.
    '''
    if not os.path.exists(DUMP_PATH):
        os.makedirs(DUMP_PATH)

    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

if __name__ == '__main__':
    create_folders()

    # Utilizar o Tor com Proxie para que a coleta continue, mesmo após bloqueio de IP pelo Google.
    # Obs.: Tor precisa estar devidamente configurado. Mais detalhes aqui:
    #   - https://scholarly.readthedocs.io/en/latest/quickstart.html#pg-tor-external-tor-sock-port-int-tor-control-port-int-tor-password-str
    #   - https://github.com/scholarly-python-package/scholarly/blob/master/setup_tor.sh
    pg = ProxyGenerator()
    pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password=TOR_PASSWORD)
    scholarly.use_proxy(pg)

    queries = get_queries_to_crawl()
    
    queries_size = len(queries)
    it = 1

    dump = open(DUMP_PATH + 'bundle.jsonl', 'a')
    processeds = open(PROCESSEDS_PATH, 'a')
    errors = open(ERROR_PATH, 'a')

    for source, title, sid, query in queries:
        print(f'Processing "{query}" ({it}/{queries_size})...')

        attempt = 1
        while attempt <= MAX_ATTEMPTS:
            try:
                results = scholarly.search_pubs(query)
                for order, result in enumerate(results, 1):
                    if order > MAX_NUM_RESULTS:
                        break
                    
                    # remove objetos do dicionário que não são possíveis de fazer parsing em json
                    del result['container_type']
                    del result['source']

                    # melhora a formataçõa do dicionário final.
                    bib = result['bib']
                    del result['bib']
                    result.update(bib)

                    # insere metadados sobre a coleta

                    # tabela fonte da coleta. P.e.: Artigo, capítulo de livro...
                    result['source_table'] = source

                    # Id da publicação na tabela fonte da coleta.
                    result['source_id'] = sid
                    
                    # a consulta que gerou o resultado
                    result['query'] = query

                    # a ordem do resultado no ranking do Google para a consulta
                    result['order_in_results'] = order

                    # Distâncida de edição absoluta entre o título original da publicação e o resultado do Google
                    result['edit_dist_between_titles'] = distance.levenshtein(title, result.get('title', ''))

                    # Distância de edição normalizado entre 0 e 1 (distância de edição absoluta divididade pelo tamanho da maior sequência (resultado do Google ou título original))
                    result['normalized_edit_dist_between_titles'] = distance.levenshtein(title, result.get('title', ''), normalized=True)

                    dump.write(json.dumps(result) + '\n')
    
                processeds.write(f'{source}:{sid}\n')
                break

            except Exception as e:
                renew_tor_ip()

                print(f'\t[Erro {attempt}/{MAX_ATTEMPTS}]: {e}')
                print(f'\t\t Esperando por {15 * attempt}s...')

                # Tempo de espera para tentar recoleta aumenta progressivamente
                time.sleep(15 * attempt)
                attempt += 1 

        if attempt > MAX_ATTEMPTS:
            errors.write(f'{source}:{sid}\n')

        it += 1
        
    dump.close()
    processeds.close()
    errors.close()
