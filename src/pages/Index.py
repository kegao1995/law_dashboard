import streamlit as st
# 设置页面宽度
st.set_page_config(layout="wide")
pages = {
    "Data": [
        st.Page("A34_Refused_Data.py", title="A34 Refused Data"),
    ],

}
pg = st.navigation(pages)
pg.run()
