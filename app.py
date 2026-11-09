import streamlit as st
import random
import json
import os

# ==========================================
# 1. 頁面與視覺設定
# ==========================================
st.set_page_config(page_title="凡事靠自己 - 隱藏任務", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .main-title { text-align: center; color: #d9534f; font-size: 3rem; font-weight: 900; }
    .question-box { font-size: 4rem; text-align: center; font-weight: bold; color: #333; background: #f0f2f6; padding: 20px; border-radius: 15px; margin: 20px 0; }
    .prize-text { color: #28a745; font-size: 3rem; font-weight: bold; text-align: center; margin: 20px 0; animation: pulse 1s infinite; }
    .winner-board { background: #fff3cd; padding: 20px; border-radius: 10px; border: 2px dashed #ffc107; margin-top: 30px; }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 全域中獎名單資料庫設定 (winners.json)
# ==========================================
WINNERS_FILE = "winners.json"

def load_winners():
    """讀取中獎名單"""
    if os.path.exists(WINNERS_FILE):
        with open(WINNERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_winner(name, prize):
    """將新中獎者存入名單"""
    winners = load_winners()
    winners.append({"name": name, "prize": prize})
    with open(WINNERS_FILE, "w", encoding="utf-8") as f:
        json.dump(winners, f, ensure_ascii=False)

# ==========================================
# 3. 初始化 Session State (記憶個人狀態)
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = "login" # 步驟：login (登入) -> math (算數學) -> reward (領獎)
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "math_q" not in st.session_state:
    # 隨機產生千位數的數學題 (加法或乘法)
    if random.choice(["+", "x"]) == "+":
        a, b = random.randint(500, 5000), random.randint(500, 4999)
        st.session_state.math_q = f"{a} + {b}"
        st.session_state.math_a = a + b
    else:
        a, b = random.randint(30, 99), random.randint(30, 99)
        st.session_state.math_q = f"{a} × {b}"
        st.session_state.math_a = a * b
if "prize" not in st.session_state:
    st.session_state.prize = 0

# ==========================================
# 4. 遊戲流程畫面
# ==========================================
st.markdown('<div class="main-title">💪 凡事靠自己</div>', unsafe_allow_html=True)

# --- 步驟 1：輸入姓名 ---
if st.session_state.step == "login":
    st.info("🔎 恭喜你找到隱藏的 QR Code！請輸入你的名字來挑戰領取獎金：")
    name_input = st.text_input("👤 你的名字是？")
    
    if st.button("開始挑戰 🚀", use_container_width=True, type="primary"):
        if name_input.strip() == "":
            st.error("⚠️ 名字不能空白喔！")
        else:
            st.session_state.user_name = name_input
            st.session_state.step = "math"
            st.rerun()

# --- 步驟 2：解數學題 ---
elif st.session_state.step == "math":
    st.write(f"哈囉 **{st.session_state.user_name}**！解開這道題目，獎金就是你的！")
    
    st.markdown(f'<div class="question-box">{st.session_state.math_q} = ?</div>', unsafe_allow_html=True)
    
    user_answer = st.number_input("✍️ 請輸入答案：", step=1, value=0)
    
    if st.button("送出答案 ✨", use_container_width=True, type="primary"):
        if user_answer == st.session_state.math_a:
            st.balloons()
            # 隨機抽出 200 或 500 元
            st.session_state.prize = random.choice([200, 500])
            # 把名字跟獎金存入共用資料庫
            save_winner(st.session_state.user_name, st.session_state.prize)
            st.session_state.step = "reward"
            st.rerun()
        else:
            st.error("❌ 哎呀！算錯囉，再檢查一下吧！")

# --- 步驟 3：領取獎金與英雄榜 ---
elif st.session_state.step == "reward":
    st.success("🎉 太神啦！完全正確！")
    st.markdown(f'<div class="prize-text">💰 恭喜獲得 {st.session_state.prize} 元！</div>', unsafe_allow_html=True)
    st.write("👉 請拿著這個畫面，去主桌找長官領取你的獎金！")
    
    st.markdown("---")
    
    # 讀取並顯示全場的中獎名單
    winners = load_winners()
    st.markdown('<div class="winner-board">', unsafe_allow_html=True)
    st.markdown("### 🏆 目前成功領取獎金的英雄榜")
    if winners:
        for i, w in enumerate(winners[::-1]): # 反轉順序讓最新中獎的人在最上面
            st.markdown(f"- **{w['name']}** 成功解題，抱走 **{w['prize']} 元**！")
    else:
        st.write("目前還沒有人中獎。")
    st.markdown('</div>', unsafe_allow_html=True)
