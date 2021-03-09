import os
import json 
import random
import time 

import distance

from stem import Signal
from stem.control import Controller

from scholarly import ProxyGenerator, scholarly

MAX_ATTEMPTS = 30
MAX_NUM_RESULTS = 10

LOG_PATH = '../log/'
PROCESSEDS_PATH = LOG_PATH + 'processeds.txt'
ERROR_PATH = LOG_PATH + 'errors.txt'
DUMP_PATH = '../dump/'

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="scholarly_password")
        controller.signal(Signal.NEWNYM)
    time.sleep(random.randint(5, 17))

def get_queries_to_crawl() -> list:
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
    if not os.path.exists(DUMP_PATH):
        os.makedirs(DUMP_PATH)

    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

if __name__ == '__main__':
    create_folders()

    pg = ProxyGenerator()
    pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
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
                    
                    del result['container_type']
                    del result['source']

                    bib = result['bib']
                    del result['bib']
                    result.update(bib)

                    result['source_table'] = source
                    result['source_id'] = sid
                    result['query'] = query
                    result['order_in_results'] = order
                    result['edit_dist_between_titles'] = distance.levenshtein(title, result.get('title', ''))
                    result['normalized_edit_dist_between_titles'] = distance.levenshtein(title, result.get('title', ''), normalized=True)

                    dump.write(json.dumps(result) + '\n')
    
                processeds.write(f'{source}:{sid}\n')
                break

            except Exception as e:
                renew_tor_ip()

                print(f'\t[Erro {attempt}/{MAX_ATTEMPTS}]: {e}')
                print(f'\t\t Esperando por {15 * attempt}s...')

                time.sleep(15 * attempt)
                attempt += 1 

        if attempt > MAX_ATTEMPTS:
            errors.write(f'{source}:{sid}\n')

        it += 1
        
    dump.close()
    processeds.close()
    errors.close()
