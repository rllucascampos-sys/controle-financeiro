import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle Financeiro", layout="centered")
st.title("💸 Meu Controle de Gastos")

# --- 1. CONEXÃO (O Túnel para o Google) ---
try:
    # Cria a conexão usando as senhas do secrets.toml
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lê os dados da planilha (ttl=5 significa: atualiza a cada 5 segundos)
    data = conn.read(ttl=5)
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop() # Para o código se não conectar

# --- 2. FORMULÁRIO DE CADASTRO (Create) ---
with st.expander("➕ Adicionar Novo Gasto", expanded=True):
    with st.form("form_gastos"):
        # Campos para o usuário preencher
        col1, col2 = st.columns(2)
        with col1:
            data_gasto = st.date_input("Data do Gasto")
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        with col2:
            descricao = st.text_input("Descrição (Ex: Mercado, Uber)")
            categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Moradia", "Lazer", "Outros", "Investimento"])
        
        # Botão de Enviar
        submitted = st.form_submit_button("Salvar Gasto")

        if submitted:
            # Cria uma tabela nova só com essa linha que acabou de ser digitada
            novo_dado = pd.DataFrame([
                {
                    "Data": data_gasto.strftime("%Y-%m-%d"),
                    "Descricao": descricao,
                    "Valor": valor,
                    "Categoria": categoria
                }
            ])
            
            # Junta a tabela antiga (data) com a nova (novo_dado)
            dados_atualizados = pd.concat([data, novo_dado], ignore_index=True)
            
            # Manda para o Google
            conn.update(data=dados_atualizados)
            
            # Feedback e Recarregar
            st.success("Gasto salvo com sucesso!")
            st.cache_data.clear() # Limpa a memória para baixar a planilha atualizada
            st.rerun() # Recarrega a página

# --- 3. VISUALIZAÇÃO (Read) ---
st.divider()
st.subheader("📊 Resumo do Mês")

if not data.empty:
    # Garante que a coluna Valor é número (caso o Google mande como texto)
    # Mostra a tabela de dados
    st.dataframe(data, use_container_width=True)
    
    # Mostra o Total
    total = data["Valor"].sum()
    st.metric("Total Gasto", f"R$ {total:,.2f}")
    
    # Gráfico de Barras por Categoria
    grafico = data.groupby("Categoria")["Valor"].sum()
    st.bar_chart(grafico)
else:
    st.info("Sua planilha está vazia. Adicione o primeiro gasto acima!")