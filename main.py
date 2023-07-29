
import json
import os
from zipfile import ZipFile

import streamlit as st
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

from util.modelhelpers import get_llm_model, get_embedding_model


# load environment variables from .env
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['HUGGINGFACEHUB_API_TOKEN'] = os.getenv('HUGGINGFACEHUB_API_TOKEN')


# page
uploaded_model_file = st.file_uploader('Choose a model file (.zip)')
if uploaded_model_file is not None:
    # initialize context
    with ZipFile(uploaded_model_file, 'r') as zip_ref:
        if not os.path.isdir('model'):
            os.makedirs('model')
        zip_ref.extractall('model')
    config = json.load(open(os.path.join('model', 'config.json'), 'r'))
    llm = get_llm_model(config)
    embedding = get_embedding_model(config)
    db = FAISS.load_local('model', embedding)
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

# input
input_question_text = st.text_area('Question')

# get results
if st.button('Ask!'):
    if uploaded_model_file is None:
        st.write('Please upload a model!')
    else:
        response = qa({'query': input_question_text})
        st.write(response['result'])
