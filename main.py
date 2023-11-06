import requests
import sqlite3
from datetime import datetime

def obter_taxas_de_cambio():
    url = "https://api.hgbrasil.com/finance/quotations?format=json&key=d85766b2"  
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Erro ao obter dados da API")
        return None

def converter_moeda(valor, taxa_euro, taxa_dolar):
    valor_em_euro = valor / taxa_euro
    valor_em_dolar = valor / taxa_dolar
    return valor_em_euro, valor_em_dolar

def inserir_dados_no_banco(valor, valor_em_euro, valor_em_dolar, data_hora_consulta):
    conn = sqlite3.connect('cambio.db')  # Crie um banco de dados SQLite chamado "cambio.db" se não existir
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cotacoes (
            id INTEGER PRIMARY KEY,
            valor_em_reais REAL,
            valor_em_euro REAL,
            valor_em_dolar REAL,
            data_hora_consulta DATETIME
        )
    ''')

    cursor.execute("INSERT INTO cotacoes (valor_em_reais, valor_em_euro, valor_em_dolar, data_hora_consulta) VALUES (?, ?, ?, ?)",
                   (valor, valor_em_euro, valor_em_dolar, data_hora_consulta))

    conn.commit()
    conn.close()

def exibir_dados_do_banco():
    conn = sqlite3.connect('cambio.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cotacoes ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        id, valor_em_reais, valor_em_euro, valor_em_dolar, data_hora_consulta = row
        print(f"Data e Hora da Consulta: {data_hora_consulta}")
        print(f"Valor em Reais (BRL): {valor_em_reais:.2f}")
        print(f"Valor em Euro (EUR): {valor_em_euro:.2f}")
        print(f"Valor em Dólares (USD): {valor_em_dolar:.2f}")

    conn.close()

def main():
    data = obter_taxas_de_cambio()
    if data:
        taxa_euro = data["results"]["currencies"]["EUR"]["buy"]
        taxa_dolar = data["results"]["currencies"]["USD"]["buy"]
        
        valor_em_reais = float(input("Digite o valor em Reais (R$): "))
        
        valor_em_euro, valor_em_dolar = converter_moeda(valor_em_reais, taxa_euro, taxa_dolar)
        
        data_hora_consulta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        inserir_dados_no_banco(valor_em_reais, valor_em_euro, valor_em_dolar, data_hora_consulta)
        
        print(f"Valor em Euro (EUR): {valor_em_euro:.2f}")
        print(f"Valor em Dólares (USD): {valor_em_dolar:.2f}")
    
    exibir_dados_do_banco()

if __name__ == "__main__":
    main()
