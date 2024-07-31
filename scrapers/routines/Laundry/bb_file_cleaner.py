import pandas as pd
import re
from fractions import Fraction
import ast

def cleanup(df: pd.DataFrame):
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
        # Verifica se o texto é uma string que parece uma lista
        if isinstance(text, list):
            # Se for uma lista, remover os colchetes de cada item da lista
            return '\n'.join([str(item).replace('[','').replace(']','') for item in text])
        elif isinstance(text, float):
            return text
        else:
            # Se não for uma lista ou não puder ser avaliado, simplesmente remover os colchetes
            return text.replace('[','').replace(']','')  
        
        # Função para remover 'maxHeight=120;maxWidth=120'
    def remove_max_dimensions(text):
        if isinstance(text, str):
            return text.replace(';maxHeight=120;maxWidth=120', '').strip()
        return text

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
        
        
    
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')
    try:
        df = df.apply(fill_brand_from_name, axis=1)
    except Exception as e: print('Not able to fill out name', e)
    try:
        df['Description'] = df['Description'].apply(clean_brackets)
        df['More Images Links'] = df['More Images Links'].apply(clean_brackets).apply(remove_max_dimensions)
        df['Videos Links'] = df['Videos Links'].apply(clean_brackets)
    except Exception as e:
        print('not able to cleanup list-like objects', e)
    try:
        df['Review Amount'] = df['Review Amount'].apply(clean_reviews)
    except Exception as e:
        print('Review Amount not cleaned', e)
        
    df['Capacity'] = df['Capacity'].apply(clean_capacity)
    try:
        df['Dryer Capacity'] = df['Dryer Capacity'].apply(clean_capacity)
        df['Washer Capacity'] = df['Washer Capacity'].apply(clean_capacity)
        df['Capacity'] = df['Capacity'].fillna(df['Washer Capacity'])
        df['Capacity'] = df['Capacity'].fillna(df['Dryer Capacity'])
    except Exception as e:
        print('No cleanup done in alternatives capacities', e)
    try:
        df['Product Depth'] = df['Product Depth'].apply(convert_to_decimal)
        df['Product Height'] = df['Product Height'].apply(convert_to_decimal)
        df['Product Width'] = df['Product Width'].apply(convert_to_decimal)
    except Exception as e: 
        print('Not able to convert from fraction to decimal', e)
    try:
        df['SKU'] = df['SKU'].astype(str)
        df['SKU'] = df['SKU'].str.lower()
        df[['OBX', 'SKU']] = df['SKU'].apply(lambda x: pd.Series(clean_SKU(x)))
    except Exception as e:
        print('No cleanup on the SKU // OBX done', e)
        
    # df['Voltage'] = df['Voltage'].fillna(df['Washer Voltage'])
    return df

