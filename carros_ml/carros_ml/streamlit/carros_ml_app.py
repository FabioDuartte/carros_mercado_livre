import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import pymysql
import mysql.connector

# Definindo o tamanho da página
from matplotlib import gridspec

st.set_page_config(layout='wide')

def conectar_banco_dados(host, usuario, senha, banco_dados):

    conn = None

    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(
            host=host,
            user=usuario,
            password=senha,
            database=banco_dados
        )

        # Retornar a conexão estabelecida
        return conn

    except mysql.connector.Error as erro:
        # Lidar com erros de conexão
        print(f"Erro ao conectar ao banco de dados: {erro}")
        return conn


def data_overview (conn):
    st.title('Data Overview')
    query = """
        SELECT carros.id AS carros_id, marca, modelo, ano, cor, tipo_de_combustivel, motor,
            tipo_de_transmissao, quilometros, portas, price, carros_info.id, com_ipva_pago,
            aceita_troca, entrega_a_domicilio, unico_dono, com_preco_negociavel,
            hgienizacao_completa, nao_aceita_troca, com_garantia_mecanica, test_drive_a_domicilio
        FROM carros
        JOIN carros_info ON carros.id = carros_info.id
    """
    df = pd.read_sql_query(query, conn)
    st.write(df)

def analise_descritiva(conn):
    query = """
        SELECT marca, modelo, COUNT(*) quantidade, AVG(price) media_de_preco FROM carros GROUP BY(marca) ORDER BY(quantidade) DESC 

    """
    analise_descritiva = pd.read_sql_query(query, conn)
    # analise_descritiva

    # Definição do número de colunas que as tabelas ocuparão
    c1, c2 = st.columns((1, 1))

   ########################### ESTATÍSTOCA DESCRITIVA ############################

    ########################### MÉDIA ###################

    query_media = """
      SELECT 
        FLOOR(AVG(ano)) as media_ANO,
        MAX(ano) as max_ANO,
        MIN(ano) as min_ANO,
        (
            SELECT AVG(ano)
            FROM (
                SELECT ano
                FROM (
                    SELECT @rownum:=@rownum+1 AS rownum, ano
                    FROM carros, (SELECT @rownum:=0) r
                    ORDER BY ano
                ) ranked
                WHERE rownum IN (FLOOR((@rownum+1)/2), FLOOR((@rownum+2)/2))
            ) mediana_ANO
        ) as mediana_ANO,    
        STDDEV(ano) as std_ANO,
        
        ########################################################################
        
        AVG(motor) as media_MOTOR,
        MAX(motor) as max_MOTOR,
        MIN(motor) as min_MOTOR,
        (
            SELECT AVG(motor)
            FROM (
                SELECT motor
                FROM (
                    SELECT @rownum_motor:=@rownum_motor+1 AS rownum_motor, motor
                    FROM carros, (SELECT @rownum_motor:=0) r
                    ORDER BY motor
                ) ranked_motor
                WHERE rownum_motor IN (FLOOR((@rownum_motor+1)/2), FLOOR((@rownum_motor+2)/2))
            ) mediana_MOTOR
        ) as mediana_MOTOR,
        STDDEV(motor) as std_MOTOR,
        
        #######################################################################
        
        AVG(portas) as media_PORTAS,
        MAX(portas) as max_PORTAS,
        MIN(portas) as min_PORTAS,
        (
            SELECT AVG(portas)
            FROM (
                SELECT portas
                FROM (
                    SELECT @rownum_portas:=@rownum_portas+1 AS rownum_portas, portas
                    FROM carros, (SELECT @rownum_portas:=0) r
                    ORDER BY portas
                ) ranked_portas
                WHERE rownum_portas IN (FLOOR((@rownum_portas+1)/2), FLOOR((@rownum_portas+2)/2))
            ) mediana_PORTAS
        ) as mediana_PORTAS,
        STDDEV(portas) as std_PORTAS,
        
        ########################################################################
        
        AVG(quilometros) as media_KM,
        MAX(quilometros) as max_KM,
        MIN(quilometros) as min_KM,
        (
            SELECT AVG(quilometros)
            FROM (
                SELECT quilometros
                FROM (
                    SELECT @rownum_portas:=@rownum_quilometros+1 AS rownum_quilometros, quilometros
                    FROM carros, (SELECT @rownum_quilometros:=0) r
                    ORDER BY quilometros
                ) ranked_quilometros
                WHERE rownum_quilometros IN (FLOOR((@rownum_quilometros+1)/2), FLOOR((@rownum_quilometros+2)/2))
            ) mediana_KM
        ) as mediana_KM,
        STDDEV(quilometros) as std_KM,
        
        #########################################################################
        AVG(price) as media_PRICE,
        MAX(price) as max_PRICE,
        MIN(price) as min_PRICE,
        (
            SELECT AVG(price)
            FROM (
                SELECT price
                FROM (
                    SELECT @rownum_price:=@rownum_price+1 AS rownum_price, price
                    FROM carros, (SELECT @rownum_price:=0) r
                    ORDER BY price
                ) ranked_price
                WHERE rownum_price IN (FLOOR((@rownum_price+1)/2), FLOOR((@rownum_price+2)/2))
            ) mediana_PRICE
        ) as mediana_PRICE,
        STDDEV(price) as std_PRICE
    FROM carros;
    """
    ad_query_estatistica = pd.read_sql_query(query_media, conn)
    ad_query_estatistica = ad_query_estatistica.melt()

    # Imprimindo
    c1.header('Analise Descritiva')
    c1.dataframe(analise_descritiva, width=600, height=600)

    c2.header('Estatística Descritiva')
    c2.dataframe(ad_query_estatistica, width=600, height=600)

def data_plot(conn):
    st.sidebar.title('Opções de atributos')
    st.title("Atributos das casas")

    query = """SELECT tipo_de_transmissao,
               COUNT(tipo_de_transmissao) quantidade
               FROM carros
               GROUP BY(tipo_de_transmissao)
               ORDER BY(quantidade) DESC
            """
    tipo_transmissao = pd.read_sql_query(query, conn)
    # tipo_transmissao
    # st.sidebar.multiselect('Escolha qual coluna deseja filtrar', tipo_transmissao)

    fig = plt.figure(figsize=(10, 4))

    ax = sns.barplot(data=tipo_transmissao, x='tipo_de_transmissao', y='quantidade')
    ax.set(title='Tipos de transmissão dos automóveis', xlabel='Tipo de transmissão', ylabel='Quantidade')

    for i in ax.containers:
        ax.bar_label(i)

    st.pyplot(fig)


def graph(conn):
    st.sidebar.title('Opções de atributos')
    st.title("Atributos das casas")

    # Consulta para obter tipos de transmissão distintos
    query_filter = "SELECT DISTINCT tipo_de_transmissao FROM carros;"
    tipo_transmissao = pd.read_sql_query(query_filter, conn)

    # Consulta para obter contagem de tipos de transmissão
    query_graph = "SELECT 'manual' AS tipo_de_transmissao, COUNT(*) AS quantidade FROM carros WHERE tipo_de_transmissao = 'manual'"
    tipo_transmissao_graph = pd.read_sql_query(query_graph, conn)

    # Filtros de tipo de transmissão
    f_tipo_transmissao = st.sidebar.selectbox("Tipo de transmissão", tipo_transmissao["tipo_de_transmissao"])

    # Gráfico de tipos de transmissão
    with st.expander("Tipos de transmissão"):
        if len(f_tipo_transmissao) > 0:
            if f_tipo_transmissao == 'manual':
                fig, ax = plt.subplots(figsize=(10, 4))
                ax = sns.barplot(data=tipo_transmissao_graph, x='tipo_de_transmissao', y='quantidade')
                ax.set(title='Tipos de transmissão dos automóveis', xlabel='Tipo de transmissão', ylabel='Quantidade')

                for i in ax.containers:
                    ax.bar_label(i)

                st.pyplot(fig)
            else:
                st.warning("Não há automóveis que atendam aos critérios de filtro selecionados.")
        else:
            st.warning("Não há atutomóveis que atendam aos critérios de filtro selecionados.")

def check_box(conn):
    st.sidebar.title('Preços')
    st.title('Variação de preço em R$')
    st.write('Utilize as checkbox na barra lateral para exibir os preços')



    ########################### CHECK BOX 1 R$89.000-R$120.000 ############################
    check_89_120 = st.sidebar.checkbox("89.000-120.000")
    # Preços entre 89000 e 120000
    query = """
        SELECT marca, modelo, cor, ano, COUNT(marca) AS quantidade, portas, price
        FROM carros
        WHERE price >= 89000 AND price <= 120000
        GROUP BY(marca)
        ORDER BY(price) DESC
    """
    check_1 = pd.read_sql_query(query, conn)
    # check_1

    with st.expander("Variação 89.000 - 120.000"):
        if check_89_120:
            check_1
        else:
            st.warning("Não há automóveis que atendam aos critérios de filtro selecionados.")

    ########################### CHECK BOX 2 R$120.000-R$200.000 ############################

    check_120_200 = st.sidebar.checkbox("120.000-200.000")
    # Preços entre 120000 e 200000
    query = """
            SELECT marca, modelo, cor, ano, COUNT(marca) AS quantidade, portas, price
            FROM carros
            WHERE price > 120000 AND price <= 200000
            GROUP BY(marca)
            ORDER BY(price) DESC
        """
    check_2 = pd.read_sql_query(query, conn)
    # check_1

    with st.expander("Variação 120.000 - 200.000"):
        if check_120_200:
            check_2
        else:
            st.warning("Não há automóveis que atendam aos critérios de filtro selecionados.")

    ########################### CHECK BOX 2 MAIOR QUE R$200.000 ############################

    check_200_400 = st.sidebar.checkbox("200.000 - 400000")
    # Preços entre 120000 e 200000
    query = """
            SELECT marca, modelo, cor, ano,
            COUNT(marca) AS quantidade, portas, price
            FROM carros
            WHERE price > 200000 AND price <= 400000
            GROUP BY(marca)
            ORDER BY(price) DESC
        """
    check_3 = pd.read_sql_query(query, conn)
    # check_1

    with st.expander("Variação 200.000 - 400.000"):
        if check_200_400:
            check_3
        else:
            st.warning("Não há automóveis que atendam aos critérios de filtro selecionados.")

def car_per_brand(conn):
    st.title("Quantidade de carros por marca e cor")

    col1, col2 = st.columns(2)

    with col1:
        query = """
            SELECT marca, cor, COUNT(modelo) quantidade FROM carros GROUP BY(marca) ORDER BY(modelo) DESC
        """

        # Executar a query e obter os dados do banco de dados
        marcas_por_modelo = pd.read_sql_query(query, conn)

        # Configurar o gráfico de barras
        fig, ax = plt.subplots(figsize=(8,6))
        ax = sns.barplot(data=marcas_por_modelo, x='marca', y='quantidade')
        ax.set(title='', xlabel='Marcas', ylabel='Quantidade')

        # Rotacionar os rótulos do eixo x
        plt.xticks(rotation=90)

        # Adicionar rótulos às barras
        for container in ax.containers:
            ax.bar_label(container)

        # Exibir o gráfico no Streamlit
        st.pyplot(fig)

    with col2:

        query_marca_cor = """
            SELECT marca, cor, COUNT(modelo) quantidade FROM carros GROUP BY(marca) ORDER BY(modelo) DESC

        """
        marcas_por_cor = pd.read_sql_query(query_marca_cor, conn)
        marcas_por_cor

def preco_ano(conn):
    st.title('Análise de variação dos preços dos automóveis ao longo dos anos')

    # Definir a figura e as especificações da grade
    fig = plt.figure(figsize=(20, 12))
    specs = gridspec.GridSpec(ncols=2, nrows=3, figure=fig)

    # Gráfico 1: Preço médio dos automóveis ao longo dos anos
    ax1 = fig.add_subplot(specs[1, 0])

    query_avg_ano = "SELECT ano, AVG(price) avg_por_ano FROM carros GROUP BY(ano) ORDER BY(avg_por_ano) DESC"
    avg_ano = pd.read_sql_query(query_avg_ano, conn)
    avg_ano_rounded = avg_ano.round(2)

    sns.lineplot(data=avg_ano_rounded, x='ano', y='avg_por_ano', ax=ax1)
    ax1.set(title='Preço médio dos automóveis ao longo dos anos', xlabel='Ano', ylabel='Preço Médio')


    # Exibir a figura no Streamlit
    st.pyplot(fig)

def tipo_transmissao(conn):
    st.title('Tipos de transmissão dos automóveis')

    fig = plt.figure(figsize=(20, 12))
    specs = gridspec.GridSpec(ncols=2, nrows=3, figure=fig)

    # Gráfico 2: Tipos de transmissão
    ax1 = fig.add_subplot(specs[1, 0])

    query_transmissao = """
            SELECT tipo_de_transmissao,
               COUNT(tipo_de_transmissao) quantidade
               FROM carros
               GROUP BY(tipo_de_transmissao)
               ORDER BY(quantidade) DESC
        """
    tipo_transmissao = pd.read_sql_query(query_transmissao, conn)

    sns.barplot(data=tipo_transmissao, x='tipo_de_transmissao', y='quantidade', ax=ax1)
    ax1.set(title='', xlabel='Tipo de Transmissão', ylabel='Quantidade')

    for container in ax1.containers:
        ax1.bar_label(container)

    st.pyplot(fig)



if __name__ == "__main__":

    # conn = conectar_banco_dados("localhost", "root", " ", "carros_bd_ml")
    conn = conectar_banco_dados("localhost", "root", "", "carros_bd_ml")


    if conn is not None:
        print("Conexão estabelecida com sucesso!")
        data_overview(conn)
        analise_descritiva(conn)
        # data_plot(conn)
        # graph(conn)
        check_box(conn)
        car_per_brand(conn)
        preco_ano(conn)
        tipo_transmissao(conn)
    else:
        print("Falha ao conectar ao banco de dados.")


