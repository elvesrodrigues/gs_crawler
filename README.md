# gs_crawler
Crawler de publicações do Google Scholar.

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

Cada consulta será tentada até 30 vezes, aumentando em 15 segundos progressivamente a cada erro.