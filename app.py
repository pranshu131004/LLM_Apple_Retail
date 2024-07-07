import streamlit as st
import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from streamlit_lottie import st_lottie
import subprocess

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if api_key is None:
    st.error("API key for Google Generative AI not found. Please set it in your environment variables.")
else:
    genai.configure(api_key=api_key)

product_store = "products.json"

if os.path.exists(product_store):
    with open(product_store, "r") as file:
        products = json.load(file)
else:
    products = {}

def save_products():
    with open(product_store, "w") as file:
        json.dump(products, file, indent=4)

def read_product_id():
    filename = "product_id.txt"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            product_id = file.read().strip()
        return product_id
    return None

def get_product_info(product_id):
    return products.get(product_id, "Product information not available.")

def add_product(product_id, name, category, description, specifications, features, use_cases):
    products[product_id] = {
        "name": name,
        "category": category,
        "description": description,
        "specifications": specifications,
        "features": features,
        "use_cases": use_cases
    }
    save_products()

def generate_recommendations(product_info, user_query):
    text_chunks = [product_info]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    prompt_template = """
    Based on the following product information, provide detailed recommendations and insights for the given user query. If no specific recommendations can be made, provide relevant information based on the context.
    
    Product Information:
    {context}
    
    User Query: {question}
    
    Recommendations:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    docs = vector_store.similarity_search(user_query)
    response = chain.invoke({"input_documents": docs, "question": user_query})
    return response["output_text"]

def load_lottie_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def main():
    st.set_page_config(page_title="Retail Product Info and Recommendations", layout="wide")
    
    pages = ["Home", "Add Product", "Search Product", "Scan Product"]
    selected_page = st.sidebar.selectbox("Navigate", pages)
    
    if selected_page == "Home":
        st.title("Welcome to Apple Retailer")
        st.write("Your one-stop solution for all retail product information and recommendations.")
        lottie_retailer = "https://lottie.host/b56c87b0-776b-4af8-8a0d-37e569d429fa/7QEq1AnpDO.json"
        lottie_json = load_lottie_url(lottie_retailer)
        if lottie_json:
            st_lottie(lottie_json, height=400, width=400)
        else:
            st.error("Failed to load Lottie animation.")
    
    elif selected_page == "Add Product":
        st.title("Add New Product")
        product_id = st.text_input("Product ID")
        name = st.text_input("Name")
        category = st.text_input("Category")
        description = st.text_area("Description")
        specifications = st.text_area("Specifications")
        features = st.text_area("Features")
        use_cases = st.text_area("Use Cases")
        if st.button("Add Product"):
            add_product(product_id, name, category, description, specifications, features, use_cases)
            st.success("Product added successfully!")
    
    elif selected_page == "Search Product":
        st.title("Search Product")
        iphone_data = {
            "iphone13": {
                "name": "iPhone 13",
                "category": "Smartphone",
                "description": "The iPhone 13 features a sleek design, powerful A15 Bionic chip, and advanced dual-camera system.",
                "specifications": "128GB, 256GB, 512GB, 6.1-inch Super Retina XDR display.",
                "features": "Face ID, 5G capability, Ceramic Shield, Night mode.",
                "use_cases": "Ideal for photography, gaming, and day-to-day usage.",
                "image": "E:/WebD/C programming EL/iPhone13.jpg"
            },
            "iphone14": {
                "name": "iPhone 14",
                "category": "Smartphone",
                "description": "The iPhone 14 offers a refined design with upgraded performance and enhanced camera features.",
                "specifications": "128GB, 256GB, 512GB, 6.1-inch Super Retina XDR display.",
                "features": "ProMotion, Ceramic Shield, A16 Bionic chip.",
                "use_cases": "Great for professional photography, video editing, and high-performance tasks.",
                "image": "E:/WebD/C programming EL/iPhone14.jpg"
            },
            "iphone15": {
                "name": "iPhone 15",
                "category": "Smartphone",
                "description": "The iPhone 15 comes with an advanced camera system, powerful A17 chip, and improved battery life.",
                "specifications": "128GB, 256GB, 512GB, 1TB, 6.7-inch Super Retina XDR display.",
                "features": "ProMotion, Ceramic Shield, 5G, MagSafe, Improved battery.",
                "use_cases": "Perfect for creatives, gamers, and professionals.",
                "image": "E:/WebD/C programming EL/iPhone15.jpg"
            }
        }

        for key, data in iphone_data.items():
            st.subheader(data["name"])
            st.write(f"**Category:** {data['category']}")
            st.write(f"**Description:** {data['description']}")
            st.write(f"**Specifications:** {data['specifications']}")
            st.write(f"**Features:** {data['features']}")
            st.write(f"**Use Cases:** {data['use_cases']}")
            st.image(data["image"], caption=data["name"], use_column_width=True)
            st.write("---")

        user_query = st.text_input("Enter your query about the product (e.g., What is the best iPhone for photography?)", placeholder="e.g., What are the best applications for this product?")
        product_option = st.selectbox("Select a Product to Query", ["iPhone 13", "iPhone 14", "iPhone 15"])

        if user_query:
            with st.spinner("Generating recommendations..."):
                selected_product_key = product_option.lower().replace(" ", "")
                product_info = iphone_data[selected_product_key]["description"]
                recommendations = generate_recommendations(product_info, user_query)
                st.write(f"**Recommendations for {product_option}:**\n{recommendations}")

    elif selected_page == "Scan Product":
        st.title("Scan Product")
        if st.button("Simulate Scan"):
            # Run the C program to simulate scanning
            result = subprocess.run(["scanner.exe"], capture_output=True, text=True)
            st.text(result.stdout)
            st.text(result.stderr)
            
            # Read the product ID written by the C program
            product_id = read_product_id()
            if product_id:
                st.success(f"Scanned Product ID: {product_id}")
                product_info = get_product_info(product_id)
                st.write(f"**Product Information:** {product_info}")
            else:
                st.error("No product ID found.")
    
if __name__ == "__main__":
    main()
