import random
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Monty Hall Class Experiment", layout="centered", page_icon="🚪")

st.title("🚪 The Monty Hall Experiment")
st.write("Play a round to contribute to our live class probability dataset!")

# Initialize session state for game flow
if "game_stage" not in st.session_state:
    st.session_state.game_stage = "start"

if st.session_state.game_stage == "start":
    if st.button("Start New Game", type="primary"):
        st.session_state.car_door = random.randint(1, 3)
        st.session_state.game_stage = "first_choice"
        st.rerun()

elif st.session_state.game_stage == "first_choice":
    st.subheader("Step 1: Pick a door")
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

elif st.session_state.game_stage == "host_reveal":
    # Host reveals a door with a goat that isn't the car and wasn't picked
    available_to_reveal = [
        d for d in [1, 2, 3]
        if d != st.session_state.user_pick and d != st.session_state.car_door
    ]
    st.session_state.revealed_door = random.choice(available_to_reveal)
    
    # The remaining unopened door to switch to
    remaining_doors = [
        d for d in [1, 2, 3]
        if d != st.session_state.user_pick and d != st.session_state.revealed_door
    ]
    st.session_state.other_unopened = remaining_doors[0]
    
    st.info(f"The host opens **Door {st.session_state.revealed_door}** to reveal a 🐐 **GOAT**!")
    st.subheader("Step 2: Do you want to STAY or SWITCH?")
    
    col_stay, col_switch = st.columns(2)
    with col_stay:
        if st.button(f"STAY with Door {st.session_state.user_pick}", use_container_width=True):
            st.session_state.final_pick = st.session_state.user_pick
            st.session_state.strategy = "Stay"
            st.session_state.game_stage = "results"
            st.rerun()
    with col_switch:
        if st.button(f"SWITCH to Door {st.session_state.other_unopened}", type="primary", use_container_width=True):
            st.session_state.final_pick = st.session_state.other_unopened
            st.session_state.strategy = "Switch"
            st.session_state.game_stage = "results"
            st.rerun()

elif st.session_state.game_stage == "results":
    won = (st.session_state.final_pick == st.session_state.car_door)
    result_str = "Win (Car)" if won else "Loss (Goat)"
    
    if won:
        st.balloons()
        st.success("🎉 CONGRATULATIONS! You won the 🚗 CAR!")
    else:
        st.error("🐐 Bummer! You got a GOAT!")
        
    st.write(f"**Strategy Used:** {st.session_state.strategy}")
    st.write(f"**Result:** {result_str}")
    
    # --- LOG TO GOOGLE SHEETS ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existing = conn.read()
        new_row_df = pd.DataFrame([{"Strategy": st.session_state.strategy, "Result": result_str}])
        
        if df_existing is not None and not df_existing.empty:
            updated_df = pd.concat([df_existing, new_row_df], ignore_index=True)
        else:
            updated_df = new_row_df
            
        conn.update(data=updated_df)
        st.caption("✅ Result recorded in class dataset!")
    except Exception as e:
        st.caption("Note: Working in offline mode or waiting for GSheets secret setup.")

    if st.button("Play Again", type="primary"):
        st.session_state.game_stage = "start"
        st.rerun()
