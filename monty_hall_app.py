import random
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MAT 120: Monty Hall Experiment",
    page_icon="🚪",
    layout="centered"
)

st.title("🚪 MAT 120: The Monty Hall Experiment")
st.markdown("""
Welcome! We are testing probability theory in real-time. 
Play a round below, and your choice (**Stay** vs. **Switch**) and outcome (**Win** vs. **Loss**) 
will be added to our live class dataset!
""")

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "game_stage" not in st.session_state:
    st.session_state.game_stage = "start"

# -----------------------------------------------------------------------------
# GAME STAGE 1: START NEW GAME
# -----------------------------------------------------------------------------
if st.session_state.game_stage == "start":
    st.info("Press the button below to start a new round!")
    if st.button("🎮 Start New Round", use_container_width=True):
        st.session_state.car_door = random.randint(1, 3)
        st.session_state.game_stage = "first_choice"
        st.rerun()

# -----------------------------------------------------------------------------
# GAME STAGE 2: FIRST DOOR CHOICE
# -----------------------------------------------------------------------------
elif st.session_state.game_stage == "first_choice":
    st.subheader("Step 1: Pick a Door")
    st.write("Behind one door is a 🚗 **NEW CAR**! Behind the other two are 🐐 **GOATS**.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚪 Door 1", use_container_width=True):
            st.session_state.user_pick = 1
            st.session_state.game_stage = "host_reveal"
            st.rerun()
    with col2:
        if st.button("🚪 Door 2", use_container_width=True):
            st.session_state.user_pick = 2
            st.session_state.game_stage = "host_reveal"
            st.rerun()
    with col3:
        if st.button("🚪 Door 3", use_container_width=True):
            st.session_state.user_pick = 3
            st.session_state.game_stage = "host_reveal"
            st.rerun()

# -----------------------------------------------------------------------------
# GAME STAGE 3: HOST REVEALS A GOAT & DECISION (STAY vs SWITCH)
# -----------------------------------------------------------------------------
elif st.session_state.game_stage == "host_reveal":
    user_pick = st.session_state.user_pick
    car_door = st.session_state.car_door
    
    # The host must reveal a goat door that the user didn't pick
    available_to_reveal = [d for d in [1, 2, 3] if d != user_pick and d != car_door]
    revealed_door = random.choice(available_to_reveal)
    
    # Identify the remaining unopened door
    other_door = [d for d in [1, 2, 3] if d != user_pick and d != revealed_door][0]
    
    st.session_state.revealed_door = revealed_door
    st.session_state.other_door = other_door
    
    st.warning(f"🐐 **Host Action:** The host opens **Door {revealed_door}**, revealing a **GOAT**!")
    st.subheader(f"You initially chose Door {user_pick}.")
    st.write("Now, make your final choice:")
    
    col_stay, col_switch = st.columns(2)
    with col_stay:
        if st.button(f"🔒 STAY with Door {user_pick}", use_container_width=True):
            st.session_state.final_pick = user_pick
            st.session_state.strategy = "Stay"
            st.session_state.game_stage = "results"
            st.rerun()
            
    with col_switch:
        if st.button(f"🔄 SWITCH to Door {other_door}", use_container_width=True):
            st.session_state.final_pick = other_door
            st.session_state.strategy = "Switch"
            st.session_state.game_stage = "results"
            st.rerun()

# -----------------------------------------------------------------------------
# GAME STAGE 4: RESULTS & LOGGING TO GOOGLE SHEETS
# -----------------------------------------------------------------------------
elif st.session_state.game_stage == "results":
    final_pick = st.session_state.final_pick
    car_door = st.session_state.car_door
    strategy = st.session_state.strategy
    
    won = (final_pick == car_door)
    result_str = "Win" if won else "Loss"
    
    st.divider()
    if won:
        st.balloons()
        st.success(f"🎉 **YOU WON THE CAR!** 🚗 (It was behind Door {car_door})")
    else:
        st.error(f"🐐 **YOU GOT A GOAT!** (The car was behind Door {car_door})")
        
    st.write(f"**Your Strategy:** `{strategy}` | **Outcome:** `{result_str}`")
    
    # --- LOG TO GOOGLE SHEET ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Read current class data without caching so updates are live
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        
        new_row = pd.DataFrame([{"Strategy": strategy, "Result": result_str}])
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        
        conn.update(worksheet="Sheet1", data=updated_data)
        st.caption("✅ Result successfully recorded in the class Google Sheet!")
    except Exception as e:
        st.info("ℹ️ Game complete! (Note: Connect Streamlit GSheets secrets to log results live).")
        
    st.divider()
    if st.button("🔄 Play Again", use_container_width=True):
        st.session_state.game_stage = "start"
        st.rerun()
