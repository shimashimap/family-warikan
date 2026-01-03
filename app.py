import streamlit as st

def calculate_settlement(payments):
    total = sum(payments.values())
    num_people = len(payments)
    if num_people == 0: return []
    average = total / num_people
    
    # 各自の過不足を計算 (支払い額 - 平均)
    balances = {name: amount - average for name, amount in payments.items()}
    
    receivers = sorted([(name, bal) for name, bal in balances.items() if bal > 0], key=lambda x: x[1], reverse=True)
    payers = sorted([(name, -bal) for name, bal in balances.items() if bal < 0], key=lambda x: x[1], reverse=True)
    
    settlements = []
    
    # 精算アルゴリズム (多い人から順に相殺)
    p_idx, r_idx = 0, 0
    while p_idx < len(payers) and r_idx < len(receivers):
        p_name, p_amount = payers[p_idx]
        r_name, r_amount = receivers[r_idx]
        
        transfer = min(p_amount, r_amount)
        if transfer > 0:
            settlements.append(f"💰 **{p_name}** → **{r_name}** へ **{int(transfer)}円** 渡す")
        
        payers[p_idx] = (p_name, p_amount - transfer)
        receivers[r_idx] = (r_name, r_amount - transfer)
        
        if payers[p_idx][1] <= 0: p_idx += 1
        if receivers[r_idx][1] <= 0: r_idx += 1
            
    return settlements, total, average

# --- UI部分 ---
st.title("🏠 我が家の持ち寄り精算システム")
st.write("各自が払った金額を入力してください。`1500 + 300 - 200` のような計算も可能です。")

if 'members' not in st.session_state:
    st.session_state.members = ["お父さん", "お母さん"]

# メンバー追加機能
new_member = st.sidebar.text_input("メンバー追加")
if st.sidebar.button("追加") and new_member:
    if new_member not in st.session_state.members:
        st.session_state.members.append(new_member)

# 入力フォーム
payments = {}
st.subheader("💡 支払い情報の入力")
for name in st.session_state.members:
    expr = st.text_input(f"{name} の支払い額 (数式OK)", value="0", key=name)
    try:
        # 入力された文字列を計算（安全のためevalの代わりに簡単な計算のみ許可する実装が望ましいですが、まずはevalで）
        amount = float(eval(expr.replace(' ', '')))
        payments[name] = amount
    except:
        st.error(f"{name} の入力が正しくありません")
        payments[name] = 0

if st.button("精算を実行する"):
    settlements, total, average = calculate_settlement(payments)
    
    st.divider()
    st.subheader("📊 精算結果")
    col1, col2 = st.columns(2)
    col1.metric("合計金額", f"{int(total)}円")
    col2.metric("1人あたりの平均", f"{int(average)}円")
    
    if settlements:
        for s in settlements:
            st.info(s)
    else:
        st.success("全員公平です！精算の必要はありません。")
