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

    registro = {
        "DataHora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Alimento": alimento,
        "Quantidade (g/ml)": quantidade,
        "Calorias": calorias,
        "Carboidratos": carboidratos,
        "Açúcar": acucar
    }

    salvar_registro_csv(registro)
    st.success("Alimento registrado com sucesso!")

# ========================
# Exibir Registros do Dia a partir do CSV
# ========================
st.subheader("📋 Registro do Dia")

df_historico = carregar_registros_csv()
if not df_historico.empty:
    df_historico["DataHora"] = pd.to_datetime(df_historico["DataHora"])
    hoje = datetime.now().date()
    df_dia = df_historico[df_historico["DataHora"].dt.date == hoje]

    if not df_dia.empty:
        st.dataframe(df_dia, use_container_width=True)

        st.subheader("🔢 Totais do Dia")
        total = df_dia[["Calorias", "Carboidratos", "Açúcar"]].sum()
        st.write(f"**Total de Calorias:** {total['Calorias']} kcal")
        st.write(f"**Total de Carboidratos:** {total['Carboidratos']} g")
        st.write(f"**Total de Açúcar:** {total['Açúcar']} g")

        # 🎯 Meta Diária
        st.subheader("🎯 Meta Diária")

        meta_diaria = {
            "Calorias": 2000,
            "Carboidratos": 300,
            "Açúcar": 30,
        }

        consumo = {
            "Calorias": total.get("Calorias", 0),
            "Carboidratos": total.get("Carboidratos", 0),
            "Açúcar": total.get("Açúcar", 0),
        }

        saldo = {k: round(meta_diaria[k] - consumo[k], 2) for k in meta_diaria}

        df_meta = pd.DataFrame({
            "Meta Diária": meta_diaria,
            "Consumido": consumo,
            "Saldo": saldo
        })

        st.table(df_meta)
    else:
        st.info("Nenhum alimento registrado hoje ainda.")
else:
    st.info("Nenhum alimento registrado ainda.")

# ========================
# Exibir Histórico Completo + Resumo Mensal
# ========================
st.markdown("---")
st.subheader("📚 Histórico Completo")

if not df_historico.empty:
    st.dataframe(df_historico.sort_values(by="DataHora", ascending=False), use_container_width=True)

    df_historico["Mês"] = df_historico["DataHora"].dt.to_period("M")
    resumo_mensal = df_historico.groupby("Mês")[["Calorias", "Carboidratos", "Açúcar"]].sum()
    st.subheader("📈 Resumo Mensal")
    st.write(resumo_mensal)
else:
    st.info("Ainda não há registros salvos no histórico.")
