import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime
import random, platform
import matplotlib.pyplot as plt

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="응급실 대기 예측", page_icon="🏥",
                   layout="wide", initial_sidebar_state="expanded")

# ── session_state ────────────────────────────────────────
if "menu" not in st.session_state:
    st.session_state.menu = "대시보드"
if "sb_open" not in st.session_state:
    st.session_state.sb_open = True

# ── 데이터 ───────────────────────────────────────────────
@st.cache_data
def load_data():
    random.seed(42); np.random.seed(42)
    hospitals = [
        {"name":"부산대학교병원",    "lat":35.1318,"lon":129.1026,"level":"권역"},
        {"name":"고신대학교복음병원","lat":35.0960,"lon":128.9788,"level":"지역"},
        {"name":"동아대학교병원",    "lat":35.1042,"lon":128.9749,"level":"권역"},
        {"name":"해운대백병원",      "lat":35.1637,"lon":129.1696,"level":"지역"},
        {"name":"부산성모병원",      "lat":35.1547,"lon":129.0607,"level":"지역"},
    ]
    data = []
    for h in hospitals:
        wait = random.randint(20,240); bt = random.randint(30,80); ba = random.randint(0,bt//2)
        cong = "혼잡" if wait>120 else ("보통" if wait>60 else "여유")
        data.append({"병원명":h["name"],"위도":h["lat"],"경도":h["lon"],
                     "등급":h["level"],"대기(분)":wait,"전체병상":bt,"가용병상":ba,"혼잡도":cong})
    df_h = pd.DataFrame(data)
    td = {}
    for h in hospitals[:3]:
        base, vals = random.randint(60,120), []
        for hr in range(24):
            v = base*(0.6 if hr<6 else 1.2 if hr<9 else 1.5 if hr<18 else 1.8 if hr<22 else 1.3)
            vals.append(int(v+random.randint(-10,10)))
        td[h["name"]] = vals
    df_t = pd.DataFrame(td, index=range(24))
    df_k = pd.DataFrame({
        "등급":["1등급 소생","2등급 긴급","3등급 응급","4등급 준응급","5등급 비응급"],
        "환자":[12,45,180,320,290],
        "색":["#ff6b6b","#ffa94d","#748ffc","#69db7c","#adb5bd"]
    })
    return df_h, df_t, df_k

df_h, df_t, df_k = load_data()
tabs       = ["대시보드","지도","AI 문진","분석"]
menu_icons = ["▦","◉","⊕","▲"]
menu    = st.session_state.menu
sb_open = st.session_state.sb_open

# ── 사이드바 ─────────────────────────────────────────────
with st.sidebar:
    # 토글
    tog = "◀ 접기" if sb_open else "▶"
    if st.button(tog, key="tog", use_container_width=sb_open):
        st.session_state.sb_open = not sb_open
        st.rerun()

    if sb_open:
        st.markdown("---")
        for lbl, icon in zip(tabs, menu_icons):
            active = lbl == menu
            label  = f"{icon}  {lbl}"
            if st.button(label, key=f"nav_{lbl}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.menu = lbl
                st.rerun()
        st.markdown("---")
        st.caption("⚙ 설정")
        st.caption("→ 로그아웃")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        for lbl, icon in zip(tabs, menu_icons):
            active = lbl == menu
            if st.button(icon, key=f"nav_{lbl}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.menu = lbl
                st.session_state.sb_open = True
                st.rerun()

# ── CSS ─────────────────────────────────────────────────
SB_W = 220 if sb_open else 72
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*,html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;box-sizing:border-box;}}
.stApp{{background:#f0f2ff;}}

[data-testid="stSidebarHeader"],
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"],
[data-testid="stAppToolbar"],
[data-testid="stMainMenu"]{{display:none!important;}}
div[data-testid="metric-container"]{{display:none!important;}}

/* 사이드바 크기·배경 */
[data-testid="stSidebar"]{{
    background:#2d2b55!important;
    min-width:{SB_W}px!important;
    max-width:{SB_W}px!important;
}}
[data-testid="stSidebar"]>div:first-child{{
    background:#2d2b55!important;
    padding:{"16px 12px" if sb_open else "16px 8px"}!important;
}}

/* 사이드바 버튼 공통 */
[data-testid="stSidebar"] button{{
    background:transparent!important;
    border:none!important;
    color:rgba(255,255,255,0.45)!important;
    font-size:{"13px" if sb_open else "20px"}!important;
    font-weight:500!important;
    text-align:{"left" if sb_open else "center"}!important;
    border-radius:10px!important;
    box-shadow:none!important;
    transition:background .12s,color .12s!important;
    width:100%!important;
    padding:{"9px 12px" if sb_open else "10px 0"}!important;
    line-height:1.2!important;
}}
[data-testid="stSidebar"] button:hover{{
    background:rgba(255,255,255,0.08)!important;
    color:rgba(255,255,255,0.9)!important;
}}
[data-testid="stSidebar"] button[kind="primary"]{{
    background:#7c6fcd!important;
    color:#fff!important;
    font-weight:600!important;
}}
[data-testid="stSidebar"] button[kind="primary"]:hover{{
    background:#6d5fc0!important;
}}

/* 토글 버튼 */
[data-testid="stSidebar"] [data-testid="stButton"]:first-child button{{
    color:rgba(255,255,255,0.3)!important;
    font-size:12px!important;
    padding:6px 10px!important;
    text-align:{"left" if sb_open else "center"}!important;
}}

/* hr */
[data-testid="stSidebar"] hr{{
    border-color:rgba(255,255,255,0.1)!important;
    margin:8px 0!important;
}}
/* caption */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{{
    color:rgba(255,255,255,0.28)!important;
    padding:4px 2px!important;
}}

/* 메인 */
.main .block-container{{padding:24px 28px!important;max-width:100%!important;}}
.pg-title{{font-size:24px;font-weight:700;color:#1a1a2e;letter-spacing:-0.03em;}}
.pg-sub{{font-size:13px;color:#868e96;margin-top:2px;margin-bottom:20px;}}
.kpi-card{{background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.05);}}
.kpi-card.accent{{background:linear-gradient(135deg,#7c6fcd 0%,#5f4fc4 100%);}}
.kpi-card.accent .kpi-label{{color:rgba(255,255,255,.7);}}
.kpi-card.accent .kpi-value{{color:#fff;}}
.kpi-card.accent .kpi-delta{{color:rgba(255,255,255,.85);}}
.kpi-label{{font-size:12px;font-weight:500;color:#868e96;margin-bottom:6px;}}
.kpi-value{{font-size:26px;font-weight:700;color:#1a1a2e;letter-spacing:-0.03em;line-height:1;}}
.kpi-delta{{font-size:12px;font-weight:500;margin-top:8px;}}
.delta-up{{color:#40c057;}}.delta-dn{{color:#fa5252;}}
.sc{{background:transparent;padding:0;margin-bottom:16px;}}
.sc-title{{font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:14px;
           display:flex;align-items:center;justify-content:space-between;}}
.badge{{display:inline-flex;align-items:center;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;}}
.badge-red{{background:#fff5f5;color:#fa5252;}}
.badge-amber{{background:#fff9db;color:#f59f00;}}
.badge-green{{background:#ebfbee;color:#40c057;}}
.badge-purple{{background:#f3f0ff;color:#7c6fcd;}}
.tl-item{{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid #f8f9fa;}}
.tl-dot{{width:8px;height:8px;border-radius:50%;margin-top:5px;flex-shrink:0;}}
.tl-name{{font-size:13px;font-weight:500;color:#1a1a2e;}}
.tl-sub{{font-size:12px;color:#868e96;margin-top:2px;}}
</style>
""", unsafe_allow_html=True)

# ── 페이지 제목 ──────────────────────────────────────────
st.markdown(f"""
<div class="pg-title">{menu}</div>
<div class="pg-sub">부산 권역 응급실 실시간 현황 · {datetime.now().strftime('%H:%M')} 기준</div>
""", unsafe_allow_html=True)

# ── 대시보드 ─────────────────────────────────────────────
if menu == "대시보드":
    avg_wait  = int(df_h["대기(분)"].mean())
    tot_beds  = df_h["가용병상"].sum()
    congested = len(df_h[df_h["혼잡도"]=="혼잡"])

    c1,c2,c3,c4 = st.columns(4)
    for col,accent,label,val,dcls,delta in [
        (c1,True, "평균 대기시간", f"{avg_wait}분","delta-dn","↑ +12분"),
        (c2,False,"총 가용 병상",  f"{tot_beds}개","delta-up","↑ +1.2%"),
        (c3,False,"혼잡 병원 수",  f"{congested}개","delta-dn","↓ 즉시 분산"),
        (c4,False,"경증 환자 비율","61.0%",        "delta-up","↑ +0.5%"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card {"accent" if accent else ""}">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{val}</div>
              <div class="kpi-delta {dcls}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_g, col_tl = st.columns([1.8,1])

    with col_g:
        st.markdown('<div class="sc"><div class="sc-title"><span>📈 시간대별 대기시간 예측</span><span class="badge badge-purple">실시간</span></div>', unsafe_allow_html=True)
        selected = st.multiselect("", df_t.columns.tolist(), default=df_t.columns.tolist()[:2], label_visibility="collapsed")
        if selected:
            fig = go.Figure()
            pal = ["#7c6fcd","#69db7c","#ffa94d"]
            fp  = ["rgba(124,111,205,.1)","rgba(105,219,124,.1)","rgba(255,169,77,.1)"]
            for i,c in enumerate(selected):
                fig.add_trace(go.Scatter(x=list(range(24)),y=df_t[c],name=c,mode='lines',
                    line=dict(color=pal[i%3],width=2.5,shape='spline',smoothing=1.2),
                    fill='tozeroy',fillcolor=fp[i%3],hovertemplate="%{y}분<extra></extra>"))
            fig.add_hline(y=120,line_dash="dot",line_color="#fa5252",line_width=1,
                annotation_text="혼잡 기준",annotation_font_color="#fa5252",annotation_position="right")
            fig.update_layout(height=240,plot_bgcolor="#fff",paper_bgcolor="#fff",
                margin=dict(l=0,r=10,t=10,b=0),font=dict(color="#1a1a2e",size=11),
                legend=dict(bgcolor="rgba(255,255,255,.9)",bordercolor="#f1f3f5",borderwidth=1,
                    orientation="h",yanchor="bottom",y=1.02,x=0),
                xaxis=dict(gridcolor="#f1f3f5",tickmode="array",tickvals=list(range(0,24,3)),
                    ticktext=[f"{h}시" for h in range(0,24,3)],showline=False,zeroline=False),
                yaxis=dict(gridcolor="#f1f3f5",title="대기(분)",showline=False,zeroline=False),
                hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tl:
        st.markdown('<div class="sc"><div class="sc-title">🏥 실시간 현황</div>', unsafe_allow_html=True)
        for cong,name,detail,color in [
            ("혼잡",df_h.iloc[0]["병원명"],f"대기 {df_h.iloc[0]['대기(분)']}분","#fa5252"),
            ("보통",df_h.iloc[2]["병원명"],f"대기 {df_h.iloc[2]['대기(분)']}분","#f59f00"),
            ("여유",df_h.iloc[3]["병원명"],f"대기 {df_h.iloc[3]['대기(분)']}분","#40c057"),
            ("보통",df_h.iloc[4]["병원명"],f"가용 {df_h.iloc[4]['가용병상']}병상","#f59f00"),
            ("혼잡",df_h.iloc[1]["병원명"],f"대기 {df_h.iloc[1]['대기(분)']}분","#fa5252"),
        ]:
            bc = "badge-red" if cong=="혼잡" else ("badge-amber" if cong=="보통" else "badge-green")
            st.markdown(f"""<div class="tl-item">
              <div class="tl-dot" style="background:{color}"></div>
              <div style="flex:1"><div style="display:flex;justify-content:space-between;align-items:center">
                <div class="tl-name">{name}</div><span class="badge {bc}">{cong}</span>
              </div><div class="tl-sub">{detail}</div></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_tb, col_ktas = st.columns([1.4,1])
    with col_tb:
        st.markdown('<div class="sc"><div class="sc-title">📋 응급실 현황</div>', unsafe_allow_html=True)
        def cc(v): return "color:#fa5252;font-weight:600" if v=="혼잡" else ("color:#f59f00;font-weight:600" if v=="보통" else "color:#40c057;font-weight:600")
        def cw(v): return "color:#fa5252" if v>120 else ("color:#f59f00" if v>60 else "color:#40c057")
        st.dataframe(df_h[["병원명","등급","대기(분)","가용병상","혼잡도"]].style.map(cc,subset=["혼잡도"]).map(cw,subset=["대기(분)"]),
            use_container_width=True, hide_index=True, height=200)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_ktas:
        st.markdown('<div class="sc"><div class="sc-title">👥 KTAS 환자 분포</div>', unsafe_allow_html=True)
        total = df_k["환자"].sum()
        fig2 = go.Figure(go.Pie(labels=df_k["등급"],values=df_k["환자"],hole=0.62,
            marker=dict(colors=df_k["색"].tolist(),line=dict(color="#fff",width=3)),
            textinfo="percent",textfont=dict(size=11),hovertemplate="%{label}<br>%{value}명<extra></extra>"))
        fig2.add_annotation(text=f"<b>{total}</b><br>총 환자",x=0.5,y=0.5,showarrow=False,
            font=dict(size=14,color="#1a1a2e"),align="center")
        fig2.update_layout(height=200,paper_bgcolor="#fff",margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(orientation="v",font=dict(size=10,color="#868e96"),bgcolor="rgba(0,0,0,0)",x=1,y=0.5))
        st.plotly_chart(fig2, use_container_width=True)
        mild = df_k[df_k["등급"].str.contains("4등급|5등급")]["환자"].sum()
        st.markdown(f'<div style="font-size:12px;color:#868e96;">경증 비율 <b style="color:#7c6fcd">{mild/total*100:.1f}%</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "지도":
    st.markdown('<div class="sc"><div class="sc-title"><span>🗺 병원 위치</span><span class="badge badge-purple">부산 권역</span></div>', unsafe_allow_html=True)
    m = folium.Map(location=[35.13,129.05],zoom_start=12,tiles='CartoDB positron')
    cmap = {'혼잡':'red','보통':'beige','여유':'green'}
    for _,row in df_h.iterrows():
        folium.Marker([row['위도'],row['경도']],
            popup=folium.Popup(f"<b>{row['병원명']}</b><br>대기:{row['대기(분)']}분 / 병상:{row['가용병상']}/{row['전체병상']}",max_width=200),
            tooltip=f"{row['병원명']} ({row['혼잡도']})",
            icon=folium.Icon(color=cmap[row['혼잡도']],icon='plus-sign',prefix='glyphicon')).add_to(m)
    folium.Marker([35.1796,129.0756],tooltip="📍 현재 위치",
        icon=folium.Icon(color='purple',icon='user',prefix='glyphicon')).add_to(m)
    st_folium(m, width=None, height=520)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "AI 문진":
    st.markdown('<div class="sc"><div class="sc-title">🤖 증상 선택</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#868e96;">해당하는 증상을 선택하면 경증/중증 여부를 판별해 드립니다</p>', unsafe_allow_html=True)
    syms = ["발열 (38도 이상)","두통","복통","호흡곤란","가슴 통증","구토/설사","외상/골절","의식 저하","단순 감기","피부 발진"]
    ca, cb = st.columns(2); sel = []
    for i,s in enumerate(syms):
        with ca if i%2==0 else cb:
            if st.checkbox(s, key=f"s{i}"): sel.append(s)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("중증도 판별", key="check"):
        if sel:
            if any(s in sel for s in ["호흡곤란","가슴 통증","의식 저하","외상/골절"]):
                st.error("🚨 중증 의심 — 즉시 대형병원 응급실로 이동하세요")
            else:
                st.success("✅ 경증 판정 — 아래 대체 병원을 이용하세요")
                for h in [{"name":"부산 달빛어린이병원","dist":"1.2km","wait":"15분","open":"24시간"},
                           {"name":"해운대 야간 의원","dist":"2.1km","wait":"20분","open":"23:00까지"},
                           {"name":"서면 24시 내과의원","dist":"3.4km","wait":"5분","open":"24시간"}]:
                    st.markdown(f"**{h['name']}** · {h['dist']} · 대기 {h['wait']} · {h['open']}")
        else: st.warning("증상을 하나 이상 선택해주세요")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "분석":
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sc"><div class="sc-title">📊 병원별 대기시간</div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(x=df_h["대기(분)"],y=df_h["병원명"],orientation='h',
            marker=dict(color=df_h["대기(분)"],colorscale=[[0,"#69db7c"],[.5,"#ffa94d"],[1,"#ff6b6b"]],
                showscale=False,line=dict(width=0)),
            text=df_h["대기(분)"].astype(str)+"분",textposition='outside'))
        fig3.update_layout(height=250,plot_bgcolor="#fff",paper_bgcolor="#fff",
            margin=dict(l=0,r=60,t=0,b=0),font=dict(color="#1a1a2e",size=11),
            xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
            yaxis=dict(showgrid=False,tickangle=0))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="sc"><div class="sc-title">🛏 병상 가용률</div>', unsafe_allow_html=True)
        df_h["가용률(%)"] = (df_h["가용병상"]/df_h["전체병상"]*100).round(1)
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_h["병원명"],y=df_h["전체병상"],name="전체병상",
            marker_color="rgba(124,111,205,.15)",marker_line_width=0))
        fig4.add_trace(go.Bar(x=df_h["병원명"],y=df_h["가용병상"],name="가용병상",
            marker_color="#7c6fcd",marker_line_width=0))
        fig4.update_layout(height=250,plot_bgcolor="#fff",paper_bgcolor="#fff",
            barmode='overlay',margin=dict(l=0,r=0,t=0,b=0),font=dict(color="#1a1a2e",size=11),
            xaxis=dict(gridcolor="#f1f3f5",tickangle=0),yaxis=dict(gridcolor="#f1f3f5"),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=11)))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center;color:#adb5bd;font-size:11px;padding:12px;'>국립중앙의료원 응급의료 공공데이터 | 프로토타입 v0.6</div>", unsafe_allow_html=True)
