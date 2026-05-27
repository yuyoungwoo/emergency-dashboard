import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random
import platform
import matplotlib.pyplot as plt

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(
    page_title="응급실 대기 예측 시스템",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SVG 아이콘 딕셔너리 ─────────────────────────────────
ICON = {
    "chart":    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
    "clock":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "bed":      '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8v9"/></svg>',
    "alert":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "users":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "logout":   '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
    "hospital": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "trend_up": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "trend_dn": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
    "search":   '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M4.93 19.07l1.41-1.41M19.07 19.07l-1.41-1.41M12 2v2M12 20v2M2 12h2M20 12h2"/></svg>',
    "logo":     '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "wifi":     '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>',
    "table":    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="9" x2="9" y2="21"/></svg>',
    "menu":     '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>',
    "close":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
}

def svg(key, color="currentColor"):
    return ICON[key].replace('stroke="currentColor"', f'stroke="{color}"')

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Pretendard', 'Inter', sans-serif !important;
    box-sizing: border-box;
}
.stApp { background: #f1f5f9; }

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #1e3a5f !important;
    border-right: none !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
}

/* 사이드바 토글 버튼 커스텀 */
[data-testid="stSidebarHeader"] {
    background: #1e3a5f !important;
    padding: 8px !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] button {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    width: 34px !important;
    height: 34px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: background .15s !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"] button:hover {
    background: rgba(255,255,255,0.2) !important;
}
[data-testid="stSidebarCollapseButton"] button svg,
[data-testid="stExpandSidebarButton"] button svg {
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

/* 상단 툴바 숨기기 */
[data-testid="stAppToolbar"] { display: none !important; }
[data-testid="stMainMenu"]   { display: none !important; }

.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 100% !important;
}
.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 4px rgba(15,23,42,.06), 0 4px 16px rgba(15,23,42,.04);
    margin-bottom: 16px;
    border: 1px solid #e2e8f0;
}
.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 1px 4px rgba(15,23,42,.06);
    border: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    min-height: 150px;
}
.kpi-icon {
    width: 42px; height: 42px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 16px;
}
.kpi-label { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 6px; }
.kpi-value { font-size: 30px; font-weight: 800; color: #0f172a; line-height: 1.1; }
.kpi-delta { font-size: 12px; font-weight: 600; margin-top: 8px; display: flex; align-items: center; gap: 4px; }
.sec-title { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.pg-title  { font-size: 22px; font-weight: 800; color: #0f172a; margin-bottom: 2px; }
.pg-sub    { font-size: 13px; color: #64748b; margin-bottom: 20px; }
.badge { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge-red   { background:#fee2e2; color:#dc2626; }
.badge-amber { background:#fef3c7; color:#b45309; }
.badge-green { background:#d1fae5; color:#059669; }
.tl-item { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.tl-dot  { width: 9px; height: 9px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
.tl-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.tl-sub  { font-size: 12px; color: #64748b; margin-top: 2px; }
.sb-divider  { border: none; border-top: 1px solid rgba(255,255,255,.08); margin: 8px 0; }
.sb-section  { font-size: 10px; font-weight: 700; letter-spacing:.1em; color: #475569; text-transform: uppercase; padding: 14px 12px 6px; }
.sb-menu-item { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; color: #94a3b8; margin-bottom: 2px; }
div[data-testid="metric-container"] { display: none; }
.stButton > button {
    background: #2563eb !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: .5rem 1.4rem !important;
}
.stMultiSelect [data-baseweb="tag"] { background: #2563eb !important; color: #fff !important; }

/* 모바일 대응 */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem !important; }
    .kpi-card { padding: 16px 18px !important; min-height: 120px !important; }
    .kpi-value { font-size: 24px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── 샘플 데이터 생성 ────────────────────────────────────
@st.cache_data
def load_data():
    random.seed(42); np.random.seed(42)
    hospitals = [
        {"name": "부산대학교병원",     "lat": 35.1318, "lon": 129.1026, "level": "권역"},
        {"name": "고신대학교복음병원", "lat": 35.0960, "lon": 128.9788, "level": "지역"},
        {"name": "동아대학교병원",     "lat": 35.1042, "lon": 128.9749, "level": "권역"},
        {"name": "해운대백병원",       "lat": 35.1637, "lon": 129.1696, "level": "지역"},
        {"name": "부산성모병원",       "lat": 35.1547, "lon": 129.0607, "level": "지역"},
    ]
    data = []
    for h in hospitals:
        wait = random.randint(20, 240)
        bt = random.randint(30, 80)
        ba = random.randint(0, bt // 2)
        cong = "혼잡" if wait > 120 else ("보통" if wait > 60 else "여유")
        data.append({"병원명": h["name"], "위도": h["lat"], "경도": h["lon"],
                     "등급": h["level"], "대기(분)": wait,
                     "전체병상": bt, "가용병상": ba, "혼잡도": cong})
    df_h = pd.DataFrame(data)
    td = {}
    for h in hospitals[:3]:
        base, vals = random.randint(60, 120), []
        for hr in range(24):
            v = base * (0.6 if hr < 6 else 1.2 if hr < 9 else 1.5 if hr < 18 else 1.8 if hr < 22 else 1.3)
            vals.append(int(v + random.randint(-10, 10)))
        td[h["name"]] = vals
    df_t = pd.DataFrame(td, index=range(24))
    df_k = pd.DataFrame({
        "등급": ["1등급 소생", "2등급 긴급", "3등급 응급", "4등급 준응급", "5등급 비응급"],
        "환자": [12, 45, 180, 320, 290],
        "색":   ["#ef4444", "#f59e0b", "#2563eb", "#10b981", "#94a3b8"]
    })
    return df_h, df_t, df_k

df_h, df_t, df_k = load_data()

# ── 사이드바 ────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:.8rem 0 1rem;">
        <div style="width:36px;height:36px;border-radius:10px;background:#2563eb;
                    display:flex;align-items:center;justify-content:center;">
            {svg('logo')}
        </div>
        <div>
            <div style="color:#f8fafc;font-weight:800;font-size:14px;line-height:1.2;">응급실 예측</div>
            <div style="color:#64748b;font-size:11px;">AI 모니터링</div>
        </div>
    </div>
    <hr class="sb-divider">
    <div class="sb-section">메뉴</div>
    """, unsafe_allow_html=True)

    menu = st.radio("", ["대시보드", "지도", "AI 문진", "분석"], label_visibility="collapsed")

    st.markdown(f"""
    <hr class="sb-divider">
    <div class="sb-section">시스템</div>
    <div class="sb-menu-item">{svg('settings','#94a3b8')} &nbsp;설정</div>
    <div class="sb-menu-item" style="color:#ef4444 !important;">{svg('logout','#ef4444')} &nbsp;로그아웃</div>
    <hr class="sb-divider">
    <div style="padding:8px 12px;">
        <div style="font-size:11px;color:#475569;">{svg('clock','#475569')} &nbsp;{datetime.now().strftime('%H:%M')} 기준 (샘플)</div>
        <div style="font-size:11px;color:#475569;margin-top:4px;">{svg('wifi','#475569')} &nbsp;국립중앙의료원 API</div>
    </div>
    """, unsafe_allow_html=True)

# ── 대시보드 ─────────────────────────────────────────────
if menu == "대시보드":
    st.markdown('<div class="pg-title">대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">부산 권역 응급실 실시간 현황</div>', unsafe_allow_html=True)

    avg_wait  = int(df_h["대기(분)"].mean())
    tot_beds  = df_h["가용병상"].sum()
    congested = len(df_h[df_h["혼잡도"] == "혼잡"])
    mild_pct  = 61.0

    kpis = [
        ("clock",  "#eff6ff", "#2563eb", "평균 대기시간",  f"{avg_wait}분",  "trend_dn", "#ef4444", "+12분"),
        ("bed",    "#f0fdf4", "#10b981", "총 가용 병상",   f"{tot_beds}개",  "trend_up", "#10b981", "+1.2%"),
        ("alert",  "#fff7ed", "#f59e0b", "혼잡 병원 수",   f"{congested}개", "trend_dn", "#ef4444", "즉시 분산 필요"),
        ("users",  "#eff6ff", "#2563eb", "경증 환자 비율", f"{mild_pct}%",   "trend_up", "#10b981", "+0.5%"),
    ]

    cols = st.columns(4)
    for col, (icon_key, bg, ic_color, label, val, trend_key, t_color, delta) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon" style="background:{bg};">{svg(icon_key, ic_color)}</div>
                <div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val}</div>
                    <div class="kpi-delta" style="color:{t_color};">
                        {svg(trend_key, t_color)} {delta}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_g, col_tl = st.columns([1.8, 1])

    with col_g:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{svg("chart","#2563eb")} 시간대별 대기시간 예측</div>', unsafe_allow_html=True)
        selected = st.multiselect("", df_t.columns.tolist(),
                                  default=df_t.columns.tolist()[:2],
                                  label_visibility="collapsed")
        if selected:
            fig = go.Figure()
            pal      = ["#2563eb", "#10b981", "#f59e0b"]
            fill_pal = ["rgba(37,99,235,0.07)", "rgba(16,185,129,0.07)", "rgba(245,158,11,0.07)"]
            for i, col in enumerate(selected):
                fig.add_trace(go.Scatter(
                    x=df_t.index, y=df_t[col], name=col,
                    mode='lines+markers',
                    line=dict(color=pal[i % len(pal)], width=2.5),
                    marker=dict(size=4, color=pal[i % len(pal)]),
                    fill='tozeroy', fillcolor=fill_pal[i % len(fill_pal)]
                ))
            fig.add_hline(y=120, line_dash="dot", line_color="#ef4444", line_width=1.5,
                          annotation_text="혼잡 기준", annotation_font_color="#ef4444",
                          annotation_position="right")
            fig.add_vline(x=datetime.now().hour, line_dash="dash", line_color="#94a3b8", line_width=1)
            fig.update_layout(
                height=270, plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
                margin=dict(l=0, r=10, t=10, b=0),
                font=dict(family="Pretendard, Inter", color="#0f172a", size=11),
                legend=dict(bgcolor="#ffffff", bordercolor="#e2e8f0", borderwidth=1,
                            orientation="h", yanchor="bottom", y=1.02, x=0),
                xaxis=dict(gridcolor="#e2e8f0", tickmode="array",
                           tickvals=list(range(0, 24, 3)),
                           ticktext=[f"{h}시" for h in range(0, 24, 3)],
                           showline=False, zeroline=False),
                yaxis=dict(gridcolor="#e2e8f0", title="대기(분)", showline=False, zeroline=False),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tl:
        st.markdown('<div class="card" style="height:100%">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{svg("hospital","#2563eb")} 실시간 현황</div>', unsafe_allow_html=True)
        tl_data = [
            ("혼잡", df_h.iloc[0]["병원명"], f"대기 {df_h.iloc[0]['대기(분)']}분", "#ef4444"),
            ("보통", df_h.iloc[2]["병원명"], f"대기 {df_h.iloc[2]['대기(분)']}분", "#f59e0b"),
            ("여유", df_h.iloc[3]["병원명"], f"대기 {df_h.iloc[3]['대기(분)']}분", "#10b981"),
            ("보통", df_h.iloc[4]["병원명"], f"가용 {df_h.iloc[4]['가용병상']}병상", "#f59e0b"),
            ("혼잡", df_h.iloc[1]["병원명"], f"대기 {df_h.iloc[1]['대기(분)']}분", "#ef4444"),
        ]
        for cong, name, detail, color in tl_data:
            bc = "badge-red" if cong == "혼잡" else ("badge-amber" if cong == "보통" else "badge-green")
            st.markdown(f"""
            <div class="tl-item">
                <div class="tl-dot" style="background:{color};margin-top:6px;"></div>
                <div style="flex:1;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div class="tl-name">{name}</div>
                        <span class="badge {bc}">{cong}</span>
                    </div>
                    <div class="tl-sub">{detail}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_tb, col_ktas = st.columns([1.4, 1])

    with col_tb:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{svg("table","#2563eb")} 응급실 현황</div>', unsafe_allow_html=True)
        def cc(v): return "color:#dc2626;font-weight:700" if v=="혼잡" else ("color:#b45309;font-weight:700" if v=="보통" else "color:#059669;font-weight:700")
        def cw(v): return "color:#dc2626" if v>120 else ("color:#b45309" if v>60 else "color:#059669")
        styled = df_h[["병원명","등급","대기(분)","가용병상","혼잡도"]].style\
            .map(cc, subset=["혼잡도"]).map(cw, subset=["대기(분)"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=210)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_ktas:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{svg("users","#2563eb")} KTAS 환자 분포</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=df_k["환자"], y=df_k["등급"], orientation='h',
            marker_color=df_k["색"].tolist(),
            text=df_k["환자"].astype(str) + "명",
            textposition='outside',
        ))
        fig2.update_layout(
            height=210, plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
            margin=dict(l=0, r=50, t=0, b=0),
            font=dict(family="Pretendard, Inter", color="#0f172a", size=11),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False), showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
        total = df_k["환자"].sum()
        mild  = df_k[df_k["등급"].str.contains("4등급|5등급")]["환자"].sum()
        st.markdown(f'<div style="font-size:12px;color:#64748b;margin-top:-8px;">💡 경증 비율 <b style="color:#2563eb">{mild/total*100:.1f}%</b> — 분산 시 혼잡도 완화 가능</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "지도":
    st.markdown('<div class="pg-title">지도</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">부산 권역 응급실 위치 및 혼잡도</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    m = folium.Map(location=[35.13, 129.05], zoom_start=12, tiles='CartoDB positron')
    cmap = {'혼잡': 'red', '보통': 'orange', '여유': 'green'}
    for _, row in df_h.iterrows():
        popup_html = f"""<div style='font-family:sans-serif;min-width:150px;'>
            <b>{row['병원명']}</b><br>대기: <b>{row['대기(분)']}분</b><br>
            가용병상: <b>{row['가용병상']}/{row['전체병상']}</b><br>혼잡도: <b>{row['혼잡도']}</b></div>"""
        folium.Marker(
            [row['위도'], row['경도']],
            popup=folium.Popup(popup_html, max_width=180),
            tooltip=f"{row['병원명']} ({row['혼잡도']})",
            icon=folium.Icon(color=cmap[row['혼잡도']], icon='plus-sign', prefix='glyphicon')
        ).add_to(m)
    st_folium(m, width=None, height=520)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "AI 문진":
    st.markdown('<div class="pg-title">AI 증상 문진</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">증상을 선택하면 경증/중증 여부를 AI가 판별합니다</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">{svg("search","#2563eb")} 증상 선택</div>', unsafe_allow_html=True)
    symptoms = st.multiselect("", [
        "발열 (38도 이상)", "두통", "복통", "호흡곤란", "가슴 통증",
        "구토/설사", "외상/골절", "의식 저하", "단순 감기", "피부 발진"
    ], label_visibility="collapsed")
    if st.button("중증도 판별하기"):
        if symptoms:
            severe = any(s in symptoms for s in ["호흡곤란", "가슴 통증", "의식 저하", "외상/골절"])
            if severe:
                st.error("🚨 **중증 의심** — 즉시 대형병원 응급실로 이동하세요")
            else:
                st.success("✅ **경증 판정** — 아래 대체 병원을 이용하세요")
                st.markdown("#### 📍 추천 야간 진료 병원")
                for h in [
                    {"name": "부산 달빛어린이병원", "dist": "1.2km", "wait": "15분", "open": "24시간"},
                    {"name": "해운대 야간 의원",    "dist": "2.1km", "wait": "20분", "open": "23:00까지"},
                    {"name": "서면 24시 내과의원",  "dist": "3.4km", "wait": "5분",  "open": "24시간"},
                ]:
                    st.markdown(f"**{h['name']}** · {h['dist']} · 대기 {h['wait']} · {h['open']}")
        else:
            st.warning("증상을 하나 이상 선택해주세요")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "분석":
    st.markdown('<div class="pg-title">분석</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">응급실 데이터 심층 분석</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{svg("chart","#2563eb")} 병원별 대기시간</div>', unsafe_allow_html=True)
        fig3 = px.bar(df_h, x="병원명", y="대기(분)", color="혼잡도",
                      color_discrete_map={"혼잡": "#ef4444", "보통": "#f59e0b", "여유": "#10b981"})
        fig3.update_layout(height=250, plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
                           margin=dict(l=0,r=0,t=0,b=0),
                           font=dict(family="Pretendard,Inter", size=11),
                           xaxis=dict(gridcolor="#e2e8f0", tickangle=-15),
                           yaxis=dict(gridcolor="#e2e8f0"))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{svg("bed","#2563eb")} 병상 가용률</div>', unsafe_allow_html=True)
        df_h["가용률(%)"] = (df_h["가용병상"] / df_h["전체병상"] * 100).round(1)
        fig4 = px.bar(df_h, x="병원명", y="가용률(%)", color_discrete_sequence=["#2563eb"])
        fig4.update_layout(height=250, plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
                           margin=dict(l=0,r=0,t=0,b=0),
                           font=dict(family="Pretendard,Inter", size=11),
                           xaxis=dict(gridcolor="#e2e8f0", tickangle=-15),
                           yaxis=dict(gridcolor="#e2e8f0"))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#94a3b8;font-size:11px;'>데이터 출처 : 국립중앙의료원 응급의료 공공데이터 | 프로토타입 v0.3</div>", unsafe_allow_html=True)
