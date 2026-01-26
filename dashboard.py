import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="CRM Analytics Dashboard - Final Boss Edition",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fb 100%);
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #2E86AB;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
        border-left: 5px solid #ff6b35;
    }
    
    .strategy-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-left: 5px solid #ff6b35;
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    h1, h2, h3 {
        color: #1a1a2e;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 600;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING & CACHING
# ============================================================================
@st.cache_data
def load_and_process_data():
    """Load customer-level CLTV data with RFM segments."""
    try:
        df = pd.read_csv('final_cltv_segmentation.csv')
        
        # Ensure numeric columns
        numeric_cols = ['cltv', 'expected_purc_3_month', 'expected_purc_6_month', 
                       'expected_average_profit', 'monetary', 'frequency']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove NaN values
        df = df.dropna(subset=['cltv'])
        
        # Create CLTV-based grades (A, B, C, D) using qcut for quantile-based binning
        df['cltv_grade'] = pd.qcut(df['cltv'], 
                                    q=[0, 0.4, 0.7, 0.9, 1.0],
                                    labels=['D (At Risk)', 'C (Re-Engagement)', 
                                           'B (High Potential)', 'A (Champions)'],
                                    duplicates='drop')
        
        # Calculate financial projections
        df['Current Profit'] = df['expected_average_profit']
        df['Projected Profit (3 Months)'] = df['expected_average_profit'] * df['expected_purc_3_month']
        df['Projected Profit (6 Months)'] = df['expected_average_profit'] * df['expected_purc_6_month']
        
        return df
    except FileNotFoundError:
        st.error("❌ Error: 'final_cltv_segmentation.csv' not found.")
        return None

@st.cache_data
def load_ai_strategies():
    """Load AI marketing strategies from CSV."""
    try:
        df = pd.read_csv('final_ai_powered_crm_analysis.csv')
        # Create a mapping of segment -> AI strategy
        strategies_dict = {}
        for idx, row in df.iterrows():
            segment = row.get('segment', 'Unknown')
            strategy = row.get('AI_Marketing_Strategy', 'Strategy not available')
            if segment not in strategies_dict:
                strategies_dict[segment] = strategy
        return strategies_dict
    except FileNotFoundError:
        st.warning("⚠️ AI strategy file not found. Using default strategies.")
        return {}

def format_currency(value):
    """Format value as currency with $ sign and 2 decimal places."""
    if pd.isna(value):
        return "$0.00"
    return f"${value:,.2f}"

def format_number(value):
    """Format number with commas."""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}"

def get_rfm_segment_emoji(rfm_segment):
    """Get emoji for RFM segment."""
    emoji_map = {
        'Champions': '🏆',
        'Loyal Customers': '💎',
        'Potential Loyalists': '⭐',
        'At Risk': '⚠️',
        'Hibernating': '💤',
        'Can\'t Lose Them': '🔥',
        'New Customers': '🌱',
        'Promising': '📈',
        'Need Attention': '👀',
        'About To Sleep': '😴'
    }
    return emoji_map.get(rfm_segment, '📊')

def get_rfm_segment_strategy(rfm_segment, ai_strategies):
    """Get AI strategy for RFM segment from loaded data."""
    # Try to get from loaded strategies first
    if rfm_segment in ai_strategies and ai_strategies[rfm_segment]:
        return ai_strategies[rfm_segment]
    
    # Fallback to default strategies
    default_strategies = {
        'Champions': 'VIP Retention & Upselling: Maximize lifetime value through exclusive programs, premium rewards, and strategic cross-selling opportunities.',
        'Loyal Customers': 'Growth & Expansion: Increase purchase frequency and order value through personalized offers, loyalty perks, and bundle deals.',
        'Potential Loyalists': 'Convert & Nurture: Build customer relationships through education, incentives, and smart product recommendations.',
        'At Risk': 'Retention & Win-Back: Prevent churn with special offers, feedback collection, and priority service recovery.',
        'Hibernating': 'Re-Engagement Push: Reactivate inactive customers with special offers, product updates, and fresh engagement strategies.',
        'Can\'t Lose Them': 'Emergency Intervention: Prevent loss of high-value customers with executive outreach and custom recovery programs.',
        'New Customers': 'Onboarding & Integration: Convert into loyal repeat customers through welcome programs and education.',
        'Promising': 'Accelerate Growth: Fast-track high-potential customers with engagement, early upselling, and loyalty program enrollment.',
        'Need Attention': 'Focused Support: Engage and retain potentially high-value customers through personalized outreach.',
        'About To Sleep': 'Wake-Up Campaign: Prevent hibernation with proactive outreach and relevant offers.'
    }
    return default_strategies.get(rfm_segment, f'Develop strategic approach for {rfm_segment} segment.')

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    # Load data
    df = load_and_process_data()
    ai_strategies = load_ai_strategies()
    
    if df is None:
        return
    
    # ========================================================================
    # HEADER SECTION
    # ========================================================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🎯 CRM Analytics Dashboard - Final Boss Edition")
        st.markdown("**Professional Financial Projections & AI-Powered Strategies**")
    
    st.markdown("---")
    
    # ========================================================================
    # SIDEBAR FILTERS
    # ========================================================================
    st.sidebar.markdown("## 🎯 Dashboard Controls")
    
    # CLTV Grade Filter
    st.sidebar.markdown("### 📊 Filter by CLTV Grade")
    all_grades = sorted([str(x) for x in df['cltv_grade'].unique() if pd.notna(x)])
    selected_grades = st.sidebar.multiselect(
        "Select Customer Grades:",
        options=all_grades,
        default=all_grades,
        help="Filter dashboard by customer CLTV grades"
    )
    
    # RFM Segment Filter
    st.sidebar.markdown("### 🎯 Select RFM Segment")
    rfm_segments = sorted([x for x in df['segment'].unique() if pd.notna(x)])
    selected_rfm = st.sidebar.selectbox(
        "Choose RFM Segment:",
        options=rfm_segments,
        help="Select a specific RFM segment to analyze"
    )
    
    # Filter data
    filtered_df = df[df['cltv_grade'].astype(str).isin(selected_grades)].copy()
    segment_df = df[df['segment'] == selected_rfm].copy()
    segment_filtered_df = segment_df[segment_df['cltv_grade'].astype(str).isin(selected_grades)].copy()
    
    if filtered_df.empty:
        st.warning("⚠️ No data available for selected filters.")
        return
    
    # ========================================================================
    # TAB NAVIGATION
    # ========================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Financial Dashboard", 
        "🎯 Segment Analysis", 
        "🤖 AI Strategy Engine", 
        "📈 Predictive Analytics"
    ])
    
    # ========================================================================
    # TAB 1: FINANCIAL DASHBOARD
    # ========================================================================
    with tab1:
        st.subheader("💰 Financial Projections by CLTV Grade")
        st.markdown("**Current Profit vs 3-Month and 6-Month Projections**")
        st.markdown("---")
        
        # Create aggregated financial data by grade
        grade_financials = filtered_df.groupby('cltv_grade', observed=True).agg({
            'Customer ID': 'count',
            'Current Profit': ['mean', 'sum'],
            'Projected Profit (3 Months)': ['mean', 'sum'],
            'Projected Profit (6 Months)': ['mean', 'sum'],
            'cltv': ['mean', 'sum']
        }).round(2)
        
        # Flatten columns
        grade_financials.columns = [
            'Customer Count',
            'Avg Current Profit', 'Total Current Profit',
            'Avg Proj 3M', 'Total Proj 3M',
            'Avg Proj 6M', 'Total Proj 6M',
            'Avg CLTV', 'Total CLTV'
        ]
        grade_financials = grade_financials.reset_index()
        
        # Display as interactive table
        st.markdown("### 📊 Interactive Profit Table")
        
        # Create styled dataframe display
        display_df = grade_financials[[
            'cltv_grade', 'Customer Count',
            'Avg Current Profit', 'Avg Proj 3M', 'Avg Proj 6M'
        ]].copy()
        
        display_df.columns = ['Grade', 'Customers', 'Current Profit', '3-Month Proj', '6-Month Proj']
        
        # Format currencies
        display_df['Current Profit'] = grade_financials['Avg Current Profit'].apply(format_currency)
        display_df['3-Month Proj'] = grade_financials['Avg Proj 3M'].apply(format_currency)
        display_df['6-Month Proj'] = grade_financials['Avg Proj 6M'].apply(format_currency)
        display_df['Customers'] = grade_financials['Customer Count'].apply(format_number)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Total aggregates
        st.markdown("### 💵 Total Profit Aggregates")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_current = grade_financials['Total Current Profit'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #2E86AB; margin: 0;">Current Total Profit</h4>
                <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(total_current)}</h2>
                <p style="color: #666; margin: 0; font-size: 0.85em;">All Customers</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_proj3m = grade_financials['Total Proj 3M'].sum()
            growth_3m = ((total_proj3m - total_current) / total_current * 100) if total_current > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #00A8E8; margin: 0;">3-Month Projection</h4>
                <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(total_proj3m)}</h2>
                <p style="color: #00A8E8; margin: 0; font-size: 0.85em;">↑ {growth_3m:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_proj6m = grade_financials['Total Proj 6M'].sum()
            growth_6m = ((total_proj6m - total_current) / total_current * 100) if total_current > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #00D084; margin: 0;">6-Month Projection</h4>
                <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(total_proj6m)}</h2>
                <p style="color: #00D084; margin: 0; font-size: 0.85em;">↑ {growth_6m:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_cltv = grade_financials['Avg CLTV'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #FF6B35; margin: 0;">Average CLTV</h4>
                <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(avg_cltv)}</h2>
                <p style="color: #666; margin: 0; font-size: 0.85em;">Customer Lifetime Value</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Visualization: Profit comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Profit Progression by Grade")
            profit_data = grade_financials.sort_values('cltv_grade')
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=profit_data['cltv_grade'].astype(str),
                y=profit_data['Avg Current Profit'],
                name='Current Profit',
                marker_color='#FF6B35'
            ))
            
            fig.add_trace(go.Bar(
                x=profit_data['cltv_grade'].astype(str),
                y=profit_data['Avg Proj 3M'],
                name='3-Month Projection',
                marker_color='#00A8E8'
            ))
            
            fig.add_trace(go.Bar(
                x=profit_data['cltv_grade'].astype(str),
                y=profit_data['Avg Proj 6M'],
                name='6-Month Projection',
                marker_color='#00D084'
            ))
            
            fig.update_layout(
                barmode='group',
                height=400,
                hovermode='x unified',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Total CLTV by Grade")
            cltv_data = grade_financials.sort_values('cltv_grade')
            
            fig = px.bar(
                cltv_data,
                x='cltv_grade',
                y='Total CLTV',
                color='cltv_grade',
                color_discrete_sequence=['#FF6B6B', '#FFA500', '#00A8E8', '#00D084'],
                labels={'cltv_grade': 'Grade', 'Total CLTV': 'Total CLTV ($)'},
                text='Total CLTV'
            )
            
            fig.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            )
            
            fig.update_layout(
                height=400,
                hovermode='x unified',
                showlegend=False,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # TAB 2: SEGMENT ANALYSIS
    # ========================================================================
    with tab2:
        st.subheader(f"🎯 RFM Segment Analysis: {selected_rfm}")
        st.markdown(f"**Detailed breakdown of {selected_rfm} segment**")
        st.markdown("---")
        
        if segment_filtered_df.empty:
            st.warning(f"⚠️ No customers in {selected_rfm} segment with selected grades.")
        else:
            # Segment overview cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                seg_count = len(segment_filtered_df)
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #2E86AB; margin: 0;">Total Customers</h4>
                    <h2 style="color: #1a1a2e; margin: 10px 0;">{format_number(seg_count)}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.85em;">{selected_rfm}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                seg_avg_cltv = segment_filtered_df['cltv'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #2E86AB; margin: 0;">Average CLTV</h4>
                    <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(seg_avg_cltv)}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.85em;">Customer Value</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                seg_total_cltv = segment_filtered_df['cltv'].sum()
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #2E86AB; margin: 0;">Total Segment Value</h4>
                    <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(seg_total_cltv)}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.85em;">Combined CLTV</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                seg_avg_profit = segment_filtered_df['Current Profit'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #00D084; margin: 0;">Avg Profit</h4>
                    <h2 style="color: #1a1a2e; margin: 10px 0;">{format_currency(seg_avg_profit)}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.85em;">Per Customer</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Grade distribution in segment
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Grade Distribution")
                grade_dist = segment_filtered_df['cltv_grade'].value_counts().sort_index()
                
                fig = px.bar(
                    x=grade_dist.index.astype(str),
                    y=grade_dist.values,
                    color=grade_dist.index.astype(str),
                    color_discrete_sequence=['#FF6B6B', '#FFA500', '#00A8E8', '#00D084'],
                    labels={'x': 'Grade', 'y': 'Customer Count'},
                    text=grade_dist.values
                )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 💰 CLTV by Grade")
                cltv_by_grade = segment_filtered_df.groupby('cltv_grade', observed=True)['cltv'].mean().sort_index()
                
                fig = px.bar(
                    x=cltv_by_grade.index.astype(str),
                    y=cltv_by_grade.values,
                    color=cltv_by_grade.index.astype(str),
                    color_discrete_sequence=['#FF6B6B', '#FFA500', '#00A8E8', '#00D084'],
                    labels={'x': 'Grade', 'y': 'Avg CLTV ($)'},
                    text=cltv_by_grade.values
                )
                
                fig.update_traces(
                    texttemplate='$%{text:,.0f}',
                    textposition='outside'
                )
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed segment table
            st.markdown("### 📋 Top 10 Customers in Segment")
            seg_table = segment_filtered_df[[
                'Customer ID', 'cltv_grade', 'cltv',
                'Current Profit', 'Projected Profit (3 Months)', 'Projected Profit (6 Months)',
                'frequency', 'monetary'
            ]].head(10).copy()
            
            seg_table.columns = ['Customer ID', 'Grade', 'CLTV', 'Current Profit', 
                                '3M Proj', '6M Proj', 'Frequency', 'Monetary']
            
            seg_table['CLTV'] = segment_filtered_df['cltv'].head(10).apply(format_currency)
            seg_table['Current Profit'] = segment_filtered_df['Current Profit'].head(10).apply(format_currency)
            seg_table['3M Proj'] = segment_filtered_df['Projected Profit (3 Months)'].head(10).apply(format_currency)
            seg_table['6M Proj'] = segment_filtered_df['Projected Profit (6 Months)'].head(10).apply(format_currency)
            
            st.dataframe(seg_table, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 3: AI STRATEGY ENGINE (GÜNCELLENMİŞ VERSİYON)
    # ========================================================================
    with tab3:
        st.subheader("🤖 AI-Integrated Strategy Engine")
        st.markdown("**Select a segment below to view specific AI-driven recommendations.**")
        
        # Strateji Verileri
        strategies_data = {
            "Segment A": {
                "marketing": "Implement a VIP Loyalty Program offering exclusive perks, such as early access to new products or special events, ensuring they feel valued and engaged.",
                "win_back": "Send personalized appreciation messages with special offers or discounts on their next purchase, reinforcing their loyalty and encouraging repeat business.",
                "emoji": "🏆",
                "color": "success"
            },
            "Segment B": {
                "marketing": "Launch targeted email campaigns that offer tailored recommendations based on their past purchases, combined with limited-time offers to boost engagement and sales.",
                "win_back": "Create a feedback loop by reaching out with a survey about their experience, offering a small discount for completing it, showing that their opinions matter and aiming to re-engage them.",
                "emoji": "💎",
                "color": "info"
            },
            "Segment C": {
                "marketing": "Introduce a re-engagement campaign featuring educational content about product usage or benefits, aimed at increasing their interest and perceived value.",
                "win_back": "Provide a strong incentive, such as a significant discount or a free add-on with their next purchase, targeted specifically to those at high risk of churning.",
                "emoji": "⚠️",
                "color": "warning"
            },
            "Segment D": {
                "marketing": "Implement personalized check-in communications that convey concern for their experience, with customized recommendations to enhance their satisfaction and product engagement.",
                "win_back": "Offer a compelling 'second chance' offer, such as a one-time deep discount or value bundle, aimed at winning back their trust and prompting immediate action.",
                "emoji": "🚨",
                "color": "error"
            }
        }

        # Session State Kontrolü
        if 'selected_strat_segment' not in st.session_state:
            st.session_state.selected_strat_segment = 'Segment A'

        st.markdown("---")

        # 4 Tane Tıklanabilir Kutu (Butonlar)
        col1, col2, col3, col4 = st.columns(4)
        
        # Butonların oluşturulması ve tıklama mantığı
        if col1.button(f"🏆 Segment A", use_container_width=True):
            st.session_state.selected_strat_segment = 'Segment A'
            
        if col2.button(f"💎 Segment B", use_container_width=True):
            st.session_state.selected_strat_segment = 'Segment B'
            
        if col3.button(f"⚠️ Segment C", use_container_width=True):
            st.session_state.selected_strat_segment = 'Segment C'
            
        if col4.button(f"🚨 Segment D", use_container_width=True):
            st.session_state.selected_strat_segment = 'Segment D'

        # Seçilen Stratejinin Gösterimi
        selected_seg = st.session_state.selected_strat_segment
        data = strategies_data[selected_seg]

        st.markdown(f"### {data['emoji']} Strategy for {selected_seg}")
        
        # Görsel olarak zenginleştirilmiş kutular
        with st.container():
            # Marketing Strategy Box
            st.markdown(f"""
            <div style="background-color: #000000; padding: 20px; border-radius: 10px; border-left: 5px solid #2E86AB; margin-bottom: 20px;">
                <h4 style="color: #2E86AB; margin-top: 0;">📢 Marketing Strategy</h4>
                <p style="font-size: 1.1em; line-height: 1.6;">{data['marketing']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Win-back Action Box
            st.markdown(f"""
            <div style="background-color: #000000; padding: 20px; border-radius: 10px; border-left: 5px solid #ff6b35;">
                <h4 style="color: #ff6b35; margin-top: 0;">↩️ Win-back Action</h4>
                <p style="font-size: 1.1em; line-height: 1.6;">{data['win_back']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 4: PREDICTIVE ANALYTICS
    # ========================================================================
    with tab4:
        st.subheader("📈 Predictive Analytics & Insights")
        st.markdown("**Forecast and trend analysis**")
        st.markdown("---")
        
        # Grade-wise profit trajectory
        st.markdown("### 📊 Profit Trajectory by Grade")
        
        grade_trajectory = filtered_df.groupby('cltv_grade', observed=True).agg({
            'Current Profit': 'mean',
            'Projected Profit (3 Months)': 'mean',
            'Projected Profit (6 Months)': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        
        color_map = {
            'D (At Risk)': '#FF6B6B',
            'C (Re-Engagement)': '#FFA500',
            'B (High Potential)': '#00A8E8',
            'A (Champions)': '#00D084'
        }
        
        for grade in grade_trajectory['cltv_grade'].unique():
            grade_data = grade_trajectory[grade_trajectory['cltv_grade'] == grade]
            
            fig.add_trace(go.Scatter(
                x=['Current', '3-Month', '6-Month'],
                y=[
                    grade_data['Current Profit'].values[0],
                    grade_data['Projected Profit (3 Months)'].values[0],
                    grade_data['Projected Profit (6 Months)'].values[0]
                ],
                mode='lines+markers',
                name=str(grade),
                line=dict(color=color_map.get(str(grade), '#999'), width=3),
                marker=dict(size=10)
            ))
        
        fig.update_layout(
            title='Profit Progression Timeline',
            xaxis_title='Time Period',
            yaxis_title='Average Profit ($)',
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Key insights
        st.markdown("### 💡 Key Insights & Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Best performing grade
            best_grade = filtered_df.groupby('cltv_grade', observed=True)['Projected Profit (6 Months)'].mean().idxmax()
            best_value = filtered_df.groupby('cltv_grade', observed=True)['Projected Profit (6 Months)'].mean().max()
            
            st.info(f"""
            **🏆 Best Performing Grade**: {best_grade}
            
            Expected 6-month profit per customer: {format_currency(best_value)}
            
            *Recommendation*: Invest heavily in this grade to maximize ROI
            """)
        
        with col2:
            # Needs attention grade
            worst_grade = filtered_df.groupby('cltv_grade', observed=True)['Projected Profit (6 Months)'].mean().idxmin()
            worst_value = filtered_df.groupby('cltv_grade', observed=True)['Projected Profit (6 Months)'].mean().min()
            
            st.warning(f"""
            **⚠️ Needs Attention**: {worst_grade}
            
            Expected 6-month profit per customer: {format_currency(worst_value)}
            
            *Recommendation*: Deploy intervention strategies immediately
            """)
        
        st.markdown("---")
        
        # Segment comparison
        st.markdown("### 🎯 All RFM Segments Comparison")
        
        rfm_comparison = df.groupby('segment', observed=True).agg({
            'Customer ID': 'count',
            'cltv': 'mean',
            'Current Profit': 'mean',
            'Projected Profit (6 Months)': 'mean'
        }).round(2).reset_index()
        
        rfm_comparison.columns = ['Segment', 'Customers', 'Avg CLTV', 'Avg Profit', 'Avg 6M Proj']
        rfm_comparison = rfm_comparison.sort_values('Avg 6M Proj', ascending=False)
        
        display_rfm = rfm_comparison.copy()
        display_rfm['Customers'] = rfm_comparison['Customers'].apply(lambda x: f"{int(x):,}")
        display_rfm['Avg CLTV'] = rfm_comparison['Avg CLTV'].apply(format_currency)
        display_rfm['Avg Profit'] = rfm_comparison['Avg Profit'].apply(format_currency)
        display_rfm['Avg 6M Proj'] = rfm_comparison['Avg 6M Proj'].apply(format_currency)
        
        st.dataframe(display_rfm, use_container_width=True, hide_index=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()