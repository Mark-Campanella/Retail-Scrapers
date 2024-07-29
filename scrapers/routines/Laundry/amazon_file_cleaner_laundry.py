
import pandas as pd

def cleanup_BR(df:pd.DataFrame):
    # Remove substrings that we don't need
    df['Avaliações de clientes'] = df['Avaliações de clientes'].str.replace(' de 5 estrelas', '', regex=False)
    df['Review Count'] = df['Review Count'].str.replace(' avaliações de clientes', '', regex=False)
    #Brazilian pattern for price is getting in the way so I am changing them to USA format
    df['Price'] = df['Price'].str.replace('.','',regex=False)
    df['Review Count'] = df['Review Count'].str.replace('.','',regex=False)
    df['Avaliações de clientes'] = df['Avaliações de clientes'].str.replace(',','.',regex=False)
    df = df.loc[df['Tipo de Cabelo'].isna() | (df['Tipo de Cabelo'] == '')]
    df = df.loc[df['Tipo de suporte ou fixação'].isna() | (df['Tipo de suporte ou fixação'] == '')]
    df = df.loc[df['Desenho ou estampa'].isna() | (df['Desenho ou estampa'] == '')]
    df['Nome da marca'] = df['Nome da marca'].fillna(df['Marca'])
    df['Nome da marca'] = df['Nome da marca'].fillna(df['Fabricante'])   
    #Setting all Nome da Marca as lowercase 
    df['Nome da marca'] = df['Nome da marca'].str.lower()
    df['Nome da marca'] = df['Nome da marca'].fillna(df['Número do modelo'])
    df['Tensão'] = df['Tensão'].fillna(df['Voltagem'])
    df['Velocidade máxima de rotação'] = df['Velocidade máxima de rotação'].fillna(df['Velocidade máxima de centrifugação'])
    df['Número de Peças'] = df['Número de Peças'].fillna(df['Número de produtos'])
    df['Número de Peças'] = df['Número de Peças'].fillna(df['Número de unidades'])
    df['Número de Peças'] = df['Número de Peças'].fillna(df['Número de peças'])
    df['Potência'] = df['Potência'].fillna(df['Potência em watts'])
    df['Eficiência'] = df['Eficiência'].fillna(df['Etiqueta Nacional de Eficiência Energética (ENCE)'])
    df['Tipo de fonte de energia'] = df['Tipo de fonte de energia'].fillna(df['Combustível'])
    df['Material'] = df['Material'].fillna(df['Tipo de material'])
    df['Material'] = df['Material'].fillna(df['Composição do material'])
    df['Material'] = df['Material'].fillna(df['Material da alça ou do cabo'])
    df['Tipo de controles'] = df['Tipo de controles'].fillna(df['Painel de controle'])
    df['Tipo de controles'] = df['Tipo de controles'].fillna(df['Entrada de usuário'])
    df['Tipo de instalação'] = df['Tipo de instalação'].fillna(df['Forma de instalação'])
    df['Certificação'] = df['Certificação'].fillna(df['Registro no Inmetro'])
    df['Garantia do fabricante'] = df['Garantia do fabricante'].fillna(df['Descrição da garantia'])
    df['Número da Peça'] = df['Número da Peça'].fillna(df['Número do modelo'])
    df['Informações do modelo'] = (df['Informações do modelo'].fillna(df['Número da Peça'])).str.lower()
    to_delete = ['Ranking dos mais vendidos','Tipo de Cabelo','Tipo de suporte ou fixação',
                'Desenho ou estampa','Marca','Baterias inclusas','Baterias inclusas?',
                'Departamento','Funciona a bateria ou pilha?','Funciona com baterias',
                'Precisa de pilhas ou baterias?','Voltagem','Velocidade máxima de centrifugação',
                'Número de peças', 'Número de produtos', 'Número de unidades',
                'Potência em watts', 'Etiqueta Nacional de Eficiência Energética (ENCE)','Combustível',
                'Tipo de material', 'Composição do material', 'Material da alça ou do cabo',
                'Quantidade','Quantidade por pacote', 'Painel de controle',
                'Entrada de usuário','Nome do produto','Unidades',
                'Fator de forma','Dispositivos compatíveis', 'Ano',
                'Formato','Dobradiças da porta','Tipo de acabamento',
                'Correspondência de tamanho','Forma de instalação', 'Contém líquido?',
                'É necessária montagem','Acabamento','Nível de ruído',
                'Altura do cano', 'Tipo de instalação', 'Tipo de queimadores',
                'Peças para montagem','Modelo','Nome do modelo',
                'Estilo', 'Instruções de cuidado','Descrição da garantia',
                'Configuração básica', 'Registro no Inmetro']
    df = df.drop(to_delete,axis=1)
    # Specify which columns are not going to be translated
    col_ignore = ['Link', 'Price', 'Nome da marca', 'Informações do modelo', 'Número da Peça','Fabricante','Avaliações de clientes','Review Count','Image Link' ]
    # This function adds GOOGLETRANSLATE({x},'auto') in the objects
    def apply_googletranslate(x):
        if pd.isna(x):
            return ''  # If nan shouldn't be translated
        if isinstance(x, (int, float)):
            return x  # If numeric, shouldn't be translated
        return f'=GOOGLETRANSLATE("{x}", "auto")'

    # we will not change the original document
    df_translated = df.copy()

    for col in df.columns:
        if col not in col_ignore:#ignore those we don't want to trnaslate
            df_translated[col] = df[col].apply(apply_googletranslate)

    translated_columns = [apply_googletranslate(col) for col in df.columns]
    df_translated.columns = translated_columns

    # Exibir o DataFrame modificado
    print("DataFrame translated:")
    print(df_translated)

    return df_translated
    # Exportar o DataFrame para um arquivo CSV
    #df_translated.to_csv('final_product_data.csv', index=False, encoding='utf-8')



def cleanup_USA(df:pd.DataFrame):
    df['Customer Reviews'] = df['Customer Reviews'].str.replace(' out of 5 stars', '', regex=False)
    df['Review Count'] = df['Review Count'].str.replace(' ratings', '', regex=False)
    df['Price'] = df['Price'].str.replace(',','',regex=False)
    df['Review Count'] = df['Review Count'].str.replace(',','',regex=False)
    to_delete = ['Best Sellers Rank']
    df = df.drop(to_delete,axis=1)
    return df
    #df.to_csv("final_product_data.csv")


