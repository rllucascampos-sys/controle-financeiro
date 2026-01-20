import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sempre a primeira linha) ---
st.set_page_config(
    page_title="Gestão Financeira Pro",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PERSONALIZADO (A Maquiagem) ---
st.markdown("""
<style>
    /* Estilo para os Cards (Métricas) */
    [data-testid="stMetric"] {
        background-color: #262730;
        border: 1px solid #464b5f;
        padding: 15px;
        border-radius: 10px;
        color: white;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    
    /* Título das Métricas em cor diferente */
    [data-testid="stMetricLabel"] {
        color: #a3a8b8;
        font-size: 14px;
    }

    /* Botão de Salvar mais bonito */
    div.stButton > button {
        width: 100%;
        background-color: #00C853;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #009624;
        color: white;
        border: 1px solid white;
    }

    /* Ajuste das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #0e1117;
        border-radius: 5px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
        border-bottom: 2px solid #00C853;
    }
</style>
""", unsafe_allow_html=True)

st.title("💸 Minha Central Financeira")

# --- 3. CONEXÃO E DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    data = conn.read(ttl=5)
    if data.empty:
        data = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descricao", "Valor"])
except:
    data = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descricao", "Valor"])

# --- 4. SIDEBAR (Lateral) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2382/2382461.png", width=100) # Ícone de Dinheiro
    st.header("Filtros do Mês")
    mes_selecionado = st.selectbox("Mês", range(1, 13), index=datetime.datetime.now().month - 1)
    ano_selecionado = st.number_input("Ano", value=datetime.datetime.now().year)
    st.divider()
    st.info("💡 Dica: Mantenha seus gastos fixos abaixo de 50% da renda.")

# Converter data
data["Data"] = pd.to_datetime(data["Data"], errors='coerce')

# --- 5. ESTRUTURA DE ABAS ---
aba1, aba2, aba3 = st.tabs(["📝 Lançamentos", "📊 Dashboards", "🛡️ Segurança"])

# ================= ABA 1: LANÇAMENTOS =================
with aba1:
    st.markdown("### Novo Lançamento")
    with st.container(border=True): # Cria uma caixa ao redor do formulário
        with st.form("form_transacao", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                data_mov = st.date_input("📅 Data", datetime.date.today())
                tipo = st.radio("Tipo", ["🔴 Saída (Gasto)", "🟢 Entrada (Receita)"], horizontal=True)
            
            with col2:
                # Lógica de Categorias Dinâmicas
                if "Entrada" in tipo:
                    lista = ["Salário 05", "Adiantamento 20", "Vale Refeição", "Vale Transporte", "Renda Extra", "Outros"]
                else:
                    lista = ["Gasto Fixo (Casa)", "Gasto Fixo (Contas)", "Lazer/Fim de Semana", "Transporte/Uber", "Mercado", "Investimento", "Saúde", "Educação"]
                
                categoria = st.selectbox("📂 Categoria", lista)
                valor = st.number_input("💲 Valor (R$)", min_value=0.0, format="%.2f")
            
            descricao = st.text_input("📝 Descrição (Detalhe do gasto)")
            
            # Espaço para separar o botão
            st.write("") 
            submitted = st.form_submit_button("✅ SALVAR REGISTRO")

            if submitted:
                tipo_limpo = "Entrada" if "Entrada" in tipo else "Saída"
                novo_dado = pd.DataFrame([{
                    "Data": data_mov.strftime("%Y-%m-%d"),
                    "Tipo": tipo_limpo,
                    "Categoria": categoria,
                    "Descricao": descricao,
                    "Valor": valor
                }])
                dados_atualizados = pd.concat([data, novo_dado], ignore_index=True)
                conn.update(data=dados_atualizados)
                st.toast("Lançamento salvo com sucesso!", icon="🎉") # Notificação pop-up
                st.rerun()

    # Tabela Recente
    st.subheader("Histórico Recente")
    st.dataframe(
        data.tail(5).sort_values(by="Data", ascending=False), 
        use_container_width=True,
        hide_index=True
    )

# ================= ABA 2: DASHBOARD =================
with aba2:
    # Filtro de Dados
    df_mes = data[(data["Data"].dt.month == mes_selecionado) & (data["Data"].dt.year == ano_selecionado)]

    if not df_mes.empty:
        # Cálculos
        entradas = df_mes[df_mes["Tipo"] == "Entrada"]["Valor"].sum()
        saidas = df_mes[df_mes["Tipo"] == "Saída"]["Valor"].sum()
        saldo = entradas - saidas
        investido = df_mes[df_mes["Categoria"] == "Investimento"]["Valor"].sum()

        # KPIs (Métricas) Estilizadas pelo CSS
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ganhos", f"R$ {entradas:,.2f}")
        c2.metric("Gastos", f"R$ {saidas:,.2f}", delta=-saidas, delta_color="inverse")
        c3.metric("Saldo", f"R$ {saldo:,.2f}", delta=saldo)
        c4.metric("Investido", f"R$ {investido:,.2f}")

        st.markdown("---")

        # Gráficos Lado a Lado
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### 💸 Gastos por Categoria")
            df_saidas = df_mes[df_mes["Tipo"] == "Saída"]
            if not df_saidas.empty:
                st.bar_chart(df_saidas.groupby("Categoria")["Valor"].sum(), color="#FF4B4B")
            else:
                st.info("Sem gastos este mês.")
        
        with g2:
            st.markdown("#### ⚖️ Entradas vs Saídas")
            resumo = pd.DataFrame({"Tipo": ["Entradas", "Saídas"], "Valor": [entradas, saidas]}).set_index("Tipo")
            st.bar_chart(resumo, color=["#00C853", "#FF4B4B"]) # Tenta colorir se a versão permitir, senão usa padrão
            
    else:
        st.warning("Nenhum dado encontrado para este período.")

# ================= ABA 3: SEGURANÇA =================
with aba3:
    st.markdown("## 🛡️ Sua Fortaleza Financeira")
    
    # Cálculo Inteligente
    custos_fixos = data[data["Categoria"].str.contains("Fixo", na=False)]
    media_fixo = custos_fixos["Valor"].sum() / max(data["Data"].dt.month.nunique(), 1) if not custos_fixos.empty else 0
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.info(f"**Custo Fixo Mensal:** R$ {media_fixo:,.2f}")
        meses = st.slider("Meses de Segurança:", 1, 12, 6)
    
    with c2:
        meta = media_fixo * meses
        total_guardado = data[data["Categoria"] == "Investimento"]["Valor"].sum()
        falta = meta - total_guardado
        
        st.metric("Meta da Reserva", f"R$ {meta:,.2f}")
        
        if meta > 0:
            progresso = min(total_guardado / meta, 1.0)
            st.progress(progresso)
            st.caption(f"Você já tem R$ {total_guardado:,.2f} ({progresso*100:.0f}%)")
            
            if falta > 0:
                st.write(f"📉 Faltam **R$ {falta:,.2f}** para sua tranquilidade.")
            else:
                st.success("🎉 META BATIDA! Você está seguro.")
