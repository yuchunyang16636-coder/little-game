import streamlit as st
import random
import json
import os
import time

# ==========================================
# 1. 頁面與視覺設定 (俏皮風格 CSS)
# ==========================================
st.set_page_config(page_title="忘年會 - 終極任務", page_icon="🎉", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@700;900&display=swap');
    html, body, [class*="st-"] { font-family: 'Zen Maru Gothic', sans-serif !important; font-weight: 700 !important; }
    
    .title-text { text-align: center; color: #FF5A5F; font-size: clamp(2rem, 6vw, 4rem); font-weight: 900; text-shadow: 2px 2px 0px #FFD166; margin-bottom: 20px; }
    
    /* 俏皮風格的中獎卡片 */
    .winner-bubble {
        background: linear-gradient(135deg, #FFD166 0%, #FF9F1C 100%);
        border-radius: 50px;
        padding: 15px 30px;
        margin: 15px auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 15px rgba(255, 159, 28, 0.3);
        border: 4px solid #fff;
        max-width: 600px;
        animation: floatUp 0.5s ease-out;
        transition: transform 0.3s ease;
    }
    .winner-bubble:hover { transform: scale(1.05) rotate(-2deg); }
    .winner-name { font-size: 1.8rem; color: #fff; font-weight: 900; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); }
    .winner-prize { background: #fff; color: #E71D36; padding: 5px 20px; border-radius: 30px; font-size: 1.8rem; font-weight: 900; box-shadow: inset 0 3px 6px rgba(0,0,0,0.1); }
    
    @keyframes floatUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* 手機端任務卡片 */
    .task-card {
        background-color: #F8F9FA;
        border: 3px dashed #2EC4B6;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 20px rgba(46, 196, 182, 0.15);
    }
    .task-title { font-size: 1.5rem; color: #2EC4B6; margin-bottom: 10px; }
    .task-desc { font-size: 2rem; color: #333; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 系統設定與資料庫
# ==========================================
WINNERS_FILE = "winners.json"
HOST_PASSWORD = "888" # 🔒 主持人專屬密碼 (可自行修改)

# 隨機題庫 (包含各種題型)
TASK_BANK = [
    {"type": "🧮 數學題", "desc": f"請計算 {random.randint(100, 999)} + {random.randint(100, 999)} = ? (請告訴主持人答案)"},
    {"type": "🤸‍♂️ 動作題", "desc": "請在主持人面前，完成 5 個波比跳！"},
    {"type": "🤸‍♀️ 動作題", "desc": "請對著主持人深情演唱一句你最愛的歌！"},
    {"type": "🕵️‍♂️ 尋寶題", "desc": "請在會場內找到一件『黃色』的物品，並帶給主持人看！"},
    {"type": "🕵️‍♀️ 尋寶題", "desc": "請找到你們部門的主管，跟他/她拍一張兩人比愛心的合照給主持人看！"},
    {"type": "🧠 機智題", "desc": "請講一個能讓主持人笑出來的笑話！"}
]

def load_winners():
    if os.path.exists(WINNERS_FILE):
        with open(WINNERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_winner(name, prize):
    winners = load_winners()
    winners.append({"name": name, "prize": prize})
    with open(WINNERS_FILE, "w", encoding="utf-8") as f:
        json.dump(winners, f, ensure_ascii=False)

# 判斷目前是「大螢幕端」還是「手機玩家端」
params = st.query_params
mode = params.get("mode", "player")

# ==========================================
# 3. 大螢幕端 (Host Mode) : 英雄榜 + QR Code
# ==========================================
if mode == "host":
    st.markdown('<div class="title-text">🎉 忘年會終極任務 🎉</div>', unsafe_allow_html=True)
    
    col_qr, col_board = st.columns([1, 2])
    
    with col_qr:
        st.markdown("### 📱 掃描挑戰！")
        # 👇 這裡請替換成你未來部署在 Streamlit 上的真實網址
        YOUR_APP_URL = "https://your-canon-app.streamlit.app" 
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={YOUR_APP_URL}"
        st.image(qr_url, caption="拿出手機，掃描進入遊戲！", use_container_width=True)
        st.info("完成隱藏任務，尋找主持人解鎖獎金！")
        
    with col_board:
        st.markdown("### 🏆 獎金英雄榜 (即時連線)")
        winners = load_winners()
        if not winners:
            st.write("👀 目前還沒有人完成任務，大家快點動起來！")
        else:
            # 反轉清單，讓最新得獎的在最上面
            for w in winners[::-1]:
                st.markdown(f"""
                    <div class="winner-bubble">
                        <div class="winner-name">👤 {w['name']}</div>
                        <div class="winner-prize">💰 ${w['prize']}</div>
                    </div>
                """, unsafe_allow_html=True)

    # 讓大螢幕每 5 秒自動重新整理一次，抓取最新中獎名單
    time.sleep(5)
    st.rerun()

# ==========================================
# 4. 手機玩家端 (Player Mode) : 任務與解鎖
# ==========================================
else:
    # 玩家狀態記憶
    if "step" not in st.session_state: st.session_state.step = "login"
    if "user_name" not in st.session_state: st.session_state.user_name = ""
    if "task" not in st.session_state: st.session_state.task = random.choice(TASK_BANK)

    st.markdown('<div class="title-text" style="font-size: 2.5rem;">🔥 隱藏挑戰</div>', unsafe_allow_html=True)

    # --- 步驟 1：輸入姓名 ---
    if st.session_state.step == "login":
        st.write("歡迎來到終極挑戰！請輸入你的大名：")
        name_input = st.text_input("👤 你的名字：")
        if st.button("抽任務 🎲", use_container_width=True, type="primary"):
            if name_input:
                st.session_state.user_name = name_input
                st.session_state.step = "task"
                st.rerun()
            else:
                st.error("請輸入名字！")

    # --- 步驟 2：顯示任務，要求主持人輸入密碼 ---
    elif st.session_state.step == "task":
        st.write(f"哈囉 **{st.session_state.user_name}**！你的專屬任務來了：")
        
        # 顯示俏皮任務卡片
        task = st.session_state.task
        st.markdown(f"""
            <div class="task-card">
                <div class="task-title">{task['type']}</div>
                <div class="task-desc">{task['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning("🏃‍♂️ 完成任務後，請將手機交給主持人！")
        st.markdown("---")
        st.write("🕵️‍♂️ **主持人專屬區 (玩家勿動)**")
        
        pwd_input = st.text_input("🔑 主持人請輸入核准密碼：", type="password")
        if st.button("解鎖獎金 🔓", use_container_width=True):
            if pwd_input == HOST_PASSWORD:
                st.balloons()
                prize_pool = [200, 500, 1000] # 可以自己設定獎金級距
                final_prize = random.choice(prize_pool)
                save_winner(st.session_state.user_name, final_prize)
                st.session_state.prize = final_prize
                st.session_state.step = "reward"
                st.rerun()
            else:
                st.error("❌ 密碼錯誤！想偷按啊？")

    # --- 步驟 3：顯示獲得獎金 ---
    elif st.session_state.step == "reward":
        st.success("✅ 主持人已核准！")
        st.markdown(f"""
            <div class="winner-bubble" style="flex-direction: column; text-align: center; margin-top: 30px;">
                <div class="winner-name" style="margin-bottom: 10px; font-size: 2.5rem;">🎉 恭喜過關</div>
                <div class="winner-prize" style="font-size: 3rem;">💰 {st.session_state.prize} 元</div>
            </div>
        """, unsafe_allow_html=True)
        st.info("快抬頭看看大螢幕，你的名字已經上英雄榜囉！")
        
        # 讓玩家可以重新玩 (可選)
        if st.button("換人挑戰 🔄", use_container_width=True):
            st.session_state.step = "login"
            st.session_state.task = random.choice(TASK_BANK)
            st.rerun()
