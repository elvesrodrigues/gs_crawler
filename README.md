# gs_crawler
Crawler de publicações do Google Scholar.

O projeto está organizado da seguinte forma:

- `data/`: Possui os dados base para serem processados. A pasta `data/raw/` contém as planilhas sem qualquer processamento. O código em `data/cleaner.py` irá processar seus dados de modo a converter as planilhas em csv (salvos em `data/csv`) e, principalmente, irá criar o arquivo `data/queries.jsonl`. Cada linha desse arquivo é uma entrada formatada para o coletor (em `src/main.py`). Caso a planilha não possuia o atributo `ID`, um será criado para ela. 
  - Caso queira adicionar outra planilha para ser coletada, a adicione na pasta `data/raw/` e no arquivo `data/raw/titles.json`, informe qual é o campo da planilha que representa o título de cada artigo. Veja o arquivo em questão para exemplos.
- `src/`: Código do coletor propriamente dito. Utiliza o arquivo `data/queries.jsonl` como fontes de consulta e salva em `dump/bundle.jsonl` a coleta realizada (a pasta será criada automaticamente, se não houver nenhuma coleta anterior). Identificador de coletas feitas com ou sem erro serão salvas em `log/` (criado automaticamente, conforme a necessidade).

## Instalação

**Criar e ativar o ambiente virtual**:

```bash
python3 -m venv venv
source venv/bin/activate
```

**Instalar os requisitos**:

```bash

pip install -U pip
pip install -r requeriments.txt
```

O Google bloqueia as requisições após certo tempo, então é necessário usar um Proxie para contornar isso. Foi usado o Tor, por ser simples e gratuito. Configure-o segundo a página do [`scholarly`](https://scholarly.readthedocs.io/en/latest/quickstart.html#pg-tor-external-tor-sock-port-int-tor-control-port-int-tor-password-str).

**Importante:** A senha padrão do Tor usada é `scholarly_password`. Certifique-se de usar esta mesma senha (seguindo o página do `scholarly`) ou altere o valor da variável `TOR_PASSWORD` em `src/main.py` de acordo.

## Uso

Basta ir para a pasta `src` e rodar o comando:

```bash
python main.py
```

As coletas serão salvas em `dump/bundle.jsonl`.

Cada consulta será tentada até 30 vezes, aumentando em 15 segundos progressivamente o intervalo entre uma tentativa e outra.
