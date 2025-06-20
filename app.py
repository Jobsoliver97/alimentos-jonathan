import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ========================
# Carregamento da Tabela Nutricional
# ========================
@st.cache_data
def carregar_tabela_nutricional():
    return pd.read_csv("tabela_valores_nutricionais_com_acucar_lactose.csv")

df_nutri = carregar_tabela_nutricional()

ARQUIVO_REGISTROS = "registros_consumo.csv"

def salvar_registro_csv(registro):
    if not os.path.isfile(ARQUIVO_REGISTROS):
        df = pd.DataFrame([registro])
        df.to_csv(ARQUIVO_REGISTROS, index=False)
    else:
        df = pd.DataFrame([registro])
        df.to_csv(ARQUIVO_REGISTROS, mode='a', header=False, index=False)

def carregar_registros_csv():
    if os.path.isfile(ARQUIVO_REGISTROS):
        return pd.read_csv(ARQUIVO_REGISTROS)
    else:
        return pd.DataFrame()

# ========================
# Registro de Alimentos
# ========================
st.title("📊 Registro de Consumo Alimentar")

alimento = st.selectbox("Selecione o alimento consumido:", df_nutri["Alimento"].unique())
quantidade = st.number_input("Quantidade consumida (em gramas ou ml):", min_value=0.0, step=1.0)

if st.button("Registrar Consumo"):
    info = df_nutri[df_nutri["Alimento"] == alimento].iloc[0]
    fator = quantidade / 100

    calorias = round(info["Calorias (kcal)"] * fator, 2)
    carboidratos = round(info["Carboidratos (g)"] * fator, 2)
    acucar = round(info["Açúcar (g)"] * fator, 2)
    lactose = info["Lactose"]

    registro = {
        "DataHora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Alimento": alimento,
        "Quantidade (g/ml)": quantidade,
        "Calorias": calorias,
        "Carboidratos": carboidratos,
        "Açúcar": acucar,
        "Lactose": lactose
    }

    # Salvar no CSV
    salvar_registro_csv(registro)

    # Manter na sessão para mostrar logo abaixo
    if "registro" not in st.session_state:
        st.session_state["registro"] = []
    st.session_state["registro"].append(registro)

    st.success("Alimento registrado com sucesso!")
    if lactose == "Sim":
        st.warning("⚠️ Atenção: este alimento contém lactose.")

# ========================
# Exibir Registros do Dia (sessão)
# ========================
if "registro" in st.session_state and st.session_state["registro"]:
    df_registro = pd.DataFrame(st.session_state["registro"])
    st.subheader("📋 Registro do Dia")
    st.dataframe(df_registro, use_container_width=True)

    st.subheader("🔢 Totais do Dia")
    total = df_registro[["Calorias", "Carboidratos", "Açúcar"]].sum()
    st.write(f"**Total de Calorias:** {total['Calorias']} kcal")
    st.write(f"**Total de Carboidratos:** {total['Carboidratos']} g")
    st.write(f"**Total de Açúcar:** {total['Açúcar']} g")
else:
    st.info("Nenhum alimento registrado ainda.")

# ========================
# Exibir Histórico Completo + Resumo Mensal
# ========================
st.markdown("---")
st.subheader("📚 Histórico Completo")

df_historico = carregar_registros_csv()

if not df_historico.empty:
    # Converter DataHora para datetime
    df_historico["DataHora"] = pd.to_datetime(df_historico["DataHora"])
    st.dataframe(df_historico.sort_values(by="DataHora", ascending=False), use_container_width=True)

    # Resumo mensal
    df_historico["Mês"] = df_historico["DataHora"].dt.to_period("M")
    resumo_mensal = df_historico.groupby("Mês")[["Calorias", "Carboidratos", "Açúcar"]].sum()
    st.subheader("📈 Resumo Mensal")
    st.write(resumo_mensal)
else:
    st.info("Ainda não há registros salvos no histórico.")
