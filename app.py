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

# Dicionários de tema para light e dark mode
LIGHT_THEME = {
    "primary": "#1976D2",
    "secondary": "#2196F3", 
    "danger": "#D32F2F",
    "warning": "#FF9800",
    "success": "#388E3C",
    "info": "#0288D1",
    "background": "#FAFAFA",
    "widget_background": "#FFFFFF",
    "secondary_background": "#F5F5F5",
    "text": "#212121",
    "text_secondary": "#424242",
    "subtle_text": "#757575",
    "grid": "#E0E0E0",
    "accent": "#7B1FA2",
    "highlight": "#F57C00"
}

DARK_THEME = {
    "primary": "#2196F3",
    "secondary": "#1976D2", 
    "danger": "#F44336",
    "warning": "#FF9800",
    "success": "#4CAF50",
    "info": "#00BCD4",
    "background": "#121212",
    "widget_background": "#1E1E1E",
    "secondary_background": "#2D2D2D",
    "text": "#FFFFFF",
    "text_secondary": "#B3B3B3",
    "subtle_text": "#8A8A8A",
    "grid": "#3D3D3D",
    "accent": "#9C27B0",
    "highlight": "#FF9800"
}

# Function to get current theme
def get_current_theme():
    # Initialize theme in session state if not exists
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    return DARK_THEME if st.session_state.dark_mode else LIGHT_THEME

# Set current theme
APP_THEME = get_current_theme()

# CSS Personalizado que utiliza as variáveis do tema
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {{
        --primary-color: {APP_THEME['primary']};
        --secondary-color: {APP_THEME['secondary']};
        --danger-color: {APP_THEME['danger']};
        --warning-color: {APP_THEME['warning']};
        --success-color: {APP_THEME['success']};
        --info-color: {APP_THEME['info']};
        --background-color: {APP_THEME['background']};
        --widget-background-color: {APP_THEME['widget_background']};
        --secondary-background: {APP_THEME['secondary_background']};
        --text-color: {APP_THEME['text']};
        --text-secondary: {APP_THEME['text_secondary']};
        --subtle-text-color: {APP_THEME['subtle_text']};
        --grid-color: {APP_THEME['grid']};
        --accent-color: {APP_THEME['accent']};
        --highlight-color: {APP_THEME['highlight']};
        --font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }}
    
    .stApp {{
        background-color: var(--background-color);
    }}
    
    .main {{
        padding: 1.5rem 1rem;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-family);
        font-weight: 600;
        color: var(--text-color);
    }}
    
    h1 {{
        color: var(--primary-color);
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }}
    
    .widget-container {{
        padding: 1.5rem;
        border-radius: 8px;
        background-color: var(--widget-background-color);
        border: 1px solid var(--grid-color);
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
        border-bottom: 2px solid var(--grid-color);
        padding: 0 1rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 15px;
        font-weight: 500;
        transition: all 0.3s ease;
        color: var(--text-secondary);
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="false"]:hover {{
        background-color: var(--secondary-background);
    }}
    
    .user-card {{
        border-left: 4px solid var(--subtle-text-color);
        padding: 1rem;
        margin-bottom: 0.8rem;
        background-color: var(--widget-background-color);
        border-radius: 6px;
        border: 1px solid var(--grid-color);
        transition: all 0.3s ease;
    }}
    
    .user-card:hover {{
        transform: translateX(3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    .user-card.high-risk {{
        border-left-color: var(--danger-color);
        background-color: rgba(211,47,47,0.05);
    }}
    
    .user-card.medium-risk {{
        border-left-color: var(--warning-color);
        background-color: rgba(255,152,0,0.05);
    }}
    
    .user-card.selected {{
        border-left-color: var(--primary-color);
        background-color: rgba(25,118,210,0.05);
        box-shadow: 0 0 10px rgba(25,118,210,0.3);
    }}
    
    .stButton > button {{
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }}
    
    .stButton > button[kind="primary"] {{
        background-color: var(--primary-color);
        color: white;
    }}
    
    .stButton > button[kind="secondary"] {{
        background-color: var(--secondary-background);
        color: var(--text-color);
        border: 1px solid var(--grid-color);
    }}
    
    .status-indicator {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }}
    
    .status-online {{
        background-color: var(--success-color);
    }}
    
    .status-warning {{
        background-color: var(--warning-color);
    }}
    
    .status-critical {{
        background-color: var(--danger-color);
    }}
    
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
        100% {{ opacity: 1; }}
    }}
    
    .stExpander > details > summary {{
        background-color: var(--secondary-background);
        border: 1px solid var(--grid-color);
        border-radius: 6px;
        padding: 0.8rem;
        font-weight: 500;
    }}
    
    .stProgress > div > div {{
        background-color: var(--primary-color);
        border-radius: 4px;
    }}
    
    hr {{
        border: none;
        height: 1px;
        background-color: var(--grid-color);
        margin: 1.5rem 0;
    }}
    
    /* Limpar alguns estilos indesejados */
    .stSelectbox > div > div {{
        background-color: var(--widget-background-color);
        border: 1px solid var(--grid-color);
        border-radius: 4px;
    }}
    
    .stSlider > div > div {{
        background-color: var(--grid-color);
    }}
    
    .stSlider > div > div > div {{
        background-color: var(--primary-color);
    }}
    
    /* Dark mode improvements */
    .stMarkdown, .stMarkdown p {{
        color: var(--text-color) !important;
    }}
    
    .stDataFrame {{
        background-color: var(--widget-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    .stSidebar {{
        background-color: var(--secondary-background) !important;
    }}
    
    /* Theme toggle button styling */
    .stButton > button[key="theme_toggle"] {{
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        color: white;
        border: none;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    
    .stButton > button[key="theme_toggle"]:hover {{
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }}
    
    /* Smooth transitions for theme changes */
    * {{
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
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

# --- Funções de Inteligência Avançada ---
def create_ml_model_performance_chart(theme):
    models = ['Fraud Detection V3', 'Account Takeover V2', 'Bonus Abuse V1', 'Velocity Check V4']
    accuracy = [94.2, 89.7, 91.5, 96.1]
    precision = [92.8, 87.3, 89.2, 94.7]
    recall = [91.4, 88.9, 90.1, 95.3]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=models, y=accuracy, mode='lines+markers', name='Accuracy', line=dict(color=theme['success'], width=3)))
    fig.add_trace(go.Scatter(x=models, y=precision, mode='lines+markers', name='Precision', line=dict(color=theme['primary'], width=3)))
    fig.add_trace(go.Scatter(x=models, y=recall, mode='lines+markers', name='Recall', line=dict(color=theme['warning'], width=3)))
    
    fig.update_layout(title="Performance dos Modelos ML", yaxis_title="Percentual (%)", xaxis_title="Modelos")
    return apply_theme_to_fig(fig, theme)

def create_real_time_transaction_flow(theme):
    timestamps = [datetime.now() - timedelta(minutes=i) for i in range(30, 0, -1)]
    transactions = np.random.poisson(150, 30)
    fraud_detected = np.random.poisson(8, 30)
    blocked = np.random.poisson(3, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=transactions, mode='lines', name='Transações Totais', 
                            line=dict(color=theme['primary'], width=2), fill='tonexty'))
    fig.add_trace(go.Scatter(x=timestamps, y=fraud_detected, mode='lines+markers', name='Fraudes Detectadas',
                            line=dict(color=theme['warning'], width=2), marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=timestamps, y=blocked, mode='lines+markers', name='Bloqueios Automáticos',
                            line=dict(color=theme['danger'], width=2), marker=dict(size=4)))
    
    fig.update_layout(title="Fluxo de Transações em Tempo Real", yaxis_title="Volume", xaxis_title="Timestamp")
    return apply_theme_to_fig(fig, theme)

def create_risk_score_distribution(theme):
    scores = np.random.beta(2, 5, 1000) * 1000  # Distribuição beta para simular scores realistas
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=scores, nbinsx=50, name='Distribuição de Scores',
                              marker_color=theme['primary'], opacity=0.7))
    
    # Adicionar linhas de threshold
    fig.add_vline(x=800, line_dash="dash", line_color=theme['warning'], 
                  annotation_text="Threshold Monitoramento")
    fig.add_vline(x=950, line_dash="dash", line_color=theme['danger'], 
                  annotation_text="Threshold Bloqueio")
    
    fig.update_layout(title="Distribuição de Risk Scores na População", 
                      xaxis_title="Risk Score", yaxis_title="Frequência")
    return apply_theme_to_fig(fig, theme)

def create_automated_actions_timeline(theme):
    hours = list(range(24))
    auto_blocks = [2, 1, 0, 1, 3, 8, 12, 15, 18, 22, 25, 28, 30, 35, 32, 28, 30, 35, 40, 38, 25, 15, 8, 4]
    manual_reviews = [5, 3, 2, 4, 6, 15, 25, 30, 35, 42, 48, 52, 55, 60, 58, 55, 60, 65, 70, 68, 45, 30, 15, 8]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hours, y=auto_blocks, name='Bloqueios Automáticos', 
                        marker_color=theme['danger'], opacity=0.8))
    fig.add_trace(go.Bar(x=hours, y=manual_reviews, name='Revisões Manuais', 
                        marker_color=theme['primary'], opacity=0.8))
    
    fig.update_layout(title="Ações Automatizadas vs Manuais (24h)", 
                      xaxis_title="Hora do Dia", yaxis_title="Quantidade de Ações",
                      barmode='stack')
    return apply_theme_to_fig(fig, theme)

def create_geographic_risk_heatmap(theme):
    # Simular dados de risco por estado brasileiro
    states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE', 'PA', 'MA', 'PB', 'ES', 'PI']
    risk_levels = np.random.uniform(0.1, 0.9, len(states))
    
    fig = go.Figure(data=go.Bar(
        x=states, y=risk_levels,
        marker=dict(color=risk_levels, colorscale='Reds', showscale=True),
        text=[f'{r:.1%}' for r in risk_levels],
        textposition='auto',
    ))
    
    fig.update_layout(title="Mapa de Calor de Risco por Estado", 
                      xaxis_title="Estados", yaxis_title="Nível de Risco")
    return apply_theme_to_fig(fig, theme)

def create_anomaly_detection_radar(theme):
    categories = ['Velocidade<br>Transações', 'Padrão<br>Geográfico', 'Comportamento<br>Apostas', 
                  'Uso de<br>Dispositivo', 'Horário<br>Atividade', 'Valor<br>Médio']
    
    # Usuário normal vs usuário suspeito
    normal_user = [0.2, 0.1, 0.3, 0.2, 0.4, 0.3]
    suspicious_user = [0.9, 0.8, 0.7, 0.95, 0.85, 0.9]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=normal_user + [normal_user[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Usuário Normal',
        line=dict(color=theme['success'])
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=suspicious_user + [suspicious_user[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Usuário Suspeito',
        line=dict(color=theme['danger'])
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        title="Radar de Detecção de Anomalias"
    )
    return apply_theme_to_fig(fig, theme)

def create_intervention_effectiveness_chart(theme):
    interventions = ['Bloqueio<br>Automático', 'Revisão<br>Manual', 'Monitoramento<br>Intensivo', 'Limite<br>Reduzido']
    effectiveness = [95.2, 89.7, 78.3, 82.1]
    volume = [245, 189, 432, 156]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=interventions, y=effectiveness, name='Efetividade (%)',
                        marker_color=theme['success'], yaxis='y'))
    fig.add_trace(go.Scatter(x=interventions, y=volume, mode='lines+markers',
                           name='Volume de Casos', line=dict(color=theme['primary'], width=3),
                           yaxis='y2'))
    
    fig.update_layout(
        title="Efetividade das Intervenções vs Volume",
        yaxis=dict(title="Efetividade (%)", side='left'),
        yaxis2=dict(title="Volume de Casos", side='right', overlaying='y')
    )
    return apply_theme_to_fig(fig, theme)


# ==============================================================================
# --- LAYOUT DA APLICAÇÃO ---
# ==============================================================================

# --- Inicialização do Estado da Sessão ---
if 'df_users' not in st.session_state:
    st.session_state.df_users, st.session_state.df_bets = generate_br_mock_data()
if 'selected_case_id' not in st.session_state:
    st.session_state.selected_case_id = None
if 'real_time_alerts' not in st.session_state:
    st.session_state.real_time_alerts = []
if 'automated_rules' not in st.session_state:
    st.session_state.automated_rules = {
        'auto_block_threshold': 950,
        'auto_monitoring_threshold': 800,
        'velocity_check_enabled': True,
        'device_fingerprint_enabled': True,
        'geo_anomaly_enabled': True
    }
if 'ml_predictions' not in st.session_state:
    st.session_state.ml_predictions = {
        'fraud_probability': np.random.uniform(0.1, 0.9, 10),
        'chargeback_risk': np.random.uniform(0.05, 0.8, 10),
        'account_takeover_risk': np.random.uniform(0.02, 0.7, 10)
    }
if 'live_transactions' not in st.session_state:
    st.session_state.live_transactions = []

# --- Cabeçalho ---
# Header with theme toggle
header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.title("GuardianAI: Plataforma de Análise de Risco")

with header_col2:
    # Theme toggle button
    theme_label = "🌙 Modo Escuro" if not st.session_state.dark_mode else "☀️ Modo Claro"
    if st.button(theme_label, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Adicionar estado para simular dados dinâmicos
if 'system_stats' not in st.session_state:
    st.session_state.system_stats = {
        'active_users': 12847,
        'transactions_per_min': 2456,
        'blocked_today': 127,
        'ml_accuracy': 94.7,
        'fraud_detected_today': 45
    }

# Sistema de Alertas em Tempo Real
alert_col1, alert_col2, alert_col3, alert_col4 = st.columns([1, 1, 1, 1])

with alert_col1:
    if st.button("ALERTA CRÍTICO", type="primary", use_container_width=True, key="critical_alert_btn"):
        # Simular detecção de anel de fraude
        new_fraud_ring = {
            'timestamp': datetime.now(),
            'level': 'CRÍTICO',
            'message': 'Anel de fraude detectado - 12 contas conectadas',
            'action_required': True,
            'users_affected': ['multi_acct_sp_1', 'multi_acct_sp_2', 'multi_acct_sp_3']
        }
        st.session_state.real_time_alerts.append(new_fraud_ring)
        
        # Atualizar estatísticas do sistema
        st.session_state.system_stats['fraud_detected_today'] += 12
        st.session_state.system_stats['blocked_today'] += 8
        
        st.error("ALERTA CRÍTICO: Anel de fraude multi-conta detectado!")
        st.markdown("**Ações Automáticas Executadas:**")
        st.markdown("- 8 contas bloqueadas automaticamente")
        st.markdown("- 4 contas movidas para monitoramento intensivo")
        st.markdown("- Equipe de investigação notificada")
        st.markdown("- Relatório preliminar gerado")

with alert_col2:
    if st.button("ALERTA MODERADO", use_container_width=True, key="moderate_alert_btn"):
        # Simular pico de transações anômalas
        anomaly_alert = {
            'timestamp': datetime.now(),
            'level': 'MODERADO',
            'message': 'Pico de transações anômalas detectado',
            'action_required': False
        }
        st.session_state.real_time_alerts.append(anomaly_alert)
        
        # Atualizar estatísticas
        st.session_state.system_stats['transactions_per_min'] += 340
        st.session_state.system_stats['fraud_detected_today'] += 3
        
        st.warning("ALERTA: Anomalia comportamental detectada")
        st.markdown("**Detalhes do Evento:**")
        st.markdown(f"- Aumento de {340} transações/min")
        st.markdown("- 3 usuários flagrados para revisão")
        st.markdown("- Thresholds de monitoramento ajustados")

with alert_col3:
    if st.button("EXECUTAR AUTOMAÇÃO", use_container_width=True, key="auto_action_btn"):
        # Simular execução de ações automáticas
        auto_blocks = np.random.randint(1, 6)
        auto_monitors = np.random.randint(3, 12)
        processed_transactions = np.random.randint(1200, 1500)
        
        st.session_state.system_stats['blocked_today'] += auto_blocks
        st.session_state.system_stats['transactions_per_min'] = processed_transactions
        
        st.success(f"Sistema executou {auto_blocks} bloqueios automáticos")
        st.info(f"Processadas {processed_transactions} transações via ML")
        st.markdown("**Resultados da Automação:**")
        st.markdown(f"- {auto_blocks} contas bloqueadas por score crítico")
        st.markdown(f"- {auto_monitors} usuários em monitoramento")
        st.markdown("- Modelos ML atualizados com novos dados")

with alert_col4:
    status_color = "status-online" if len(st.session_state.real_time_alerts) < 5 else "status-warning" if len(st.session_state.real_time_alerts) < 10 else "status-critical"
    st.markdown(f'<span class="status-indicator {status_color}"></span><strong>SISTEMA ONLINE</strong>', unsafe_allow_html=True)
    st.metric("Alertas Ativos", len(st.session_state.real_time_alerts), 
              "↗ Crescendo" if len(st.session_state.real_time_alerts) > 3 else "Estável")

# Painel de Controle Rápido
with st.expander("Centro de Comando e Controle", expanded=False):
    control_cols = st.columns([2, 2, 2, 2])
    
    with control_cols[0]:
        st.subheader("Controles de Bloqueio")
        emergency_threshold = st.slider("Threshold de Emergência", 800, 1000, 
                                       st.session_state.automated_rules['auto_block_threshold'], 10,
                                       key="emergency_threshold_slider")
        if st.button("PARAR TODAS TRANSAÇÕES", type="primary", key="emergency_stop_btn"):
            st.session_state.emergency_mode = True
            st.session_state.system_stats['transactions_per_min'] = 0
            st.error("MODO EMERGÊNCIA ATIVADO")
            st.markdown("**Ações Executadas:**")
            st.markdown("- Todas as transações pausadas")
            st.markdown("- Equipe de emergência notificada")
            st.markdown("- Log de auditoria atualizado")
    
    with control_cols[1]:
        st.subheader("Monitoramento Avançado")
        monitoring_threshold = st.slider("Threshold Monitoramento", 600, 900, 
                                        st.session_state.automated_rules['auto_monitoring_threshold'], 10,
                                        key="monitoring_threshold_slider")
        if st.button("VARREDURA COMPLETA", key="full_scan_btn"):
            st.info("Iniciando varredura completa da base de usuários...")
            progress = st.progress(0)
            
            # Simular varredura realista
            stages = [
                "Carregando base de usuários...",
                "Analisando padrões comportamentais...",
                "Executando modelos de ML...",
                "Correlacionando dados de risco...",
                "Gerando relatório final..."
            ]
            
            for i in range(100):
                if i % 20 == 0 and i // 20 < len(stages):
                    st.text(stages[i // 20])
                progress.progress(i + 1)
            
            # Atualizar estatísticas baseadas na varredura
            suspicious_found = np.random.randint(8, 25)
            high_risk_found = np.random.randint(2, 8)
            st.session_state.system_stats['fraud_detected_today'] += suspicious_found
            
            st.success(f"Varredura completa finalizada")
            st.markdown(f"**Resultados:**")
            st.markdown(f"- {suspicious_found} casos suspeitos identificados")
            st.markdown(f"- {high_risk_found} usuários movidos para alto risco")
            st.markdown(f"- {np.random.randint(50, 200)} perfis atualizados")
    
    with control_cols[2]:
        st.subheader("Automação e IA")
        auto_mode = st.checkbox("Modo Automático", value=True, key="auto_mode_check")
        velocity_check = st.checkbox("Velocity Check", 
                                   value=st.session_state.automated_rules['velocity_check_enabled'],
                                   key="velocity_check_box")
        device_fingerprint = st.checkbox("Device Fingerprint", 
                                       value=st.session_state.automated_rules['device_fingerprint_enabled'],
                                       key="device_fingerprint_check")
        geo_anomaly = st.checkbox("Anomalia Geográfica", 
                                value=st.session_state.automated_rules['geo_anomaly_enabled'],
                                key="geo_anomaly_check")
        
        # Atualizar regras
        st.session_state.automated_rules.update({
            'auto_block_threshold': emergency_threshold,
            'auto_monitoring_threshold': monitoring_threshold,
            'velocity_check_enabled': velocity_check,
            'device_fingerprint_enabled': device_fingerprint,
            'geo_anomaly_enabled': geo_anomaly
        })
        
        # Mostrar impacto das configurações
        active_modules = sum([velocity_check, device_fingerprint, geo_anomaly])
        detection_improvement = active_modules * 3.2
        st.info(f"Melhoria na detecção: +{detection_improvement:.1f}%")
    
    with control_cols[3]:
        st.subheader("Status do Sistema")
        current_stats = st.session_state.system_stats
        
        st.metric("Usuários Ativos", 
                 f"{current_stats['active_users']:,}",
                 f"+{np.random.randint(150, 400)}")
        st.metric("Transações/min", 
                 f"{current_stats['transactions_per_min']:,}",
                 f"{'PAUSADO' if st.session_state.get('emergency_mode') else 'Normal'}")
        st.metric("Acurácia ML", 
                 f"{current_stats['ml_accuracy']:.1f}%",
                 f"+{np.random.uniform(0.1, 0.5):.1f}%")
        
        if st.button("NOTIFICAR EQUIPE", key="notify_team_btn"):
            analysts_count = np.random.randint(5, 12)
            st.success(f"Notificações enviadas para {analysts_count} analistas")
            st.markdown("**Canais utilizados:**")
            st.markdown("- Slack: 8 analistas")
            st.markdown("- Email: Todos")
            st.markdown("- SMS: Supervisores")

# Log de Alertas Recentes
if st.session_state.real_time_alerts:
    with st.expander("Log de Alertas e Eventos", expanded=False):
        st.subheader("Últimos 5 Eventos do Sistema")
        for alert in reversed(st.session_state.real_time_alerts[-5:]):
            level_color = "danger" if alert['level'] == 'CRÍTICO' else "warning" if alert['level'] == 'MODERADO' else "info"
            timestamp_str = alert['timestamp'].strftime('%H:%M:%S')
            
            if level_color == "danger":
                st.error(f"**{alert['level']}** - {timestamp_str} - {alert['message']}")
            elif level_color == "warning":
                st.warning(f"**{alert['level']}** - {timestamp_str} - {alert['message']}")
            else:
                st.info(f"**{alert['level']}** - {timestamp_str} - {alert['message']}")

# Rodapé com informações do sistema
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    st.caption(f"Dados atualizados em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
with col_footer2:
    st.caption("Sistema GuardianAI v2.1.4")
with col_footer3:
    uptime_days = (datetime.now() - datetime.now().replace(day=1)).days
    st.caption(f"Uptime: {uptime_days} dias")

# --- Abas Principais ---
ato1, ato2, ato3, ato4 = st.tabs(["Ato I: Pulso da Operação", "Ato II: Vigília Constante", "Ato III: Sala de Investigação", "Ato IV: Inteligência Estratégica"])

with ato1:
    st.header("Visão Geral e Saúde da Plataforma")
    
    # Primeira linha - Métricas principais
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with widget_container():
            st.plotly_chart(create_global_risk_score_gauge(APP_THEME), use_container_width=True)
        with widget_container():
            st.subheader("KPIs Financeiros de Risco")
            kp1, kp2, kp3 = st.columns(3)
            kp1.metric("GGR em Risco (24h)", "R$ 92.580", "-8%")
            kp2.metric("Fraudes Prevenidas (Mês)", "R$ 4.8M", "+12%")
            kp3.metric("ROI da Prevenção", "1,847%", "🎯")
    with col2:
        with widget_container():
            st.subheader("Atividade e Risco Geográfico")
            st.plotly_chart(create_risk_map_br(APP_THEME), use_container_width=True)
    
    # Segunda linha - Gráficos avançados
    col3, col4 = st.columns(2)
    with col3:
        with widget_container():
            st.subheader("Principais Ameaças Ativas")
            st.plotly_chart(create_top_threats_chart(APP_THEME), use_container_width=True)
    with col4:
        with widget_container():
            st.subheader("Distribuição de Risk Scores")
            st.plotly_chart(create_risk_score_distribution(APP_THEME), use_container_width=True)
    
    # Terceira linha - Monitoramento em tempo real
    col5, col6 = st.columns(2)
    with col5:
        with widget_container():
            st.subheader("Fluxo de Transações (Tempo Real)")
            st.plotly_chart(create_real_time_transaction_flow(APP_THEME), use_container_width=True)
    with col6:
        with widget_container():
            st.subheader("Mapa de Calor por Estado")
            st.plotly_chart(create_geographic_risk_heatmap(APP_THEME), use_container_width=True)
    
    # Quarta linha - Inteligência operacional
    with widget_container():
        st.subheader("Timeline de Ações Automatizadas vs Manuais")
        st.plotly_chart(create_automated_actions_timeline(APP_THEME), use_container_width=True)
    
    # Controles operacionais rápidos
    with widget_container():
        st.subheader("Controles Operacionais Avançados")
        quick_cols = st.columns(5)
        
        with quick_cols[0]:
            if st.button("MODO ALTO RISCO", use_container_width=True, key="high_risk_mode_btn"):
                # Simular ativação do modo alto risco
                st.session_state.automated_rules['auto_block_threshold'] = 850
                st.session_state.automated_rules['auto_monitoring_threshold'] = 700
                
                st.warning("MODO ALTO RISCO ATIVADO")
                st.markdown("**Configurações Aplicadas:**")
                st.markdown("- Threshold de bloqueio: 950 → 850")
                st.markdown("- Threshold de monitoramento: 800 → 700")
                st.markdown("- Sensibilidade aumentada em 40%")
                st.markdown("- Analistas de plantão notificados")
        
        with quick_cols[1]:
            if st.button("EXECUTAR ML BATCH", use_container_width=True, key="ml_batch_btn"):
                with st.spinner("Processando lote de análise..."):
                    # Simular processamento ML realista
                    progress_bar = st.progress(0)
                    
                    stages = [
                        "Preparando dataset...",
                        "Executando feature engineering...", 
                        "Aplicando modelos de classificação...",
                        "Calculando scores de risco...",
                        "Atualizando base de dados..."
                    ]
                    
                    for i in range(100):
                        if i % 20 == 0 and i // 20 < len(stages):
                            st.text(stages[i // 20])
                        progress_bar.progress(i + 1)
                    
                    # Simular resultados
                    users_processed = np.random.randint(2500, 3200)
                    high_risk_found = np.random.randint(45, 89)
                    model_accuracy = np.random.uniform(93.5, 96.2)
                    
                    st.session_state.system_stats['ml_accuracy'] = model_accuracy
                    st.session_state.system_stats['fraud_detected_today'] += high_risk_found
                    
                    st.success("Processamento ML Finalizado")
                    st.markdown("**Resultados:**")
                    st.markdown(f"- {users_processed:,} usuários analisados")
                    st.markdown(f"- {high_risk_found} casos de alto risco identificados")
                    st.markdown(f"- Acurácia do modelo: {model_accuracy:.2f}%")
                    st.markdown(f"- Tempo de processamento: {np.random.uniform(45, 120):.1f} segundos")
        
        with quick_cols[2]:
            if st.button("RELATÓRIO EXECUTIVO", use_container_width=True, key="exec_report_btn"):
                # Simular geração de relatório executivo
                with st.spinner("Compilando relatório executivo..."):
                    progress = st.progress(0)
                    for i in range(100):
                        progress.progress(i + 1)
                
                report_data = {
                    'total_fraud_prevented': f"R$ {np.random.randint(4500, 6200) * 1000:,}",
                    'cases_resolved': np.random.randint(1200, 1800),
                    'accuracy_improvement': np.random.uniform(2.1, 4.8),
                    'cost_savings': f"R$ {np.random.randint(180, 340) * 1000:,}"
                }
                
                st.success("Relatório Executivo Gerado")
                st.markdown("**Resumo Gerencial:**")
                st.markdown(f"- Fraudes prevenidas: {report_data['total_fraud_prevented']}")
                st.markdown(f"- Casos resolvidos: {report_data['cases_resolved']:,}")
                st.markdown(f"- Melhoria na acurácia: +{report_data['accuracy_improvement']:.1f}%")
                st.markdown(f"- Economia operacional: {report_data['cost_savings']}")
                st.info("Relatório enviado para: C-Level, Diretoria de Risco, Gerentes")
        
        with quick_cols[3]:
            if st.button("VERIFICAR GEO-BLOCKS", use_container_width=True, key="geo_blocks_btn"):
                # Simular verificação de bloqueios geográficos
                geo_blocks = {
                    'Venezuela': np.random.randint(8, 18),
                    'Colômbia': np.random.randint(3, 12),
                    'Paraguai': np.random.randint(1, 7),
                    'Bolívia': np.random.randint(0, 5)
                }
                
                total_blocked = sum(geo_blocks.values())
                st.session_state.system_stats['blocked_today'] += total_blocked
                
                st.success("Verificação de Geo-blocks Concluída")
                st.markdown("**Países com Bloqueios Ativos:**")
                for country, blocks in geo_blocks.items():
                    if blocks > 0:
                        st.markdown(f"- {country}: {blocks} bloqueios")
                
                st.markdown("**Análise de Risco por Região:**")
                st.markdown("- América do Sul: Risco Elevado")
                st.markdown("- Regiões de fronteira: Monitoramento intensivo")
                st.markdown(f"- Total de IPs bloqueados hoje: {total_blocked}")
        
        with quick_cols[4]:
            if st.button("OTIMIZAR REGRAS IA", use_container_width=True, key="optimize_rules_btn"):
                # Simular otimização de regras via IA
                with st.spinner("Executando algoritmo de otimização..."):
                    progress = st.progress(0)
                    optimization_steps = [
                        "Analisando performance histórica...",
                        "Identificando gargalos...",
                        "Calculando novos thresholds...",
                        "Validando otimizações...",
                        "Aplicando melhorias..."
                    ]
                    
                    for i in range(100):
                        if i % 20 == 0 and i // 20 < len(optimization_steps):
                            st.text(optimization_steps[i // 20])
                        progress.progress(i + 1)
                
                # Simular resultados da otimização
                improvements = {
                    'false_positive_reduction': np.random.uniform(12, 28),
                    'detection_improvement': np.random.uniform(8, 18),
                    'processing_speed': np.random.uniform(15, 35),
                    'cost_efficiency': np.random.uniform(18, 32)
                }
                
                st.success("Otimização IA Finalizada")
                st.markdown("**Melhorias Implementadas:**")
                st.markdown(f"- Redução de falsos positivos: -{improvements['false_positive_reduction']:.1f}%")
                st.markdown(f"- Melhoria na detecção: +{improvements['detection_improvement']:.1f}%") 
                st.markdown(f"- Aumento velocidade: +{improvements['processing_speed']:.1f}%")
                st.markdown(f"- Eficiência de custo: +{improvements['cost_efficiency']:.1f}%")
                st.info("Novas regras ativadas automaticamente")

with ato2:
    st.header("Monitoramento em Tempo Real e Alertas")
    
    # Painel de controle superior
    with widget_container():
        st.subheader("🚨 Centro de Alertas e Automação")
        alert_cols = st.columns(4)
        
        with alert_cols[0]:
            if st.button("🔔 Criar Alerta Personalizado", use_container_width=True):
                alert_type = st.selectbox("Tipo de Alerta", ["Score Alto", "Geo Anomalia", "Velocity", "Device"])
                threshold = st.number_input("Threshold", min_value=1, max_value=1000, value=900)
                if st.button("Criar"):
                    st.success(f"✅ Alerta {alert_type} criado com threshold {threshold}")
        
        with alert_cols[1]:
            if st.button("🤖 Treinar Modelo", use_container_width=True):
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                st.success("🧠 Modelo ML retreinado com novos dados")
        
        with alert_cols[2]:
            if st.button("📡 Sincronizar Sistemas", use_container_width=True):
                st.info("📡 Sincronizando com sistemas externos...")
                st.success("✅ PIX, TED, e Cartões sincronizados")
        
        with alert_cols[3]:
            if st.button("💾 Backup Configurações", use_container_width=True):
                st.success("💾 Backup realizado: config_backup_" + datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    col1, col2 = st.columns([1.5, 2])
    with col1:
        st.subheader("🔍 Fila de Investigação Inteligente")
        
        # Filtros avançados
        with st.expander("🎯 Filtros Inteligentes", expanded=False):
            risk_filter = st.selectbox("Filtrar por Risco", ["Todos", "Crítico (900+)", "Alto (800+)", "Médio (600+)"])
            fraud_type_filter = st.selectbox("Tipo de Fraude", ["Todos", "Anel de Fraude", "CPF", "Chargeback", "Bônus"])
            auto_action = st.checkbox("Ação Automática Habilitada")
        
        # Aplicar filtros
        filtered_cases = st.session_state.df_users[st.session_state.df_users['status'] == 'active']
        if risk_filter != "Todos":
            threshold = int(risk_filter.split('(')[1].split('+')[0])
            filtered_cases = filtered_cases[filtered_cases['risk_score'] >= threshold]
        
        high_risk_cases = filtered_cases.sort_values("risk_score", ascending=False)
        
        for _, row in high_risk_cases.iterrows():
            risk_level = "high-risk" if row['risk_score'] > 800 else "medium-risk"
            is_selected = row['user_id'] == st.session_state.selected_case_id
            card_class = f"user-card {risk_level}{' selected' if is_selected else ''}"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            # Cabeçalho do card mais detalhado
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**Usuário:** `{row['user_id']}` | **Score:** {row['risk_score']}")
                st.markdown(f"<small style='color:var(--subtle-text-color)'>Fator de Risco: {row['main_risk_factor']}</small>", unsafe_allow_html=True)
            with col_b:
                urgency_class = "status-critical" if row['risk_score'] > 900 else "status-warning" if row['risk_score'] > 800 else "status-online"
                urgency_text = "CRÍTICO" if row['risk_score'] > 900 else "ALTO" if row['risk_score'] > 800 else "MODERADO"
                st.markdown(f'<div style="text-align: center;"><span class="status-indicator {urgency_class}"></span><strong>{urgency_text}</strong></div>', unsafe_allow_html=True)
            
            # Botões de ação
            action_cols = st.columns(3)
            with action_cols[0]:
                if st.button("INVESTIGAR", key=f"investigate_{row['user_id']}", type="primary", use_container_width=True):
                    st.session_state.selected_case_id = row['user_id']
                    st.rerun()
            with action_cols[1]:
                if st.button("BLOQUEAR", key=f"quick_block_{row['user_id']}", use_container_width=True):
                    # Simular bloqueio com detalhes realistas
                    st.session_state.system_stats['blocked_today'] += 1
                    block_time = datetime.now().strftime('%H:%M:%S')
                    
                    st.error(f"USUÁRIO {row['user_id']} BLOQUEADO")
                    st.markdown("**Ações Executadas:**")
                    st.markdown(f"- Conta suspensa às {block_time}")
                    st.markdown("- Transações pendentes canceladas")
                    st.markdown("- Saldo bloqueado para análise")
                    st.markdown("- Notificação enviada ao usuário")
                    
            with action_cols[2]:
                if st.button("MONITORAR", key=f"quick_monitor_{row['user_id']}", use_container_width=True):
                    # Simular ativação de monitoramento
                    monitoring_level = "INTENSIVO" if row['risk_score'] > 900 else "MODERADO"
                    
                    st.warning(f"MONITORAMENTO {monitoring_level} ATIVADO")
                    st.markdown("**Configurações de Monitoramento:**")
                    st.markdown(f"- Nível: {monitoring_level}")
                    st.markdown("- Alertas automáticos: Habilitados")
                    st.markdown("- Frequency: Tempo real")
                    st.markdown("- Duração: 48h (renovável)")
            
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("Painéis de Análise em Tempo Real")
        
        with st.expander("Análise de Contas Novas ('Laranjômetro')", expanded=True):
            with widget_container():
                gauge_col, controls_col = st.columns([2, 1])
                with gauge_col:
                    st.plotly_chart(create_laranjometro_gauge(APP_THEME), use_container_width=True)
                with controls_col:
                    if st.button("ATUALIZAR DADOS", key="update_laranja_btn"):
                        # Simular atualização de dados
                        new_accounts_hour = np.random.randint(180, 280)
                        temp_emails_pct = np.random.uniform(14, 25)
                        conversion_rate = np.random.uniform(60, 75)
                        
                        st.success("Dados atualizados com sucesso")
                        st.markdown("**Novos Dados:**")
                        st.markdown(f"- Contas/hora: {new_accounts_hour}")
                        st.markdown(f"- E-mails temp: {temp_emails_pct:.1f}%")
                        st.markdown(f"- Conversão: {conversion_rate:.1f}%")
                        
                    if st.button("CALIBRAR MODELO", key="calibrate_laranja_btn"):
                        # Simular recalibração do modelo
                        with st.spinner("Recalibrando modelo..."):
                            progress = st.progress(0)
                            for i in range(100):
                                progress.progress(i + 1)
                        
                        accuracy_improvement = np.random.uniform(2.3, 5.8)
                        st.info("Modelo recalibrado com sucesso")
                        st.markdown(f"**Melhorias:**")
                        st.markdown(f"- Acurácia: +{accuracy_improvement:.1f}%")
                        st.markdown("- Novos padrões integrados")
                        st.markdown("- Thresholds otimizados")
                
                metrics_cols = st.columns(3)
                metrics_cols[0].metric("Velocidade de Criação (hora)", "210 contas", "+45%")
                metrics_cols[1].metric("E-mails Temporários", "18%", "ALERTA")
                metrics_cols[2].metric("Conversão Primeiro Depósito", "67%", "+3%")
        
        with st.expander("Detector de Padrões de Apostas Anômalas", expanded=True):
            with widget_container():
                st.plotly_chart(create_bet_pattern_scatter(APP_THEME), use_container_width=True)
                
                anomaly_cols = st.columns(4)
                with anomaly_cols[0]:
                    if st.button("DETECTAR ANOMALIAS", key="detect_anomalies_btn"):
                        # Simular detecção de anomalias em tempo real
                        anomalies_found = np.random.randint(12, 25)
                        risk_level = "ALTA" if anomalies_found > 18 else "MÉDIA"
                        
                        st.error(f"ALERTA: {anomalies_found} apostas anômalas detectadas")
                        st.markdown("**Detalhes da Análise:**")
                        st.markdown(f"- Período: Últimas 2 horas")
                        st.markdown(f"- Severidade: {risk_level}")
                        st.markdown(f"- Padrões identificados: {np.random.randint(3, 7)}")
                        st.markdown(f"- Contas flagradas: {np.random.randint(8, 15)}")
                        
                with anomaly_cols[1]:
                    if st.button("AJUSTAR SENSIBILIDADE", key="adjust_sensitivity_btn"):
                        sensitivity = st.slider("Sensibilidade do Detector", 1, 10, 7, key="sensitivity_slider")
                        
                        # Simular impacto do ajuste
                        detection_change = (sensitivity - 7) * 3.2
                        false_positive_change = (sensitivity - 7) * 1.8
                        
                        st.info(f"Sensibilidade ajustada para {sensitivity}")
                        st.markdown("**Impacto Estimado:**")
                        st.markdown(f"- Detecção: {'+' if detection_change > 0 else ''}{detection_change:.1f}%")
                        st.markdown(f"- Falsos positivos: {'+' if false_positive_change > 0 else ''}{false_positive_change:.1f}%")
                        
                with anomaly_cols[2]:
                    current_anomalies = st.session_state.system_stats.get('anomalies_per_hour', 8.3)
                    st.metric("Apostas Anômalas/h", f"{current_anomalies}", "+15%")
                with anomaly_cols[3]:
                    detection_rate = st.session_state.system_stats.get('detection_accuracy', 94.2)
                    st.metric("Taxa de Acerto", f"{detection_rate:.1f}%", "ALTA")
        
        with st.expander("Monitor Inteligente de Bônus e Promoções", expanded=True):
            with widget_container():
                st.plotly_chart(create_bonus_monitor_chart(APP_THEME), use_container_width=True)
                
                bonus_controls = st.columns(4)
                with bonus_controls[0]:
                    if st.button("ATIVAR PROTEÇÃO", key="activate_bonus_protection_btn"):
                        # Simular ativação de proteção anti-abuso
                        protection_rules = np.random.randint(8, 15)
                        blocked_attempts = np.random.randint(12, 28)
                        
                        st.success("Proteção anti-abuso ativada")
                        st.markdown("**Sistema de Proteção:**")
                        st.markdown(f"- {protection_rules} regras ativadas")
                        st.markdown(f"- {blocked_attempts} tentativas bloqueadas")
                        st.markdown("- Monitoramento: Tempo real")
                        st.markdown("- Cobertura: Todas as campanhas")
                        
                with bonus_controls[1]:
                    if st.button("ANÁLISE CONVERSÃO", key="conversion_analysis_btn"):
                        # Simular análise de conversão
                        with st.spinner("Analisando campanhas de bônus..."):
                            progress = st.progress(0)
                            for i in range(100):
                                progress.progress(i + 1)
                        
                        campaigns_analyzed = np.random.randint(8, 15)
                        conversion_avg = np.random.uniform(45, 75)
                        best_campaign = np.random.choice(['Boas-Vindas', 'Recarga FDS', 'Free Bet'])
                        
                        st.info("Análise de conversão finalizada")
                        st.markdown("**Resultados:**")
                        st.markdown(f"- Campanhas analisadas: {campaigns_analyzed}")
                        st.markdown(f"- Conversão média: {conversion_avg:.1f}%")
                        st.markdown(f"- Melhor performance: {best_campaign}")
                        
                with bonus_controls[2]:
                    abuse_rate = st.session_state.system_stats.get('bonus_abuse_rate', 5.2)
                    st.metric("Abuso Detectado", f"{abuse_rate:.1f}%", "-2%")
                with bonus_controls[3]:
                    savings = st.session_state.system_stats.get('bonus_savings', 23400)
                    st.metric("Economia Estimada", f"R$ {savings/1000:.1f}K", "ALTA")
        
        with st.expander("Radar de Detecção de Anomalias (ML)", expanded=True):
            with widget_container():
                st.plotly_chart(create_anomaly_detection_radar(APP_THEME), use_container_width=True)
                
                radar_controls = st.columns(3)
                with radar_controls[0]:
                    if st.button("ANÁLISE COMPLETA", key="full_analysis_radar_btn"):
                        # Simular análise ML completa
                        with st.spinner("Executando análise comportamental..."):
                            progress = st.progress(0)
                            analysis_steps = [
                                "Coletando dados comportamentais...",
                                "Aplicando algoritmos de ML...",
                                "Identificando padrões anômalos...",
                                "Correlacionando variáveis...",
                                "Gerando relatório de anomalias..."
                            ]
                            
                            for i in range(100):
                                if i % 20 == 0 and i // 20 < len(analysis_steps):
                                    st.text(analysis_steps[i // 20])
                                progress.progress(i + 1)
                        
                        suspicious_users = np.random.randint(8, 18)
                        anomaly_score_avg = np.random.uniform(0.75, 0.92)
                        patterns_found = np.random.randint(4, 9)
                        
                        st.success("Análise comportamental finalizada")
                        st.markdown("**Resultados da Análise:**")
                        st.markdown(f"- Usuários suspeitos: {suspicious_users}")
                        st.markdown(f"- Score médio de anomalia: {anomaly_score_avg:.2f}")
                        st.markdown(f"- Padrões identificados: {patterns_found}")
                        st.markdown("- Recomendação: Investigação manual")
                        
                with radar_controls[1]:
                    threshold_radar = st.slider("Threshold de Anomalia", 0.1, 1.0, 0.7, 0.1, key="radar_threshold_slider")
                    
                    # Mostrar impacto do threshold
                    sensitivity_level = "ALTA" if threshold_radar < 0.5 else "MÉDIA" if threshold_radar < 0.8 else "BAIXA"
                    expected_alerts = int((1 - threshold_radar) * 50)
                    
                    st.info(f"Sensibilidade: {sensitivity_level}")
                    st.markdown(f"**Impacto Estimado:**")
                    st.markdown(f"- Threshold: {threshold_radar}")
                    st.markdown(f"- Alertas esperados: ~{expected_alerts}/dia")
                    st.markdown(f"- Precisão estimada: {85 + threshold_radar * 10:.1f}%")
                    
                with radar_controls[2]:
                    if st.button("SALVAR CONFIG", key="save_radar_config_btn"):
                        # Simular salvamento de configuração
                        config_id = np.random.randint(1000, 9999)
                        
                        st.success("Configuração salva")
                        st.markdown("**Configuração Salva:**")
                        st.markdown(f"- ID da configuração: #{config_id}")
                        st.markdown(f"- Threshold: {threshold_radar}")
                        st.markdown(f"- Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                        st.markdown("- Status: Ativo em produção")

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
            
            # Inicializar estados de sessão para as ações
            if f"account_blocked_{user_data['user_id']}" not in st.session_state:
                st.session_state[f"account_blocked_{user_data['user_id']}"] = False
            if f"is_monitoring_{user_data['user_id']}" not in st.session_state:
                st.session_state[f"is_monitoring_{user_data['user_id']}"] = False
            if f"report_generated_{user_data['user_id']}" not in st.session_state:
                st.session_state[f"report_generated_{user_data['user_id']}"] = False
            
            def close_case():
                st.session_state.selected_case_id = None
                st.success("✅ Investigação encerrada com sucesso!")
            
            def block_account():
                st.session_state[f"account_blocked_{user_data['user_id']}"] = True
                st.error("🚫 Conta bloqueada! Todas as operações foram suspensas.")
                st.balloons()
            
            def start_monitoring():
                st.session_state[f"is_monitoring_{user_data['user_id']}"] = True
                st.warning("👁️ Monitoramento ativo! Alertas automáticos configurados.")
            
            def generate_report():
                st.session_state[f"report_generated_{user_data['user_id']}"] = True
                st.success("📋 Relatório gerado! Dados bancários e comportamentais compilados.")
            
            act_cols = st.columns([1.5, 1.5, 1.5, 2])
            
            # Botão Bloquear Conta
            is_blocked = st.session_state[f"account_blocked_{user_data['user_id']}"]
            block_label = "🚫 Conta Bloqueada" if is_blocked else "Bloquear Conta"
            if act_cols[0].button(block_label, key=f"block_{user_data['user_id']}", 
                                  type="secondary" if is_blocked else "primary", 
                                  use_container_width=True, disabled=is_blocked):
                block_account()
            
            # Botão Monitorar
            is_monitoring = st.session_state[f"is_monitoring_{user_data['user_id']}"]
            monitor_label = "👁️ Monitorando" if is_monitoring else "Monitorar"
            if act_cols[1].button(monitor_label, key=f"monitor_{user_data['user_id']}", 
                                  use_container_width=True, disabled=is_monitoring):
                start_monitoring()
            
            # Botão Gerar Relatório
            report_generated = st.session_state[f"report_generated_{user_data['user_id']}"]
            if act_cols[2].button("Gerar Relatório", key=f"report_{user_data['user_id']}", 
                                  use_container_width=True):
                generate_report()
            
            # Botão Fechar Investigação
            act_cols[3].button("Fechar Investigação", key=f"close_{user_data['user_id']}", 
                              use_container_width=True, on_click=close_case)
            
            # Exibir relatório mockado se foi gerado
            if report_generated:
                st.markdown("---")
                st.subheader("📋 Relatório de Investigação Gerado")
                
                with st.expander("Ver Relatório Completo", expanded=True):
                    report_cols = st.columns(2)
                    
                    with report_cols[0]:
                        st.markdown("**📊 Dados Comportamentais**")
                        st.markdown(f"""
                        - **Usuário ID:** {user_data['user_id']}
                        - **Score de Risco:** {user_data['risk_score']}/1000
                        - **Fator Principal:** {user_data['main_risk_factor']}
                        - **Tempo Total de Sessão:** {user_data['session_time_sec']}s
                        - **Valor Médio das Apostas:** R$ {user_data['avg_bet_value']:.2f}
                        - **Grupo de Pares:** {user_data['peer_group']}
                        """)
                        
                        st.markdown("**🏦 Dados Bancários (Mock)**")
                        mock_account = f"0001-{np.random.randint(10000, 99999)}"
                        mock_bank = np.random.choice(['Banco do Brasil', 'Itaú', 'Bradesco', 'Santander'])
                        mock_agency = f"{np.random.randint(1000, 9999)}-{np.random.randint(0, 9)}"
                        st.markdown(f"""
                        - **Banco:** {mock_bank}
                        - **Agência:** {mock_agency}
                        - **Conta:** {mock_account}
                        - **CPF:** ***.{np.random.randint(100, 999)}.***-**
                        - **Status:** {'🚫 Bloqueado' if is_blocked else '✅ Ativo'}
                        """)
                    
                    with report_cols[1]:
                        st.markdown("**🌍 Dados Técnicos**")
                        st.markdown(f"""
                        - **Device ID:** {user_data['device_id']}
                        - **IP/ASN:** {user_data['ip_asn']}
                        - **Localização:** {user_data['state']}, Brasil
                        - **Método Pagamento:** {user_data['payment_type']}
                        - **ID Pagamento:** {user_data['payment_method_id']}
                        """)
                        
                        st.markdown("**⚠️ Alertas e Ações**")
                        alerts = []
                        if is_blocked:
                            alerts.append("🚫 Conta bloqueada por suspeita de fraude")
                        if is_monitoring:
                            alerts.append("👁️ Monitoramento ativo configurado")
                        if user_data['risk_score'] > 900:
                            alerts.append("🔴 Score de risco crítico")
                        if "Anel de Fraude" in user_data['main_risk_factor']:
                            alerts.append("🔗 Possível conexão com rede fraudulenta")
                        
                        for alert in alerts:
                            st.markdown(f"- {alert}")
                    
                    st.markdown("**📅 Relatório gerado em:** " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                    
                    # Botão para download do relatório (simulado)
                    if st.button("💾 Baixar Relatório (PDF)", use_container_width=True):
                        st.success("📄 Relatório baixado com sucesso! (Funcionalidade simulada)")
            
            # Status das ações tomadas
            if is_blocked or is_monitoring or report_generated:
                st.markdown("---")
                st.subheader("📋 Status das Ações")
                status_cols = st.columns(3)
                
                with status_cols[0]:
                    if is_blocked:
                        st.error("🚫 Conta Bloqueada")
                    else:
                        st.info("✅ Conta Ativa")
                
                with status_cols[1]:
                    if is_monitoring:
                        st.warning("👁️ Em Monitoramento")
                    else:
                        st.info("💤 Sem Monitoramento")
                
                with status_cols[2]:
                    if report_generated:
                        st.success("📋 Relatório Gerado")
                    else:
                        st.info("📋 Sem Relatório")

with ato4:
    st.header("Inteligência Estratégica e Análise Preditiva")
    
    # Painel de inteligência estratégica
    with widget_container():
        st.subheader("🧠 Centro de Inteligência Artificial e Machine Learning")
        intelligence_cols = st.columns(4)
        
        with intelligence_cols[0]:
            if st.button("🚀 Executar Predição Batch", use_container_width=True):
                progress = st.progress(0)
                for i in range(100):
                    progress.progress(i + 1)
                st.success("🚀 Predições para 50K usuários concluídas")
        
        with intelligence_cols[1]:
            if st.button("🎯 Otimizar Thresholds", use_container_width=True):
                st.info("🎯 Thresholds otimizados via algoritmo genético")
                st.success("✅ Redução de 15% nos falsos positivos")
        
        with intelligence_cols[2]:
            if st.button("📈 Análise de Tendências", use_container_width=True):
                st.warning("📈 Tendência: Aumento de fraudes PIX em 23%")
                st.info("💡 Sugestão: Aumentar monitoramento PIX nos fins de semana")
        
        with intelligence_cols[3]:
            if st.button("🌐 Benchmark Mercado", use_container_width=True):
                st.success("🌐 Performance 34% superior à média do mercado")
    
    # Primeira linha - Análise estratégica
    col1, col2 = st.columns(2)
    with col1:
        with widget_container():
            st.subheader("📊 Matriz de Perdas por Tipologia de Fraude")
            st.plotly_chart(create_fraud_heatmap(APP_THEME), use_container_width=True)
        
        with widget_container():
            st.subheader("🎯 Performance dos Modelos de ML")
            st.plotly_chart(create_ml_model_performance_chart(APP_THEME), use_container_width=True)
            
            ml_controls = st.columns(3)
            with ml_controls[0]:
                if st.button("🔄 Retreinar Modelos"):
                    st.success("🤖 Retreinamento agendado para 02:00")
            with ml_controls[1]:
                if st.button("📊 A/B Test Novos Modelos"):
                    st.info("🧪 Teste A/B iniciado - 10% do tráfego")
            with ml_controls[2]:
                if st.button("💾 Fazer Deploy"):
                    st.success("🚀 Deploy realizado em produção")
    
    with col2:
        with widget_container():
            st.subheader("🎛️ Simulador Avançado de Políticas de Risco")
            
            # Simulador com múltiplos parâmetros
            sim_cols = st.columns(2)
            with sim_cols[0]:
                threshold_block = st.slider("Score Bloqueio Automático", 700, 1000, 950, 10)
                threshold_review = st.slider("Score Revisão Manual", 600, 900, 800, 10)
                velocity_mult = st.slider("Multiplicador Velocity", 0.5, 3.0, 1.0, 0.1)
            with sim_cols[1]:
                geo_enabled = st.checkbox("Geo-blocking Ativo", True)
                device_enabled = st.checkbox("Device Fingerprint", True)
                peak_hours_mult = st.slider("Multiplicador Horário Pico", 1.0, 2.0, 1.3, 0.1)
            
            # Cálculos do simulador
            fraud_reduction = (1000 - threshold_block) / 4 + velocity_mult * 5 + (15 if geo_enabled else 0)
            false_positives = (1000 - threshold_block) / 25 + velocity_mult * 2
            operational_cost = threshold_review * 0.1 + (10 if device_enabled else 5)
            
            sim_results = st.columns(3)
            sim_results[0].metric("🛡️ Redução de Fraude", f"{fraud_reduction:.1f}%", "↗️")
            sim_results[1].metric("⚠️ Falsos Positivos", f"{false_positives:.1f}%", "inverse")
            sim_results[2].metric("💰 Custo Operacional", f"R$ {operational_cost:.0f}K/mês", "neutral")
            
            if st.button("✅ Aplicar Configuração", type="primary", use_container_width=True):
                st.success("✅ Nova configuração aplicada em produção!")
                st.balloons()
        
        with widget_container():
            st.subheader("⚡ Efetividade das Intervenções")
            st.plotly_chart(create_intervention_effectiveness_chart(APP_THEME), use_container_width=True)
            
            intervention_controls = st.columns(2)
            with intervention_controls[0]:
                if st.button("📈 Otimizar Mix de Intervenções"):
                    st.success("📈 Mix otimizado: +12% efetividade geral")
            with intervention_controls[1]:
                if st.button("🔍 Análise de Impacto"):
                    st.info("🔍 Análise de impacto gerada em 'Relatórios'")
    
    # Segunda linha - Análises avançadas
    col3, col4 = st.columns(2)
    with col3:
        with widget_container():
            st.subheader("🏆 Desempenho da Equipe de Prevenção")
            team_cols = st.columns(3)
            team_cols[0].metric("Tempo Médio de Resolução", "8.5 min", "↘️ -3.5 min")
            team_cols[1].metric("Taxa de Falsos Positivos", "3.1%", "↘️ -0.7%")
            team_cols[2].metric("Casos Resolvidos/Dia", "127", "↗️ +15")
            
            st.markdown("---")
            team_performance_cols = st.columns(4)
            with team_performance_cols[0]:
                if st.button("👨‍💼 Rankings Individual"):
                    st.success("🏆 Top Analista: João Silva (98% acurácia)")
            with team_performance_cols[1]:
                if st.button("📚 Treinamentos"):
                    st.info("📚 3 cursos de atualização disponíveis")
            with team_performance_cols[2]:
                if st.button("📊 Dashboards Pessoais"):
                    st.success("📊 Dashboards enviados por email")
            with team_performance_cols[3]:
                if st.button("🎯 Metas da Semana"):
                    st.warning("🎯 Meta: Reduzir tempo médio para 7 min")
    
    with col4:
        with widget_container():
            st.subheader("🔮 Análise Preditiva de Risco de Eventos")
            st.plotly_chart(create_predictive_event_risk_chart(APP_THEME), use_container_width=True)
            
            prediction_controls = st.columns(3)
            with prediction_controls[0]:
                if st.button("🔮 Nova Predição"):
                    event_name = st.text_input("Nome do Evento", "Copa do Mundo - Final")
                    if st.button("Calcular Risco"):
                        risk_pred = np.random.uniform(70, 95)
                        st.error(f"🚨 Risco Previsto: {risk_pred:.1f}%")
            with prediction_controls[1]:
                if st.button("⚙️ Calibrar Modelos"):
                    st.info("⚙️ Modelos recalibrados com dados históricos")
            with prediction_controls[2]:
                if st.button("📈 Histórico de Acertos"):
                    st.success("📈 Taxa de acerto: 89.3% (últimos 6 meses)")
    
    # Terceira linha - Cenários e simulações
    with widget_container():
        st.subheader("🎮 Simulador de Cenários de Crise")
        scenario_tabs = st.tabs(["💥 Black Friday", "🏆 Copa do Mundo", "🎆 Réveillon", "📱 Campanha Viral"])
        
        with scenario_tabs[0]:  # Black Friday
            crisis_cols = st.columns(4)
            crisis_cols[0].metric("📈 Aumento do Volume", "+340%", "🔴")
            crisis_cols[1].metric("🚨 Risco de Fraude", "+180%", "🔴")
            crisis_cols[2].metric("👥 Analistas Necessários", "23", "↗️ +15")
            crisis_cols[3].metric("💰 Budget Extra", "R$ 180K", "💸")
            
            bf_actions = st.columns(3)
            with bf_actions[0]:
                if st.button("🚀 Ativar Protocolo Black Friday"):
                    st.error("🚀 PROTOCOLO ATIVADO: Thresholds ajustados para pico de volume")
            with bf_actions[1]:
                if st.button("👥 Convocar Equipe Extra"):
                    st.warning("👥 15 analistas adicionais convocados")
            with bf_actions[2]:
                if st.button("🤖 Modo ML Agressivo"):
                    st.info("🤖 Modelos ML em modo alta performance")
        
        with scenario_tabs[1]:  # Copa do Mundo
            world_cup_cols = st.columns(4)
            world_cup_cols[0].metric("⚽ Apostas Esportivas", "+520%", "🟡")
            world_cup_cols[1].metric("🎯 Apostas Suspeitas", "+89%", "🔴")
            world_cup_cols[2].metric("🌍 Tráfego Internacional", "+156%", "⚠️")
            world_cup_cols[3].metric("🕐 Pico de Atividade", "14h-22h", "📊")
        
        with scenario_tabs[2]:  # Réveillon
            new_year_cols = st.columns(4)
            new_year_cols[0].metric("🎆 Pico de Transações", "23:50-00:30", "🔴")
            new_year_cols[1].metric("🍾 Apostas Festa", "+280%", "🟡")
            new_year_cols[2].metric("📱 Apps Instabilidade", "Média", "⚠️")
            new_year_cols[3].metric("🔧 Suporte Técnico", "Reforçado", "✅")
        
        with scenario_tabs[3]:  # Campanha Viral
            viral_cols = st.columns(4)
            viral_cols[0].metric("📱 Tráfego Social", "+1,200%", "🔴")
            viral_cols[1].metric("👶 Usuários Novos", "+890%", "⚠️")
            viral_cols[2].metric("🎁 Bônus Claims", "+2,100%", "🚨")
            viral_cols[3].metric("🛡️ Risco Laranja", "CRÍTICO", "🔴")
    
    # Rodapé com estatísticas avançadas
    with widget_container():
        st.subheader("📊 Inteligência de Mercado e Benchmarks")
        benchmark_cols = st.columns(6)
        benchmark_cols[0].metric("🏅 Posição no Mercado", "#1", "🥇")
        benchmark_cols[1].metric("🎯 Taxa de Detecção", "94.7%", "↗️ +2.1%")
        benchmark_cols[2].metric("⚡ Tempo de Resposta", "1.2s", "↘️ -0.3s")
        benchmark_cols[3].metric("💎 Satisfação Cliente", "4.8/5", "⭐")
        benchmark_cols[4].metric("🔄 Uptime Sistema", "99.97%", "🟢")
        benchmark_cols[5].metric("🚀 Inovação Score", "9.2/10", "🏆")
