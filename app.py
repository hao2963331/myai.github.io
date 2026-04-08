import streamlit as st
import sqlite3
import chromadb
import google.generativeai as genai
from datetime import datetime
import os

# FREE: Use Google Gemini (1,500 requests/day)
# Get free key at: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-free-key-here")
genai.configure(api_key=GOOGLE_API_KEY)

# Setup
st.set_page_config(page_title="🧠 My Personal AI", layout="wide")
st.title("🧠 My Personal AI")

# Initialize local database
conn = sqlite3.connect('my_memory.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS interactions 
             (date TEXT, topic TEXT, preference TEXT)''')
conn.commit()

# Initialize local vector DB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="my_knowledge")

# Sidebar - Your Profile
st.sidebar.header("👤 Your Profile")
user_name = st.sidebar.text_input("Your name", "Me")
interests = st.sidebar.text_area("Your interests (comma separated)", 
                                  "coding, AI, productivity")

# Add API Key setting in sidebar
st.sidebar.divider()
st.sidebar.header("⚙️ API Configuration")
api_key_input = st.sidebar.text_input("Google API Key", value=GOOGLE_API_KEY, type="password")
if api_key_input and api_key_input != "your-free-key-here":
    GOOGLE_API_KEY = api_key_input
    genai.configure(api_key=GOOGLE_API_KEY)
    st.sidebar.success("✅ API Key configured!")

# Main App
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 My Patterns", "⚙️ Settings"])

with tab1:
    st.subheader(f"Chat with AI - Hello {user_name}! 👋")
    
    # Personalized chat that remembers you
    user_input = st.text_input("Ask me anything or tell me something:")
    
    if user_input:
        try:
            # Store interaction
            c.execute("INSERT INTO interactions VALUES (?, ?, ?)",
                      (datetime.now().isoformat(), user_input[:50], "positive"))
            conn.commit()
            
            # Get context from your history
            results = collection.query(
                query_texts=[user_input],
                n_results=3
            )
            context = results['documents'][0] if results['documents'] else []
            
            # Generate personalized response
            history = c.execute("SELECT topic FROM interactions ORDER BY date DESC LIMIT 10").fetchall()
            history_text = "\n".join([h[0] for h in history])
            
            prompt = f"""You are a personal AI assistant for {user_name}.
Their interests: {interests}
Recent topics they've discussed: {history_text}
Relevant past context: {str(context)[:500]}

User: {user_input}
Assistant:"""
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            st.success(f"**AI Response:**")
            st.write(response.text)
            
            # Store in vector DB for future context
            collection.add(
                documents=[user_input],
                ids=[f"msg_{datetime.now().timestamp()}"],
                metadatas=[{"date": datetime.now().isoformat()}]
            )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Make sure you have a valid Google API Key configured in the Settings.")

with tab2:
    st.subheader("📊 Your Usage Patterns")
    
    history = c.execute("SELECT date, topic FROM interactions ORDER BY date DESC LIMIT 20").fetchall()
    
    if history:
        st.write(f"**Total interactions: {len(history)}**")
        st.divider()
        for date, topic in history:
            col1, col2 = st.columns([2, 8])
            with col1:
                st.caption(date[:10])
            with col2:
                st.write(f"• {topic}")
    else:
        st.info("No interaction history yet. Start chatting to build your patterns!")

with tab3:
    st.subheader("⚙️ Settings & Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Database Information:**")
        st.write(f"📁 Location: `{os.path.abspath('my_memory.db')}`")
        
        interaction_count = c.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        st.write(f"📝 Total interactions: {interaction_count}")
    
    with col2:
        st.write("**Vector Database:**")
        st.write(f"📁 Location: `{os.path.abspath('./chroma_db')}`")
        st.write("🔍 Used for semantic search of past conversations")
    
    st.divider()
    
    st.write("**API Key:**")
    st.info("🔑 Google Gemini API Key - Get free key at https://aistudio.google.com/app/apikey")
    st.write("Free tier: 1,500 requests/day")
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export My Data"):
            data = c.execute("SELECT * FROM interactions").fetchall()
            st.json({"interactions": data})
    
    with col2:
        if st.button("🗑️ Clear History"):
            if st.checkbox("Confirm delete all interactions"):
                c.execute("DELETE FROM interactions")
                conn.commit()
                st.success("✅ History cleared!")
                st.rerun()
    
    with col3:
        st.write("**Version:** 1.0")

# Footer
st.divider()
st.caption("💾 All data stored locally on your computer | Powered by Google Gemini API")
