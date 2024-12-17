import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import json

# Carregando as credenciais do arquivo secrets.toml
service_account_info = st.secrets["SERVICE_ACCOUNT_JSON"]

SCOPES = [service_account_info["SCOPES1"], service_account_info["SCOPES2"]]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# Autorize o cliente
client = gspread.authorize(creds)

# Acessando a planilha
spreadsheet = client.open("Telemonitoramento")  # Substitua pelo nome da sua planilha
worksheet = spreadsheet.sheet1

def salvar_paciente_google_sheets(dados_paciente):
    worksheet.append_row(dados_paciente.values.flatten().tolist())

# Ler todos os dados do Google Sheets
def ler_pacientes_google_sheets():
    dados = worksheet.get_all_records()
    return pd.DataFrame(dados)

def calcular_escore_cleveland(df):
    df['escore'] = 0
    df['escore'] += ((df['creatinina_serica'] >= 1.6) & (df['creatinina_serica'] <= 1.8)) * 1
    df['escore'] += (df['creatinina_serica'] >= 1.9) * 4
    df['escore'] += np.where(df['fracao_ejecao_ventriculo'] < 35, 3, 0)
    df['escore'] += df['reoperacao'] * 3
    df['escore'] += df['insuficiencia_mitral'] * 3
    df['escore'] += ((df['idade'] >= 65) & (df['idade'] <= 74)) * 1
    df['escore'] += (df['idade'] > 75) * 2
    df['escore'] += df['cirurgia_vascular_previa'] * 2
    df['escore'] += df['dpoc'] * 2
    df['escore'] += df['anemia'] * 2
    df['escore'] += df['estenose_aortica'] * 1
    df['escore'] += (df['peso'] <= 65) * 1
    df['escore'] += df['diabetes'] * 1
    df['escore'] += df['doenca_cerebrovascular'] * 1

    df['risco'] = 2
    df.loc[df['escore'] <= 1, 'risco'] = 0
    df.loc[(df['escore'] >= 2) & (df['escore'] <= 4), 'risco'] = 1
    return df

def definir_grupo(df):    
    df['escore'] = 0
    df['escore'] += df['angina_instavel'] * 3
    df['escore'] += df['lesao_tronco_coronaria'] * 2
    df['escore'] += df['valva_aortica'] * 2
    df.loc[df['risco'] == 0, 'escore'] += 1
    df.loc[df['risco'] == 1, 'escore'] += 1
    df.loc[df['risco'] == 2, 'escore'] += 2
    df['escore'] += np.where(
        df['fracao_ejecao_ventriculo'] < 35, 
        2, 
        np.where((df['fracao_ejecao_ventriculo'] >= 35) & (df['fracao_ejecao_ventriculo'] <= 49), 1, 0)
    )
    df['escore'] += ((df['sexo'] == 'Masculino')) * 1

    df['grupo'] = 1
    df.loc[df['escore'] == 2, 'grupo'] = 3
    df.loc[(df['escore'] >= 3) & (df['escore'] <= 5), 'grupo'] = 2
    return df

# Configuração da página
st.set_page_config(layout="wide")

# Título do formulário
st.markdown("<h1 style='text-align: center;'>CLASSIFICAÇÃO DE DOENTES CORONARIANOS EM FILA PARA CIRURGIA ELETIVA</h1>", unsafe_allow_html=True)

# Criação do formulário
with st.form(key='medical_data_form'):
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        nome = st.text_input("Nome do Paciente")
        ba = st.text_input("BA")
        creatinina_serica = st.number_input("Creatinina Sérica (mg/dL)", min_value=0.0, step=0.1)
        reoperacao = st.checkbox("Reoperação")
        insuficiencia_mitral = st.checkbox("Insuficiência Mitral")
        
    with col2:
        idade = st.number_input("Idade", min_value=0, step=1)
        cirurgia_vascular_previa = st.checkbox("Cirurgia Vascular Prévia")
        dpoc = st.checkbox("DPOC")
        
    with col3:
        anemia = st.checkbox("Anemia")
        estenose_aortica = st.checkbox("Estenose Aórtica")
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        
    with col4:
        diabetes = st.checkbox("Diabetes")
        doenca_cerebrovascular = st.checkbox("Doença Cerebrovascular")
        angina_instavel = st.checkbox("Angina Instável")
        lesao_tronco_coronaria = st.checkbox("Lesão de Tronco de Coronária Esquerda")
        
    with col5:
        valva_aortica = st.checkbox("Doença da Valva Aórtica")
        fracao_ejecao_ventriculo = st.number_input("Fração de Ejeção (%)", min_value=0, max_value=100, step=1)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])

    submit_button = st.form_submit_button(label='Enviar')

# Ação após envio
if submit_button:
    df_paciente = pd.DataFrame({
        'Nome': [nome],
        'BA': [ba],
        'creatinina_serica': [creatinina_serica],
        'reoperacao': [reoperacao],
        'insuficiencia_mitral': [insuficiencia_mitral],
        'idade': [idade],
        'cirurgia_vascular_previa': [cirurgia_vascular_previa],
        'dpoc': [dpoc],
        'anemia': [anemia],
        'estenose_aortica': [estenose_aortica],
        'peso': [peso],
        'diabetes': [diabetes],
        'doenca_cerebrovascular': [doenca_cerebrovascular],
        'angina_instavel': [angina_instavel],
        'lesao_tronco_coronaria': [lesao_tronco_coronaria],
        'valva_aortica': [valva_aortica],
        'fracao_ejecao_ventriculo': [fracao_ejecao_ventriculo],
        'sexo': [sexo]
    })

    df_paciente = calcular_escore_cleveland(df_paciente)
    definir_grupo(df_paciente)

    # Salvando os dados no CSV
    salvar_paciente_google_sheets(df_paciente)

    st.write("Dados salvos com sucesso!")
    st.write(df_paciente)
    if df_paciente['grupo'].iloc[0] == 1:
        st.write("GRUPO 1: CIRURGIA EM ATÉ 30 DIAS")
    elif df_paciente['grupo'].iloc[0] == 2:
        st.write("GRUPO 2: CIRURGIA EM ATÉ 90 DIAS")
    else:
        st.write("GRUPO 3: CIRURGIAS A PROGRAMAR ELETIVAMENTE")

# Nova seção para visualizar pacientes
st.markdown("## Visualizar Pacientes Salvos")

# Botão para exibir pacientes
if st.button("Exibir Todos os Pacientes"):
    # Ler os dados do CSV e especificar os tipos de dados
    colunas = [
            'Nome', 'BA', 'creatinina_serica', 'reoperacao', 'insuficiencia_mitral', 
            'idade', 'cirurgia_vascular_previa', 'dpoc', 'anemia', 'estenose_aortica', 
            'peso', 'diabetes', 'doenca_cerebrovascular', 'angina_instavel', 
            'lesao_tronco_coronaria', 'valva_aortica', 'fracao_ejecao_ventriculo', 'sexo', "escore", "risco", "grupo"
        ]
    df_pacientes = ler_pacientes_google_sheets()

        # Converter os tipos de dados
    df_pacientes['idade'] = pd.to_numeric(df_pacientes['idade'], errors='coerce')
    df_pacientes['creatinina_serica'] = pd.to_numeric(df_pacientes['creatinina_serica'], errors='coerce')
    df_pacientes['peso'] = pd.to_numeric(df_pacientes['peso'], errors='coerce')
    df_pacientes['fracao_ejecao_ventriculo'] = pd.to_numeric(df_pacientes['fracao_ejecao_ventriculo'], errors='coerce')

        # Ordenar os pacientes por uma coluna, como 'Nome' ou 'idade'
    coluna_ordenacao = st.selectbox("Ordenar por", options=colunas, index=0)
    df_pacientes = df_pacientes.sort_values(by=coluna_ordenacao, ascending=True)

        # Exibir os dados na interface
    st.write("### Pacientes Ordenados por:", coluna_ordenacao)
    st.dataframe(df_pacientes)


