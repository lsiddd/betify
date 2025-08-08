# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from contextlib import contextmanager

# ==============================================================================
# --- CONFIGURAÇÃO DA PÁGINA E TEMA ---
# ==============================================================================

st.set_page_config(
    page_title="GuardianAI - Plataforma de Risco",
    page_icon="https://i.imgur.com/s6pCMWz.png",
    layout="wide",
)

# Dicionário centralizado para o tema da aplicação
APP_THEME = {
    "primary": "#3A78C4",
    "danger": "#D9534F",
    "warning": "#F0AD4E",
    "success": "#5CB85C",
    "background": "#0E1117",
    "widget_background": "#1A1F2E",
    "text": "#EAEAEA",
    "subtle_text": "#A0AEC0",
    "grid": "#2D3748"
}

# CSS Personalizado que utiliza as variáveis do tema
st.markdown(f"""
<style>
    :root {{
        --primary-color: {APP_THEME['primary']};
        --danger-color: {APP_THEME['danger']};
        --warning-color: {APP_THEME['warning']};
        --success-color: {APP_THEME['success']};
        --background-color: {APP_THEME['background']};
        --widget-background-color: {APP_THEME['widget_background']};
        --text-color: {APP_THEME['text']};
        --subtle-text-color: {APP_THEME['subtle_text']};
        --font-family: 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }}
    body {{
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: var(--font-family);
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 600;
        color: var(--text-color);
    }}
    .widget-container {{
        padding: 1.2rem 1.5rem;
        border-radius: 0.5rem;
        background-color: var(--widget-background-color);
        border: 1px solid {APP_THEME['grid']};
        margin-bottom: 1rem;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
        border-bottom: 2px solid {APP_THEME['grid']};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding: 10px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: var(--widget-background-color);
        border: 2px solid {APP_THEME['grid']};
        border-bottom: 2px solid var(--widget-background-color);
        color: var(--primary-color);
        font-weight: 600;
    }}
    .user-card {{
        border-left: 5px solid var(--subtle-text-color);
        padding: 1rem; margin-bottom: 0.5rem;
        background-color: #242b42; border-radius: 4px;
    }}
    .user-card.high-risk {{ border-left-color: var(--danger-color); }}
    .user-card.medium-risk {{ border-left-color: var(--warning-color); }}
    .user-card.selected {{
        border-color: var(--primary-color);
        box-shadow: 0 0 10px rgba(58, 120, 196, 0.6);
    }}
    hr {{
        border-color: {APP_THEME['grid']};
    }}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# --- GERAÇÃO DE DADOS MOCK ---
# ==============================================================================

@st.cache_data
def generate_br_mock_data():
    np.random.seed(42)
    now = datetime.now()
    users_data = []
    shared_device = "dev_shared_SP_A7B8"
    for i in range(8): users_data.append({"user_id": f"multi_acct_sp_{i+1}", "risk_score": 920 + i*5, "main_risk_factor": "Anel de Fraude (Multi-Conta)", "device_id": shared_device, "payment_method_id": f"pix_key_{i}", "payment_type": "PIX", "ip_asn": "AS28573 (Vivo/Telefonica)", "registration_time": now - timedelta(hours=2, minutes=i*7), "state": "SP", "lat": -23.5505, "lon": -46.6333, "status": "active", "total_deposited": 250, "avg_bet_value": 75.50, "session_time_sec": 45, "peer_group": "Apostador Casual"})
    users_data.append({"user_id": "cpf_fraud_rj_01", "risk_score": 980, "main_risk_factor": "Fraude de Identidade (CPF)", "device_id": "dev_vm_cloud_01", "payment_method_id": "card_hash_...1122", "payment_type": "Cartão de Crédito", "ip_asn": "AS262372 (Amazon AWS)", "registration_time": now - timedelta(days=2), "state": "RJ", "lat": -22.9068, "lon": -43.1729, "status": "active", "total_deposited": 5000, "avg_bet_value": 500.00, "session_time_sec": 120, "peer_group": "High Roller"})
    users_data.append({"user_id": "bonus_hunter_ba", "risk_score": 710, "main_risk_factor": "Abuso de Bônus", "device_id": "dev_mobile_proxy_01", "payment_method_id": "boleto_...3344", "payment_type": "Boleto", "ip_asn": "AS_Proxy_Network", "registration_time": now - timedelta(hours=3), "state": "BA", "lat": -12.9777, "lon": -38.5016, "status": "active", "total_deposited": 50, "avg_bet_value": 10.00, "session_time_sec": 30, "peer_group": "Caçador de Bônus"})
    users_data.append({"user_id": "pix_chargeback_mg", "risk_score": 850, "main_risk_factor": "Chargeback Fraudulento", "device_id": "dev_mobile_mg_99", "payment_method_id": "pix_key_disposable", "payment_type": "PIX", "ip_asn": "AS28573 (Claro)", "registration_time": now - timedelta(days=10), "state": "MG", "lat": -19.9167, "lon": -43.9345, "status": "active", "total_deposited": 1500, "avg_bet_value": 150.00, "session_time_sec": 85, "peer_group": "Apostador Casual"})
    df_users = pd.DataFrame(users_data)
    
    bets_data = [{'odd': np.random.uniform(1.1, 5.0), 'value': np.random.uniform(5, 100), 'type': 'Padrão'} for _ in range(400)]
    bets_data.extend([{'odd': np.random.uniform(8.0, 25.0), 'value': np.random.uniform(200, 500), 'type': 'Anômala'} for _ in range(20)])
    df_bets = pd.DataFrame(bets_data)

    return df_users, df_bets

# ==============================================================================
# --- COMPONENTES DE UI ---
# ==============================================================================

@contextmanager
def widget_container():
    """Gerenciador de contexto para criar um container de widget padronizado."""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    yield
    st.markdown('</div>', unsafe_allow_html=True)

def apply_theme_to_fig(fig, theme):
    """Aplica o tema visual padrão a uma figura Plotly."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=theme['text'],
        legend_font_color=theme['text'],
        margin=dict(l=10, r=10, t=40, b=10) # Ajuste de margem
    )
    return fig

# ==============================================================================
# --- FUNÇÕES DE GERAÇÃO DE GRÁFICOS ---
# ==============================================================================

# --- Funções do Ato I ---
def create_global_risk_score_gauge(theme):
    avg_risk = st.session_state.df_users['risk_score'].mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=avg_risk,
        title={'text': "Score de Risco Global", 'font': {'size': 20}},
        gauge={'axis': {'range': [None, 1000]}, 'bar': {'color': theme['primary']},
               'threshold': {'line': {'color': theme['danger'], 'width': 4}, 'thickness': 0.9, 'value': 850}}))
    return apply_theme_to_fig(fig.update_layout(height=250), theme)

def create_risk_map_br(theme):
    df_map = st.session_state.df_users.copy()
    df_map['size'] = df_map['risk_score'] / 40
    fig = px.scatter_geo(df_map, lat='lat', lon='lon', color="main_risk_factor",
                         hover_name="user_id", size="size", scope="south america",
                         color_discrete_map={
                             "Anel de Fraude (Multi-Conta)": theme['danger'], 
                             "Fraude de Identidade (CPF)": theme['danger'],
                             "Chargeback Fraudulento": theme['warning'], 
                             "Abuso de Bônus": theme['warning']
                         })
    fig.update_layout(geo=dict(landcolor=theme['grid'], countrycolor=theme['subtle_text'], bgcolor='rgba(0,0,0,0)'), margin=dict(l=0, r=0, t=0, b=0))
    return apply_theme_to_fig(fig, theme)

def create_top_threats_chart(theme):
    threats = st.session_state.df_users['main_risk_factor'].value_counts().reset_index()
    fig = px.bar(threats, x='count', y='main_risk_factor', orientation='h', color='count',
                 color_continuous_scale='Reds', labels={'count': 'Casos', 'main_risk_factor': 'Ameaça'})
    return apply_theme_to_fig(fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}), theme)

# --- Funções do Ato II ---
def create_laranjometro_gauge(theme):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=82, title={'text': "Score 'Potencial Laranja'"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': theme['warning']},
               'steps': [{'range': [0, 50], 'color': 'rgba(92, 184, 92, 0.5)'},
                         {'range': [50, 80], 'color': 'rgba(240, 173, 78, 0.5)'}]}))
    return apply_theme_to_fig(fig.update_layout(height=200), theme)

def create_bet_pattern_scatter(theme):
    fig = px.scatter(st.session_state.df_bets, x="value", y="odd", color="type",
                     labels={"value": "Valor da Aposta (R$)", "odd": "Odd da Aposta"},
                     color_discrete_map={'Padrão': theme['primary'], 'Anômala': theme['danger']})
    return apply_theme_to_fig(fig, theme)

def create_bonus_monitor_chart(theme):
    data = {'Campanha': ['Bônus Boas-Vindas', 'Recarga FDS', 'Free Bet Clássico'],
            'Conversão (%)': [85, 60, 45], 'Suspeita de Abuso (%)': [15, 8, 22]}
    fig = go.Figure([go.Bar(name='Conversão', x=data['Campanha'], y=data['Conversão (%)'], marker_color=theme['success']),
                     go.Bar(name='Suspeita de Abuso', x=data['Campanha'], y=data['Suspeita de Abuso (%)'], marker_color=theme['danger'])])
    return apply_theme_to_fig(fig.update_layout(barmode='group', yaxis_title="%"), theme)

# --- Funções do Ato III ---
def create_behavioral_timeline(user_data, theme):
    events = [{'Action': 'Cadastro', 'Timestamp': user_data['registration_time']},
              {'Action': 'Login', 'Timestamp': datetime.now() - timedelta(hours=2)},
              {'Action': 'Depósito', 'Timestamp': datetime.now() - timedelta(hours=1, minutes=50)},
              {'Action': 'Aposta Alta', 'Timestamp': datetime.now() - timedelta(minutes=20)},
              {'Action': 'Tentativa Saque', 'Timestamp': datetime.now() - timedelta(minutes=5)}]
    df = pd.DataFrame(events).sort_values("Timestamp")
    fig = px.scatter(df, x='Timestamp', y=['Ação']*len(df), text='Action', title="Linha do Tempo Comportamental")
    fig.update_traces(textposition="top center", marker=dict(color=theme['primary'], size=12))
    return apply_theme_to_fig(fig.update_layout(yaxis_title="", xaxis_title="Horário do Evento", yaxis_visible=False), theme)

def create_peer_comparison_chart(user, theme):
    peers = {'Apostador Casual': (50, 60), 'High Roller': (250, 180), 'Caçador de Bônus': (15, 25)}
    peer_avg_bet, peer_avg_session = peers[user['peer_group']]
    fig = go.Figure([go.Bar(name='Usuário Investigado', y=['Tempo Sessão (s)', 'Aposta Média (R$)'], x=[user['session_time_sec'], user['avg_bet_value']], orientation='h', marker_color=theme['danger']),
                     go.Bar(name=f"Média ({user['peer_group']})", y=['Tempo Sessão (s)', 'Aposta Média (R$)'], x=[peer_avg_session, peer_avg_bet], orientation='h', marker_color=theme['primary'])])
    return apply_theme_to_fig(fig.update_layout(barmode='group', height=250, title="Comparativo (Usuário vs. Pares)"), theme)

def create_investigation_graph(user_data, theme):
    net = Network(height="400px", width="100%", bgcolor=theme['widget_background'], font_color=theme['text'], notebook=True, directed=True)
    net.add_node(user_data['user_id'], label=user_data['user_id'], color=theme['danger'], size=25)
    if "Anel de Fraude" in user_data['main_risk_factor']:
        device_node = user_data['device_id']
        net.add_node(device_node, label=f"Device: {device_node}", shape='box', color=theme['warning'], size=20)
        for _, row in st.session_state.df_users[st.session_state.df_users['device_id'] == device_node].iterrows():
            if row['user_id'] != user_data['user_id']: 
                net.add_node(row['user_id'], label=row['user_id'], color=theme['primary'], size=15)
            net.add_edge(row['user_id'], device_node)
    else:
        net.add_node(user_data['device_id'], label=f"Device: {user_data['device_id']}", shape='box', color=theme['warning'], size=20)
        net.add_node(user_data['payment_type'], label=f"Pagamento: {user_data['payment_type']}", shape='diamond', color=theme['success'], size=20)
        net.add_edge(user_data['user_id'], user_data['device_id'])
        net.add_edge(user_data['user_id'], user_data['payment_type'])
    net.set_options('{"physics": {"barnesHut": {"gravitationalConstant": -3000, "springConstant": 0.05, "springLength": 150}}}')
    net.save_graph("fraud_network.html")
    return open("fraud_network.html", 'r', encoding='utf-8').read()

# --- Funções do Ato IV ---
def create_fraud_heatmap(theme):
    data = {'Multi-Conta (CPF)': [75000, 15000], 'Abuso de Bônus': [45000, 8000], 'Conluio': [150000, 35000], 'Chargeback PIX': [95000, 55000]}
    df = pd.DataFrame(data, index=['Perda Potencial (R$)', 'Perda Realizada (R$)'])
    fig = px.imshow(df, text_auto=True, aspect="auto", labels=dict(x="Tipologia de Fraude", y="Métrica", color="Valor (R$)"), color_continuous_scale='Reds')
    return apply_theme_to_fig(fig, theme)

def create_predictive_event_risk_chart(theme):
    data = {'Evento': ['Brasileirão - Clássico', 'Final Copa do Brasil', 'Libertadores', 'eSports - Final CBLOL'], 'Risco Previsto (%)': [85, 92, 78, 65]}
    df_data = pd.DataFrame(data)
    fig = px.bar(df_data, x='Evento', y='Risco Previsto (%)', title='Análise Preditiva de Risco de Eventos', color='Risco Previsto (%)', color_continuous_scale='Reds')
    return apply_theme_to_fig(fig, theme)


# ==============================================================================
# --- LAYOUT DA APLICAÇÃO ---
# ==============================================================================

# --- Inicialização do Estado da Sessão ---
if 'df_users' not in st.session_state:
    st.session_state.df_users, st.session_state.df_bets = generate_br_mock_data()
if 'selected_case_id' not in st.session_state:
    st.session_state.selected_case_id = None

# --- Cabeçalho ---
st.title("GuardianAI: Plataforma de Análise de Risco")
st.caption(f"Dados atualizados em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- Abas Principais ---
ato1, ato2, ato3, ato4 = st.tabs(["Ato I: Pulso da Operação", "Ato II: Vigília Constante", "Ato III: Sala de Investigação", "Ato IV: Inteligência Estratégica"])

with ato1:
    st.header("Visão Geral e Saúde da Plataforma")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with widget_container():
            st.plotly_chart(create_global_risk_score_gauge(APP_THEME), use_container_width=True)
        with widget_container():
            st.subheader("KPIs Financeiros de Risco")
            kp1, kp2 = st.columns(2)
            kp1.metric("GGR em Risco (24h)", "R$ 92.580", "-8%")
            kp2.metric("Fraudes Prevenidas (Mês)", "R$ 4.8M")
    with col2:
        with widget_container():
            st.subheader("Atividade e Risco Geográfico")
            st.plotly_chart(create_risk_map_br(APP_THEME), use_container_width=True)
    with widget_container():
        st.subheader("Principais Ameaças Ativas")
        st.plotly_chart(create_top_threats_chart(APP_THEME), use_container_width=True)

with ato2:
    st.header("Monitoramento em Tempo Real e Alertas")
    col1, col2 = st.columns([1.5, 2])
    with col1:
        st.subheader("Fila de Investigação")
        high_risk_cases = st.session_state.df_users[st.session_state.df_users['status'] == 'active'].sort_values("risk_score", ascending=False)
        for _, row in high_risk_cases.iterrows():
            risk_level = "high-risk" if row['risk_score'] > 800 else "medium-risk"
            is_selected = row['user_id'] == st.session_state.selected_case_id
            card_class = f"user-card {risk_level}{' selected' if is_selected else ''}"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f"**Usuário:** `{row['user_id']}` | **Score:** {row['risk_score']}")
            st.markdown(f"<small style='color:var(--subtle-text-color)'>Fator de Risco: {row['main_risk_factor']}</small>", unsafe_allow_html=True)
            if st.button("Analisar Caso", key=f"investigate_{row['user_id']}", type="primary", use_container_width=True):
                st.session_state.selected_case_id = row['user_id']
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("Painéis de Análise em Tempo Real")
        with st.expander("Análise de Contas Novas ('Laranjômetro')", expanded=True):
            with widget_container():
                st.plotly_chart(create_laranjometro_gauge(APP_THEME), use_container_width=True)
                c1, c2 = st.columns(2)
                c1.metric("Velocidade de Criação (hora)", "210 contas", "+45%")
                c2.metric("Uso de E-mails Temporários", "18%", "ALERTA")
        with st.expander("Visualizador de Padrões de Apostas Anômalas", expanded=True):
            with widget_container():
                st.plotly_chart(create_bet_pattern_scatter(APP_THEME), use_container_width=True)
        with st.expander("Monitor de Bônus e Promoções", expanded=True):
            with widget_container():
                st.plotly_chart(create_bonus_monitor_chart(APP_THEME), use_container_width=True)

with ato3:
    if not st.session_state.selected_case_id:
        st.info("Selecione um caso na 'Fila de Investigação' (Ato II) para iniciar a análise profunda.")
    else:
        user_data = st.session_state.df_users[st.session_state.df_users['user_id'] == st.session_state.selected_case_id].iloc[0].to_dict()
        st.header(f"Análise Profunda do Caso: {user_data['user_id']}")
        with widget_container():
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Dossiê 360° do Usuário")
                st.markdown(f"""
                - **Score:** <span style='color:var(--danger-color); font-weight:bold;'>{user_data['risk_score']}</span><br>
                - **Fator Principal:** {user_data['main_risk_factor']}<br>
                - **Localização:** {user_data['state']}, Brasil | **ASN:** {user_data['ip_asn']}<br>
                - **Device ID:** `{user_data['device_id']}`<br>
                - **Total Depositado:** R$ {user_data['total_deposited']:.2f}
                """, unsafe_allow_html=True)
            with c2:
                st.subheader("Comparativo de Comportamento")
                st.plotly_chart(create_peer_comparison_chart(user_data, APP_THEME), use_container_width=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("Grafo de Conexões")
                components.html(create_investigation_graph(user_data, APP_THEME), height=410)
            with c4:
                st.subheader("Linha do Tempo Comportamental")
                st.plotly_chart(create_behavioral_timeline(user_data, APP_THEME), use_container_width=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.subheader("Painel de Ação e Gerenciamento do Caso")
            def close_case():
                st.session_state.selected_case_id = None
            
            act_cols = st.columns([1.5, 1.5, 1.5, 2])
            act_cols[0].button("Bloquear Conta", key=f"block_{user_data['user_id']}", type="primary", use_container_width=True)
            act_cols[1].button("Monitorar", key=f"monitor_{user_data['user_id']}", use_container_width=True)
            act_cols[2].button("Gerar Relatório", key=f"report_{user_data['user_id']}", use_container_width=True)
            act_cols[3].button("Fechar Investigação", key=f"close_{user_data['user_id']}", use_container_width=True, on_click=close_case)

with ato4:
    st.header("Inteligência Estratégica e Análise Preditiva")
    col1, col2 = st.columns(2)
    with col1:
        with widget_container():
            st.subheader("Matriz de Perdas por Tipologia de Fraude")
            st.plotly_chart(create_fraud_heatmap(APP_THEME), use_container_width=True)
        with widget_container():
            st.subheader("Desempenho da Equipe de Prevenção")
            t1, t2, t3 = st.columns(3)
            t1.metric("Tempo Médio de Resolução", "12 min", "-3 min")
            t2.metric("Taxa de Falsos Positivos", "3.8%", "meta")
            t3.metric("Casos Resolvidos/Dia", "112", "+8%")
    with col2:
        with widget_container():
            st.subheader("Simulador de Políticas de Risco")
            threshold = st.slider("Score Mínimo para Bloqueio Automático de Saque", 700, 1000, 950, 10)
            impacto_fraude = (1000 - threshold) / 5 + 5
            impacto_falsos_positivos = (1000 - threshold) / 30
            s1, s2 = st.columns(2)
            s1.metric("Redução de Fraude Projetada", f"{impacto_fraude:.1f}%")
            s2.metric("Aumento de Falsos Positivos", f"{impacto_falsos_positivos:.1f}%", delta_color="inverse")
        with widget_container():
            st.subheader("Análise Preditiva de Risco de Eventos")
            st.plotly_chart(create_predictive_event_risk_chart(APP_THEME), use_container_width=True)
