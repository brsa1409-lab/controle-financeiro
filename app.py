from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Controle Financeiro Pessoal", page_icon="💰", layout="wide"
)

ARQUIVO_DADOS = "gastos.csv"


def carregar_dados():
  if os.path.exists(ARQUIVO_DADOS):
    df = pd.read_csv(ARQUIVO_DADOS)
    return df
  else:
    return pd.DataFrame(
        columns=["Data", "Tipo", "Categoria", "Valor", "Descrição"]
    )


def salvar_dados(df):
  df.to_csv(ARQUIVO_DADOS, index=False)


df_gastos = carregar_dados()

# --- SAUDAÇÃO DINÂMICA ---
hora_atual = datetime.now().hour
if hora_atual < 12:
  saudacao = "Bom dia"
  emoji_saudacao = "☕"
elif 12 <= hora_atual < 18:
  saudacao = "Boa tarde"
  emoji_saudacao = "☀️"
else:
  saudacao = "Boa noite"
  emoji_saudacao = "🌙"

# --- TÍTULO PRINCIPAL COM SAUDAÇÃO ---
st.title(f"{emoji_saudacao} {saudacao}, Brenda Azevedo!")
st.markdown(
    "Acompanhamento de despesas mensal."
)
st.markdown("---")

# --- SEÇÃO DE CARDS DE RESUMO ---
if not df_gastos.empty and "Tipo" in df_gastos.columns:
  total_despesas = df_gastos[df_gastos["Tipo"] == "Despesa"]["Valor"].sum()
  total_receitas = df_gastos[df_gastos["Tipo"] == "Receita"]["Valor"].sum()
else:
  total_despesas = 0.0
  total_receitas = 0.0

saldo_atual = total_receitas - total_despesas

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
  st.metric(label="Receita Mensal", value=f"R$ {total_receitas:,.2f}")
with col_m2:
  st.metric(label="Despesa Total Acumulada", value=f"R$ {total_despesas:,.2f}")
with col_m3:
  st.metric(label="Saldo Atual", value=f"R$ {saldo_atual:,.2f}")

st.markdown("")

# --- ABAS DE NAVEGAÇÃO ---
aba_visao, aba_novo, aba_historico = st.tabs(
    ["📊 Visão Geral & Gráficos", "➕ Novo Lançamento", "📋 Histórico Completo"]
)

# ==========================================
# ABA 1: VISÃO GERAL & GRÁFICOS
# ==========================================
with aba_visao:
  therapeutic_data = (
      df_gastos[df_gastos["Tipo"] == "Despesa"]
      if not df_gastos.empty and "Tipo" in df_gastos.columns
      else df_gastos
  )

  st.subheader("Resumo de Despesas por Categoria")

  if therapeutic_data.empty or therapeutic_data["Valor"].sum() == 0:
    st.info("Ainda não há despesas cadastradas para exibir no gráfico.")
  else:
    fig_pizza = px.pie(
        therapeutic_data,
        names="Categoria",
        values="Valor",
    )
    fig_pizza.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_pizza, use_container_width=True)

# ==========================================
# ABA 2: NOVO LANÇAMENTO
# ==========================================
with aba_novo:
  st.subheader("Adicionar Novo Lançamento")

  with st.form("form_cadastro", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
      tipo_lancamento = st.selectbox(
          "Tipo de Lançamento", ["Despesa", "Receita"]
      )
      data_gasto = st.date_input("Data do Lançamento")
      st.caption("Calendário interativo (o registro será salvo como DD/MM/AAAA)")

      categoria = st.selectbox(
          "Categoria",
          [
              "Alimentação",
              "Transporte",
              "Moradia",
              "Lazer",
              "Cartão de Crédito",
              "Saúde",
              "Educação",
              "Energia / Contas",
              "Salário / Rendimento",
              "Outros",
          ],
      )

    with col2:
      valor = st.number_input(
          "Valor (R$)", min_value=0.01, format="%.2f", step=10.0
      )
      descricao = st.text_input(
          "Descrição (Ex: Supermercado, Salário, Farmácia...)"
      )

    submitted = st.form_submit_button("Salvar Lançamento")

    if submitted:
      data_formatada = data_gasto.strftime("%d/%m/%Y")

      novo_registro = pd.DataFrame([{
          "Data": data_formatada,
          "Tipo": tipo_lancamento,
          "Categoria": categoria,
          "Valor": valor,
          "Descrição": descricao if descricao else "Sem descrição",
      }])

      df_gastos = pd.concat([df_gastos, novo_registro], ignore_index=True)
      salvar_dados(df_gastos)

      st.success("Lançamento salvo com sucesso!")
      st.rerun()

# ==========================================
# ABA 3: HISTÓRICO COMPLETO
# ==========================================
with aba_historico:
  st.subheader("Histórico de Lançamentos")

  if df_gastos.empty:
    st.info("Nenhum registro encontrado.")
  else:
    filtro_tipo = st.selectbox(
        "Filtrar por Tipo", ["Todos", "Despesa", "Receita"]
    )

    df_exibicao = df_gastos.copy()
    if filtro_tipo != "Todos":
      df_exibicao = df_exibicao[df_exibicao["Tipo"] == filtro_tipo]


    # Função de estilo com cores fortes e fundo sutil para destacar bem
    def colorir_tipo(val):
      if val == "Despesa":
        return "background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b; font-weight: bold;"
      elif val == "Receita":
        return "background-color: rgba(46, 125, 50, 0.1); color: #2e7d32; font-weight: bold;"
      return ""


    st.dataframe(
        df_exibicao.style.map(
            colorir_tipo, subset=["Tipo"]
            if "Tipo" in df_exibicao.columns
            else []
        ),
        use_container_width=True,
    )

    if st.button("Limpar Todos os Dados"):
      if os.path.exists(ARQUIVO_DADOS):
        os.remove(ARQUIVO_DADOS)
      st.warning("Dados apagados com sucesso!")
      st.rerun()