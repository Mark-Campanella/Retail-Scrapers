import pandas as pd
import re
from fractions import Fraction



# Função para limpar a coluna 'Review Amount'
def clean_reviews(reviews):
    if isinstance(reviews, str):
        if 'be the first to write a review' in reviews:
            return 0
        else:
            # Usar regex para remover todos os caracteres não numéricos
            reviews = re.sub(r'\D', '', reviews)
            return reviews
    return reviews
# Função para limpar a coluna 'Description'
def clean_brackets(text):
    # Adicione qualquer lógica de limpeza específica para a coluna 'Description' aqui
    return text.replace('[','').replace(']','')  # Exemplo de limpeza simples (remover espaços em branco)

# Função para remover 'cubic feet' das colunas 'Capacity' e 'Dryer Capacity'
def clean_capacity(capacity):
    if isinstance(capacity, str):
        return capacity.replace(' cubic feet', '').strip()
    return capacity

def fill_brand_from_name(row):
    if pd.isna(row['Brand']):
        row['Brand'] = row['Name'].split()[0]
    return row

# Cleans SKU, Creates OBX column
def clean_SKU(sku):
    if 'obx' in sku:
        return 'Yes', sku.replace('obx ', '').strip()
    return '', sku

def convert_to_decimal(value):
    # remove inches
    value = value.replace(' inches', '').strip()
    
    # If there is a space → there is a fraction
    if ' ' in value:
        parts = value.split()
        # convert fraction into decimal
        whole = float(parts[0])
        fraction = float(Fraction(parts[1]))
        return round(whole + fraction, 2)
    else:
        return round(float(value), 2)
    
def cleanup(df:pd.DataFrame):
    df = df.dropna(axis=1, how = 'all')
    df = df.dropna(axis=0, how = 'all')

    df = df.apply(fill_brand_from_name, axis=1)

    df['Description'] = df['Description'].apply(clean_brackets)
    df['More Images Links'] = df['More Images Links'].apply(clean_brackets)
    df['Videos Links'] = df['Videos Links'].apply(clean_brackets)

    df['Review Amount'] = df['Review Amount'].apply(clean_reviews)

    df['Capacity'] = df['Capacity'].apply(clean_capacity)
    df['Dryer Capacity'] = df['Dryer Capacity'].apply(clean_capacity)
    df['Washer Capacity'] = df['Washer Capacity'].apply(clean_capacity)
    df['Capacity'] = df['Capacity'].fillna(df['Washer Capacity'])
    df['Capacity'] = df['Capacity'].fillna(df['Dryer Capacity'])

    df['Product Depth'] = df['Product Depth'].apply(convert_to_decimal)
    df['Product Height'] = df['Product Height'].apply(convert_to_decimal)
    df['Product Width'] = df['Product Width'].apply(convert_to_decimal)


    df['SKU'] = df['SKU'].astype(str)
    df['SKU'] = df['SKU'].str.lower()
    df[['OBX', 'SKU']] = df['SKU'].apply(lambda x: pd.Series(clean_SKU(x)))

    #ASK IF:
    #df['Voltage'] = df['Voltage'].fillna(df['Washer Voltage'])
    return df
    df.to_csv('../../outputs/product_cleaned.csv')

