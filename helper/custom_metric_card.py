import streamlit as st

def metric_card(title, icon, content, description, color, text_color="white"):
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 10px 20px; border-radius: 20px">
            <h6 style="margin: 0px; font-size:13px; color:{text_color}">{title}</h6>
            <h2 style="margin: -25px 0px -15px; font-size:25px; color:{text_color}">
                <i class="{icon}" style="margin-right: 10px;"></i>{content}</h2>
            <p style="margin: 0px; font-size:12px; color:{text_color}">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
        """,
        unsafe_allow_html=True
    )
