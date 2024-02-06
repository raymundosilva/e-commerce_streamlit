import streamlit as st
import plotly.express as px 
import pandas as pd
import os
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

st.set_page_config(page_title="Rai - Análise!!", page_icon=":chart:",layout="wide")
st.sidebar.image('image.png')

st.title(" :chart: ANÁLISE DE VENDAS E-COMMERCE")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Carregar um arquivo",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df_original = pd.read_csv(filename, encoding = "utf-8", sep = ",", decimal = ",", thousands = ".")
    
else:
    os.chdir(r"C:\Users\mardo\anaconda3\envs\streamlitenv")
    df_original = pd.read_csv("dataset.csv", encoding = "utf-8", sep = ",", decimal = ",", thousands = ".")

df = df_original[['ID_Linha', 'ID_Pedido', 'Data_Pedido', 'Data_Envio', 'Modo_Envio', 'ID_Cliente', 'Nome_Cliente',
                  'Segmento', 'Pais', 'Cidade', 'Estado', 'Cep', 'Regiao', 'ID_Produto', 'Categoria', 'SubCategoria', 
                  'Nome_Produto', 'Preco', 'Quantidade', 'Desconto', 'Lucro']]
col1, col2 = st.columns((2))

df["Data_Pedido"] = pd.to_datetime(df["Data_Pedido"], format= '%d/%m/%Y', dayfirst = True)

# Obtendo a data minima e maxima 
startDate = pd.to_datetime(df["Data_Pedido"]).min()

endDate = pd.to_datetime(df["Data_Pedido"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Data Início", startDate, format = "DD/MM/YYYY"))
with col2:
    date2 = pd.to_datetime(st.date_input("Data Fim", endDate, format = "DD/MM/YYYY"))
df = df[(df["Data_Pedido"] >= date1) & (df["Data_Pedido"] <= date2)].copy()

st.sidebar.header("Escolha seu filtro: ")
# Filtrando por  Região
region = st.sidebar.multiselect("Selecione sua Região", df["Regiao"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Regiao"].isin(region)]

# Filtro por Estado
state = st.sidebar.multiselect("Escolha seu Estado", df2["Estado"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["Estado"].isin(state)]

# Filtro por  Cidade
city = st.sidebar.multiselect("Escolha sua Cidade",df3["Cidade"].unique())

# Filtra os dados baseados na Região, Estado e Cidade

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Regiao"].isin(region)]
elif not region and not city:
    filtered_df = df[df["Estado"].isin(state)]
elif state and city:
    filtered_df = df3[df["Estado"].isin(state) & df3["Cidade"].isin(city)]
elif region and city:
    filtered_df = df3[df["Regiao"].isin(region) & df3["Cidade"].isin(city)]
elif region and state:
    filtered_df = df3[df["Regiao"].isin(region) & df3["Estado"].isin(state)]
elif city:
    filtered_df = df3[df3["Cidade"].isin(city)]
else:
    filtered_df = df3[df3["Regiao"].isin(region) & df3["Estado"].isin(state) & df3["Cidade"].isin(city)]

category_df = filtered_df.groupby(by = ["Categoria"], as_index = False)["Preco"].sum()

def replace_special_chars(s):
    s = s.replace('á', 'a')
    s = s.replace('é', 'e')
    s = s.replace('í', 'i')
    s = s.replace('ó', 'o')
    s = s.replace('ú', 'u')
    s = s.replace('ç', 'c')
    # Adicione mais substituições conforme necessário
    return s

# Aplicar a função a todas as strings em seu DataFrame
category_df["Categoria"] = category_df["Categoria"].apply(replace_special_chars)

def format_brl(value):
    return locale.format_string('R$%.2f', value, True)


with col1:
    st.subheader("Vendas por categoria")      
    category_df["Preco"] = pd.to_numeric(category_df["Preco"])

    fig = px.bar(category_df, x="Categoria", y="Preco", 
             text=[format_brl(x) for x in category_df["Preco"]],
             template = "seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)
    
with col2:
    st.subheader("Vendas por região")
    fig = px.pie(filtered_df, values = "Preco", names = "Regiao", hole = 0.5)
    fig.update_traces(text = filtered_df["Regiao"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Dados de exibição de categoria"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Baixar dados", data = csv, file_name = "Categoria.csv", mime = "text/csv",
                            help = 'Clique aqui para baixar os dados como um arquivo CSV')

with cl2:
    with st.expander("Dados de exibição de Região"):
        region = filtered_df.groupby(by = "Regiao", as_index = False)["Preco"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Baixar dados", data = csv, file_name = "Regiao.csv", mime = "text/csv",
                        help = 'Clique aqui para baixar os dados como um arquivo CSV')
        
filtered_df["mes_ano"] = filtered_df["Data_Pedido"].dt.to_period("M")
st.subheader('Análise de séries temporais')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["mes_ano"].dt.strftime("%b : %Y"))["Preco"].sum()).reset_index()
fig2 = px.line(linechart, x = "mes_ano", y="Preco", labels = {"Preco": "Quantidade"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("Exibir dados de séries temporais:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Baixar dados', data = csv, file_name = "Series_temporais.csv", mime ='text/csv')

# Crie uma árvore com base na região, categoria, subcategoria
st.subheader("Visão hierárquica de Vendas usando TreeMap")
fig3 = px.treemap(filtered_df, path = ["Regiao","Categoria","SubCategoria"], values = "Preco",hover_data = ["Preco"],
                  color = "SubCategoria")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Vendas por segmento')
    fig = px.pie(filtered_df, values = "Preco", names = "Segmento", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segmento"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Vendas por categoria')
    fig = px.pie(filtered_df, values = "Preco", names = "Categoria", template = "gridon")
    fig.update_traces(text = filtered_df["Categoria"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff

# Alterando o nome da coluna "Regiao" para "Região" 
df.rename(columns={'Regiao': 'Região'}, inplace=True)

def formatar_coluna(df1, coluna):
    df1[coluna] = pd.to_numeric(df1[coluna])
    df1[coluna] = df1[coluna].apply(lambda x: '{:.2f}'.format(x).replace('.', ','))
    return df1

st.subheader(":point_right: Resumo de vendas da subcategoria mês a mês")
with st.expander("Quadro Resumo"):
    df_sample = df[0:6][["Região","Estado","Cidade","Categoria","Preco","Lucro","Quantidade"]]
    df_sample = formatar_coluna(df_sample, "Preco")
    df_sample = formatar_coluna(df_sample, "Lucro")
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Tabela de subcategorias mês a mês")
    filtered_df["month"] = filtered_df["Data_Pedido"].dt.month_name(locale="pt_BR.utf-8")
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Preco", index = ["SubCategoria"],columns = "month")
    
    # Ordenação dos meses
    months_order = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    sub_category_Year = sub_category_Year[months_order]
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# criando um scatter plot
data1 = px.scatter(filtered_df, x = "Preco", y = "Lucro", size = "Quantidade")
data1['layout'].update(title="Relação entre Vendas e Lucros usando Gráfico de Dispersão.",
                       titlefont = dict(size=20),xaxis = dict(title="Preço",titlefont=dict(size=19)),
                       yaxis = dict(title = "Lucro", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("Visualizar Dados"):
    filtered_df = formatar_coluna(filtered_df, 'Preco')
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download da base de dados
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Baixar dados', data = csv, file_name = "Base_Original.csv",mime = "text/csv")
