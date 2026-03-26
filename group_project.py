################################################################
# Ricardo
################################################################


################################################################
# Jacek
################################################################


################################################################
# Alberto
################################################################


################################################################
# Shadi
################################################################


################################################################
# Mateus 
################################################################
p1_moves = damaging_moves_for_pokemon(p1["id"], p1["moves"], limit=8)
    p2_moves = damaging_moves_for_pokemon(p2["id"], p2["moves"], limit=8)

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(f"### {p1_name}")
        for mv in p1_moves:
            move_name = mv["name"].replace("-", " ").title()
            c_btn, c_badge = st.columns([1, 1], gap="small")
            with c_btn:
                if st.button(move_name, key=f"p1_move_{mv['name']}", type="primary"):
                    st.session_state["p1_move"] = mv
            with c_badge:
                st.markdown(
                    f"<div style='display:flex; align-items:center; height:64px;'>"
                    f"{type_badge_html(mv['type'])}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        chosen = st.session_state.get("p1_move")
        if chosen:
            st.info(
                f"**Move Selected:** {chosen['name'].replace('-', ' ').title()}  \n"
                f"**Power:** {chosen['power']}  \n"
                f"**Accuracy:** {chosen['accuracy']}  \n"
                f"**Type:** {chosen['type'].title()}  \n"
                f"**Class:** {chosen['damage_class'].title()}"
            )

    with right:
        st.markdown(f"### {p2_name}")
        for mv in p2_moves:
            move_name = mv["name"].replace("-", " ").title()
            c_btn, c_badge = st.columns([1, 1], gap="small")
            with c_btn:
                if st.button(move_name, key=f"p2_move_{mv['name']}", type="primary"):
                    st.session_state["p2_move"] = mv
            with c_badge:
                st.markdown(
                    f"<div style='display:flex; align-items:center; height:64px;'>"
                    f"{type_badge_html(mv['type'])}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        chosen = st.session_state.get("p2_move")
        if chosen:
            st.info(
                f"**Move Selected:** {chosen['name'].replace('-', ' ').title()}  \n"
                f"**Power:** {chosen['power']}  \n"
                f"**Accuracy:** {chosen['accuracy']}  \n"
                f"**Type:** {chosen['type'].title()}  \n"
                f"**Class:** {chosen['damage_class'].title()}"
            )

    st.divider()

################################################################
# Blanca
################################################################