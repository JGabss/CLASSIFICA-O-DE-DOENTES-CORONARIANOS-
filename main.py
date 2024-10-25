import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

def calcular_escore_cleveland(df):
  # Inicializa a coluna de escore com zeros
  df['escore'] = 0

  # Adiciona os pontos para cada critério
  # df['escore'] += df['emergencia'] * 6
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
  
  # Adiciona a coluna de classificação de risco 
  df[ 'risco' ] = 2 #Alto risco
  df.loc[df['escore'] <= 1, 'risco'] = 0 #Baixo risco
  df.loc[(df['escore'] >= 2) & (df['escore'] <= 4), 'risco'] = 1 #Risco intermediário
  #   print(df)
  return df

def definir_grupo(df):    
    df['escore'] = 0
    print(df['escore'])
    df['escore'] += df['angina_instavel'] * 3
    df['escore'] += df['lesao_tronco_coronaria'] * 2
    df['escore'] += df['valva_aortica'] * 2
    df.loc[df['risco'] == 0, 'escore'] += 1 # Risco baixo
    df.loc[df['risco'] == 1, 'escore'] += 1 # Risco intermediário
    df.loc[df['risco'] == 2, 'escore'] += 2 # Risco alto
    df['escore'] += np.where(
        df['fracao_ejecao_ventriculo'] < 35, 
        2, 
        np.where((df['fracao_ejecao_ventriculo'] >= 35) & (df['fracao_ejecao_ventriculo'] <= 49), 1, 0)
    )
    df['escore'] += ((df['sexo'] == 'Masculino')) * 1

    # Adiciona a coluna de grupo
    df['grupo'] = 1 # Grupo 1: cirurgia em até 30 dias
    df.loc[df['escore'] == 2, 'grupo'] = 3 # Grupo 2: cirurgia em até 90 dias
    df.loc[(df['escore'] >= 3) & (df['escore'] <= 5), 'grupo'] = 2 # cirurgias a programar eletivamente
    return df

# # Caminho do arquivo CSV
# dados_treinamento = './dados_treinamento.csv'

# # Carregando o CSV em um DataFrame
# df = pd.read_csv(dados_treinamento)

# df = calcular_escore_cleveland(df)

# # Transforma variáveis booleanas em inteiros
# def label_encoding(df):
#     for col in ['emergencia', 'reoperacao', 'insuficiencia_mitral', 'cirurgia_vascular_previa', 'dpoc', 'anemia', 'estenose_aortica', 'diabetes', 'doenca_cerebrovascular']:
#         df[col] = df[col].astype(int)
#     return df

# df = label_encoding(df)

# # Separação de features e labels
# X = df.drop('risco', axis=1)
# y = df['risco']

# # Divisão dos dados em treino e teste
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Treinamento do modelo com limitação na profundidade
# modelo = DecisionTreeClassifier(criterion='entropy')
# modelo.fit(X_train, y_train)

# # Previsão do conjunto de teste
# y_pred = modelo.predict(X_test)

# Avaliação do modelo
# print('Acurácia do modelo: ', accuracy_score(y_test, y_pred))
# print("Relatório de Classificação do modelo:\n", classification_report(y_test, y_pred, zero_division=0))

# # Exemplo de previsão para novos dados
# novos_dados = pd.DataFrame({
#     'emergencia': [False, True, False, True, False, True],
#     'creatinina_serica': [1.0, 2.1, 1.0, 1.8, 1.2, 2.0],
#     'fracao_ejecao': [60, 30, 45, 50, 65, 35],
#     'reoperacao': [False, True, False, True, False, True],
#     'insuficiencia_mitral': [False, True, False, True, False, True],
#     'idade': [50, 75, 61, 70, 60, 72],
#     'cirurgia_vascular_previa': [False, True, False, True, False, True],
#     'dpoc': [False, True, False, True, False, True],
#     'anemia': [False, True, False, True, False, True],
#     'estenose_aortica': [False, True, False, True, False, True],
#     'peso': [60, 60, 75, 68, 72, 64],
#     'diabetes': [True, True, False, True, True, True],
#     'doenca_cerebrovascular': [True, True, False, True, True, True]
# })

# novos_dados = calcular_escore_cleveland(novos_dados)
# novos_dados = novos_dados.drop('risco', axis=1)

# # Transforma variáveis booleanas em inteiros
# for col in ['emergencia', 'reoperacao', 'insuficiencia_mitral', 'cirurgia_vascular_previa', 'dpoc', 'anemia', 'estenose_aortica', 'diabetes', 'doenca_cerebrovascular']:
#     novos_dados[col] = novos_dados[col].astype(int)

# print(novos_dados)

# previsao = modelo.predict(novos_dados)
# accuracy = accuracy_score(y_test, previsao)
# print(f"Acurácia das previsões para novos dados: {accuracy:.2f}")
# print("Previsão de risco para novos dados:", previsao)

# Configuração da página com layout expandido
st.set_page_config(layout="wide")
# Título do formulário
st.markdown("<h1 style='text-align: center;'>CLASSIFICAÇÃO DE DOENTES CORONARIANOS EM FILA PARA CIRURGIA ELETIVA</h1>", unsafe_allow_html=True)

# Criação do formulário
with st.form(key='medical_data_form'):
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    #Criar duas colunas
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        # emergencia = st.checkbox("Emergência")
        creatinina_serica = st.number_input("Creatinina Sérica (mg/dL)", min_value=0.0, step=0.1)
        reoperacao = st.checkbox("Reoperação")
        insuficiencia_mitral = st.checkbox("Insuficiência Mitral")
        #fracao_ejecao = st.number_input("Fração de Ejeção (%)", min_value=0, max_value=100, step=1)
    with col2:
        idade = st.number_input("Idade", min_value=0, step=1)
        cirurgia_vascular_previa = st.checkbox("Cirurgia Vascular Prévia")
        dpoc = st.checkbox("DPOC (Doença Pulmonar Obstrutiva Crônica)")
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
        valva_aortica = st.checkbox("Doença da Valva Aórtica que Necessita Cirurgia")
        fracao_ejecao_ventriculo = st.number_input("Fração de Ejeção do Ventrículo (%)", min_value=0, max_value=100, step=1)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])


    # Botão de envio
    submit_button = st.form_submit_button(label='Enviar')

# Ação após envio
if submit_button:
    df_paciente = pd.DataFrame({
        # Esse conjunto de dados é para calcular o score cleveland e classificar o risco do paciente
        # 'emergencia': [emergencia],
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
        # Esse conjunto tem o objetivo de classificar em qual grupo o paciente faz parte
        'angina_instavel': [angina_instavel],
        'lesao_tronco_coronaria': [lesao_tronco_coronaria],
        'valva_aortica': [valva_aortica],
        'fracao_ejecao_ventriculo': [fracao_ejecao_ventriculo],
        'sexo': [sexo]
    })

    df_paciente = calcular_escore_cleveland(df_paciente)
    definir_grupo(df_paciente)
    

    # y_true_novos_dados = df_paciente['risco']
    # print(y_true_novos_dados)

    # df_paciente = df_paciente.drop('risco', axis=1)
    # df_paciente = label_encoding(df_paciente)
    # previsao = modelo.predict(df_paciente)

    # resultado = "Alto - Grupo 1: Cirurgia em até 30 dias"
    # if previsao == 0:
    #     resultado = "Baixo - Grupo 3: Cirurgia a programar eletivamente"
    # elif previsao == 1:
    #     resultado = "Intermediário - Grupo 2: Cirurgia em até 90 dias"
     
    # print(y_true_novos_dados)
    
    # st.success(f"Previsão de risco: {resultado}")
    # st.success(f"Acurácia: {accuracy_score(y_true_novos_dados, previsao)}")

    # st.write(f"Emergência: {emergencia}")
    st.write(f"Creatinina Sérica: {creatinina_serica} mg/dL")
    # st.write(f"Fração de Ejeção: {fracao_ejecao} %")
    st.write(f"Reoperação: {reoperacao}")
    st.write(f"Insuficiência Mitral: {insuficiencia_mitral}")
    st.write(f"Idade: {idade}")
    st.write(f"Cirurgia Vascular Prévia: {cirurgia_vascular_previa}")
    st.write(f"DPOC: {dpoc}")
    st.write(f"Anemia: {anemia}")
    st.write(f"Estenose Aórtica: {estenose_aortica}")
    st.write(f"Peso: {peso} kg")
    st.write(f"Diabetes: {diabetes}")
    st.write(f"Doença Cerebrovascular: {doenca_cerebrovascular}")
    st.write("Resultado Final:")
    st.write(df_paciente['grupo'])
    if df_paciente['grupo'].iloc[0] == 1:
        st.write("GRUPO 1: CIRURGIA EM ATÉ 30 DIAS ")
    if df_paciente['grupo'].iloc[0] == 2:
        st.write("GRUPO 2: CIRURGIA EM ATÉ 90 DIAS ")
    if df_paciente['grupo'].iloc[0] == 3:    
        st.write("GRUPO 3: CIRURGIAS A PROGRAMAR ELETIVAMENTE ")
    #accuracy = accuracy_score(y_test, previsao)




