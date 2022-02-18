import streamlit as st

def local_css():
    with open("style.css") as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def header_title(text, st=st):
    local_css()
    html_str = "<p class='font_header'>"+text+"</p>"
    st.markdown(html_str, unsafe_allow_html=True)

def sub_header_title(text, st):
    local_css()
    html_str = "<p class='font_sub_header'>"+text+"</p>"
    st.markdown(html_str, unsafe_allow_html=True)

def text(text, st):
    local_css()
    html_str = "<p class='font_text'>"+text+"</p>"
    st.markdown(html_str, unsafe_allow_html=True)

def text_left(text, st):
    local_css()
    html_str = "<p class='font_text_left'>"+text+"</p>"
    st.markdown(html_str, unsafe_allow_html=True)

def horizontal(st=st):
    local_css()
    html_str = "<div class='horizontal'></div>"
    st.markdown(html_str, unsafe_allow_html=True)

