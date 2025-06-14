# =============================================
# Script: app.py
# Projeto: CryptoPrice-Dashboard (versão ao vivo)
# =============================================

from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import altair as alt
import io
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,  # pegue quantas moedas quiser
    "page": 1,
    "price_change_percentage": "24h"
}

# =============================================
# Funções de dados (direto da API)
# =============================================

@st.cache_data(ttl=30)
def get_coingecko_data():
    resp = requests.get(COINGECKO_API_URL, params=COINGECKO_PARAMS)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data)
    return df

def process_analysis(df):
    # Dados de análise para a "Visão Geral"
    df['price_change_percentage_24h'] = pd.to_numeric(df['price_change_percentage_24h'], errors='coerce').fillna(0)
    best_idx = df['price_change_percentage_24h'].idxmax()
    worst_idx = df['price_change_percentage_24h'].idxmin()

    analysis = {
        'best_coin': df.loc[best_idx, 'name'],
        'best_change': df.loc[best_idx, 'price_change_percentage_24h'],
        'worst_coin': df.loc[worst_idx, 'name'],
        'worst_change': df.loc[worst_idx, 'price_change_percentage_24h'],
        'average_change': df['price_change_percentage_24h'].mean(),
        'top1_coin': df.sort_values('price_change_percentage_24h', ascending=False).iloc[0]['name'],
        'top1_change': df.sort_values('price_change_percentage_24h', ascending=False).iloc[0]['price_change_percentage_24h'],
        'top2_coin': df.sort_values('price_change_percentage_24h', ascending=False).iloc[1]['name'],
        'top2_change': df.sort_values('price_change_percentage_24h', ascending=False).iloc[1]['price_change_percentage_24h'],
        'top3_coin': df.sort_values('price_change_percentage_24h', ascending=False).iloc[2]['name'],
        'top3_change': df.sort_values('price_change_percentage_24h', ascending=False).iloc[2]['price_change_percentage_24h'],
        'coins_up': (df['price_change_percentage_24h'] > 0).sum(),
        'coins_down': (df['price_change_percentage_24h'] < 0).sum(),
        'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return pd.DataFrame([analysis])

def format_table(df):
    df = df.copy()
    # Formatando valores para pt-BR
    for col in ['current_price', 'market_cap', 'total_volume', 'ath', 'atl']:
        df[col] = df[col].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['circulating_supply'] = df['circulating_supply'].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['price_change_percentage_24h'] = df['price_change_percentage_24h'].apply(lambda x: f"{x:.2f}%")
    df['last_updated'] = pd.to_datetime(df['last_updated']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df.rename(columns={
        "id": "Nome Técnico",
        "symbol": "Símbolo",
        "name": "Nome da Moeda",
        "current_price": "Preço Atual (US$)",
        "price_change_percentage_24h": "Variação 24h (%)",
        "market_cap": "Valor de Mercado (US$)",
        "market_cap_rank": "Ranking de Mercado",
        "total_volume": "Volume Total (US$)",
        "circulating_supply": "Quantidade Circulante",
        "ath": "Preço Máximo Histórico",
        "atl": "Preço Mínimo Histórico",
        "last_updated": "Última Atualização"
    }, inplace=True)
    return df

# =============================================
# Funções de Páginas (sem alteração)
# =============================================

def mostrar_visao_geral(df):

    # Buscar dados do dataframe
    moeda_subiu = df['best_coin'][0]
    var_subiu = df['best_change'][0]

    moeda_caiu = df['worst_coin'][0]
    var_caiu = df['worst_change'][0]

    media_geral = df['average_change'][0]

    # Layout com três colunas de cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style='padding: 1rem; border-radius: 12px; background-color: #1c1c1c; text-align: center;'>
                <h3>📈 Moeda que Mais Subiu</h3>
                <h1 style='color: #22c55e;'>{moeda_subiu}</h1>
                <p style='color: #22c55e; font-size: 1.5rem;'>⬆️ {var_subiu:.2f}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style='padding: 1rem; border-radius: 12px; background-color: #1c1c1c; text-align: center;'>
                <h3>📉 Moeda que Mais Caiu</h3>
                <h1 style='color: #ef4444;'>{moeda_caiu}</h1>
                <p style='color: #ef4444; font-size: 1.5rem;'>⬇️ {var_caiu:.2f}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style='padding: 1rem; border-radius: 12px; background-color: #1c1c1c; text-align: center;'>
                <h3>📊 Média de Variação</h3>
                <h1 style='color: #60a5fa;'>{media_geral:.2f}%</h1>
                <h4></h4>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Pequena mensagem motivacional com base na media geral
    if media_geral >= 0.5:
        st.success("🚀 O mercado está em alta! Fique atento às oportunidades.")
    elif media_geral <= -0.5:
        st.error("📉 Atenção! O mercado está retraindo hoje.")
    else:
        st.info("📈 Mercado está relativamente estável no momento.")

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================
    # Top 3 moedas que mais subiram
    # =============================
    st.subheader("🏆 Top 3 Criptomoedas em Alta")

    top3 = df[['top1_coin', 'top1_change', 'top2_coin', 'top2_change', 'top3_coin', 'top3_change']]

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(label=top3['top1_coin'][0], value=f"{top3['top1_change'][0]:.2f}%", delta_color="normal")

    with col5:
        st.metric(label=top3['top2_coin'][0], value=f"{top3['top2_change'][0]:.2f}%", delta_color="normal")

    with col6:
        st.metric(label=top3['top3_coin'][0], value=f"{top3['top3_change'][0]:.2f}%", delta_color="normal")

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================
    # Gráfico de quantas moedas subiram e caíram
    # =============================
    st.subheader("📊 Resumo de Performance das Moedas")

    # Exemplo de df para gráfico
    grafico_df = pd.DataFrame({
        'Status': ['Subiram', 'Caíram'],
        'Quantidade': [df['coins_up'][0], df['coins_down'][0]]
    })

    grafico = alt.Chart(grafico_df).mark_bar(size=40).encode(
        x=alt.X('Status:N', title='Status'),
        y=alt.Y('Quantidade:Q', title='Quantidade de Moedas'),
        color=alt.Color('Status:N', scale=alt.Scale(domain=['Subiram', 'Caíram'], range=['#22c55e', '#ef4444'])),
        tooltip=['Status:N', 'Quantidade:Q']
    ).properties(
        width=500,
        height=300
    )

    st.altair_chart(grafico, use_container_width=True)

    # =============================
    # Última atualização humanizada
    # =============================
    ultima_atualizacao = df['ultima_atualizacao'][0]
    ultima_atualizacao_dt = datetime.strptime(ultima_atualizacao, '%Y-%m-%d %H:%M:%S')
    tempo_passado = datetime.now() - ultima_atualizacao_dt
    minutos_passados = int(tempo_passado.total_seconds() // 60)

    st.caption(f"⏳ Atualizado há {minutos_passados} minutos.")

import plotly.express as px

def mostrar_graficos(df_raw):
    st.header("📊 Análises Gráficas (Dinâmico)")

    if df_raw is not None:
        col_moeda = "Nome da Moeda" if "Nome da Moeda" in df_raw.columns else "name"
        moedas_disponiveis = sorted(df_raw[col_moeda].unique())

        mostrar_so_favoritas = st.checkbox("🔍 Mostrar apenas favoritas", value=False)

        if mostrar_so_favoritas and "favoritas" in st.session_state and st.session_state.favoritas:
            moedas_disponiveis = [moeda for moeda in moedas_disponiveis if moeda in st.session_state.favoritas]

        opcoes_moedas = st.multiselect(
            "Escolha as criptomoedas para visualizar:",
            options=moedas_disponiveis,
            default=moedas_disponiveis,
            placeholder="Selecione moedas..."
        )

        metricas_disponiveis = ["Variação 24h (%)", "Preço Atual (US$)", "Quantidade Circulante"]
        metrica_escolhida = st.selectbox(
            "Selecione a métrica para o gráfico:",
            metricas_disponiveis
        )

        ordenacao = st.radio(
            "Ordenação dos dados:",
            ("Misto", "Crescente", "Decrescente"),
            horizontal=True,
            label_visibility="collapsed"
        )

        df_filtrado = df_raw[df_raw[col_moeda].isin(opcoes_moedas)][[col_moeda, metrica_escolhida]].copy()
        df_filtrado.rename(columns={col_moeda: "Nome da Moeda"}, inplace=True)

        if metrica_escolhida in ["Preço Atual (US$)", "Quantidade Circulante"]:
            df_filtrado[metrica_escolhida] = (
                df_filtrado[metrica_escolhida]
                .astype(str)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )
        elif metrica_escolhida == "Variação 24h (%)":
            df_filtrado[metrica_escolhida] = (
                df_filtrado[metrica_escolhida]
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )

        if ordenacao == "Crescente":
            df_filtrado = df_filtrado.sort_values(by=metrica_escolhida, ascending=True)
        elif ordenacao == "Decrescente":
            df_filtrado = df_filtrado.sort_values(by=metrica_escolhida, ascending=False)

        st.markdown("---")

        st.caption({
            "Variação 24h (%)": "ℹ️ Percentual de valorização ou desvalorização nas últimas 24 horas.",
            "Preço Atual (US$)": "ℹ️ Valor atual da criptomoeda em dólares americanos.",
            "Quantidade Circulante": "ℹ️ Número total de unidades disponíveis no mercado."
        }[metrica_escolhida])

        # Aqui entra o Plotly!
        fig = px.bar(
            df_filtrado,
            x="Nome da Moeda",
            y=metrica_escolhida,
            color=metrica_escolhida,
            text=metrica_escolhida,
            labels={"Nome da Moeda": "Criptomoeda"},
            template="plotly_dark",
            height=500
        )
        fig.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside'
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=80)
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nenhum dado disponível para gerar o gráfico.")

def mostrar_tabela(df_raw, df_raw_formatado):
    st.header("🔍 Tabela Detalhada das Criptomoedas")

    if df_raw is not None and df_raw_formatado is not None:
        tipo_exibicao = st.radio(
            "Tipo de Exibição:",
            ("Formatado (padrão)", "Dados Brutos"),
            horizontal=True
        )

        df_exibido = df_raw_formatado if tipo_exibicao == "Formatado (padrão)" else df_raw

        # CORREÇÃO: descobre o nome certo da coluna para moeda
        col_moeda = "Nome da Moeda" if "Nome da Moeda" in df_exibido.columns else "name"
        moedas_disponiveis = sorted(df_exibido[col_moeda].unique())

        mostrar_so_favoritas = st.checkbox("🔍 Mostrar apenas favoritas", value=False)

        if mostrar_so_favoritas and "favoritas" in st.session_state and st.session_state.favoritas:
            moedas_disponiveis = [moeda for moeda in moedas_disponiveis if moeda in st.session_state.favoritas]

        opcoes_moedas = st.multiselect(
            "Filtrar criptomoedas:",
            options=moedas_disponiveis,
            default=moedas_disponiveis,
            placeholder="Selecione as moedas..."
        )

        df_filtrado = df_exibido[df_exibido[col_moeda].isin(opcoes_moedas)].copy()
        df_filtrado.index = df_filtrado.index + 1

        st.dataframe(df_filtrado, use_container_width=True)

        formato_exportacao = st.radio(
            "Escolha o formato para exportar:",
            ("CSV", "Excel (.xlsx)"),
            horizontal=True
        )

        data_atual = datetime.now().strftime("%Y-%m-%d")
        nome_base = f"CryptoPrice_Tabela_{data_atual}"

        if formato_exportacao == "CSV":
            buffer = io.BytesIO()
            df_filtrado.to_csv(buffer, index=False, encoding='utf-8-sig')
            buffer.seek(0)
            st.download_button(
                label="⬇️ Baixar Tabela (CSV)",
                data=buffer,
                file_name=f"{nome_base}.csv",
                mime='text/csv'
            )

        elif formato_exportacao == "Excel (.xlsx)":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtrado.to_excel(writer, sheet_name='Criptomoedas', index=False)
            buffer.seek(0)
            st.download_button(
                label="⬇️ Baixar Tabela (Excel)",
                data=buffer,
                file_name=f"{nome_base}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.warning("Nenhum dado para mostrar.")

def mostrar_favoritas(df_raw):
    st.header("⭐ Gerenciar Moedas Favoritas")

    if "favoritas" not in st.session_state:
        st.session_state.favoritas = []

    if df_raw is not None:
        # Usa col_moeda igual ao resto
        col_moeda = "Nome da Moeda" if "Nome da Moeda" in df_raw.columns else "name"
        moedas_disponiveis = sorted(df_raw[col_moeda].unique())

        for moeda in moedas_disponiveis:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(moeda)
            with col2:
                if moeda in st.session_state.favoritas:
                    if st.button("⭐", key=f"desfav_{moeda}"):
                        st.session_state.favoritas.remove(moeda)
                else:
                    if st.button("☆", key=f"fav_{moeda}"):
                        st.session_state.favoritas.append(moeda)

        if st.session_state.favoritas:
            st.success(f"Favoritas: {', '.join(st.session_state.favoritas)}")
        else:
            st.info("Nenhuma moeda favoritada ainda.")
    else:
        st.warning("Nenhum dado disponível para favoritar.")

# =============================================
# Aplicativo Principal
# =============================================

def main():
    st.set_page_config(page_title="Crypto Dashboard", layout="wide")

    # ⏱️ Atualização automática (30 segundos)
    st_autorefresh(interval=30 * 1000, key='auto_refresh')

    st.title("🚀 CryptoPrice Dashboard")
    st.subheader("Monitoramento detalhado de crescimento e variação de criptomoedas.")

    st.sidebar.title("📋 Menu de Navegação")
    if "pagina" not in st.session_state:
        st.session_state.pagina = "🏠 Visão Geral"

    if st.sidebar.button("🏠 Visão Geral"):
        st.session_state.pagina = "🏠 Visão Geral"
    if st.sidebar.button("📈 Gráficos"):
        st.session_state.pagina = "📈 Gráficos"
    if st.sidebar.button("📑 Tabela Detalhada"):
        st.session_state.pagina = "📑 Tabela Detalhada"
    if st.sidebar.button("⭐ Moedas Favoritas"):
        st.session_state.pagina = "⭐ Moedas Favoritas"

    st.sidebar.markdown("---")

    # Carregar dados ao vivo
    try:
        df = get_coingecko_data()
    except Exception as e:
        st.error(f"Erro ao obter dados da CoinGecko: {e}")
        return

    df_analysis = process_analysis(df)
    df_formatado = format_table(df)

    # Última atualização no sidebar
    st.sidebar.markdown(
        f"""
        <div style="padding-left: 5px; font-size: 0.85em;">
            🕒 <b>Última Atualização:</b><br>
            <span style="padding-left: 10px;">{df_analysis['ultima_atualizacao'][0]}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Exibir conteúdo conforme página
    if st.session_state.pagina == "🏠 Visão Geral":
        mostrar_visao_geral(df_analysis)
    elif st.session_state.pagina == "📈 Gráficos":
        mostrar_graficos(df_formatado)
    elif st.session_state.pagina == "📑 Tabela Detalhada":
        mostrar_tabela(df, df_formatado)
    elif st.session_state.pagina == "⭐ Moedas Favoritas":
        mostrar_favoritas(df_formatado)

# =============================================
# Execução
# =============================================

if __name__ == "__main__":
    main()
    st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)
