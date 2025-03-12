import streamlit as st
import sqlite3
import google.generativeai as genai

# Configure Gemini API (Replace with your actual API key)
GENAI_API_KEY = "AIzaSyByLOZAmBso2PXKwA-rt9t0bs3YOBJyxY4"
genai.configure(api_key=GENAI_API_KEY)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("snippets.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        code TEXT NOT NULL,
        language TEXT NOT NULL,
        use_case TEXT,
        tags TEXT
    )
    """)
    conn.commit()
    conn.close()

# Function to add a code snippet
def add_snippet(title, code, language, use_case, tags):
    conn = sqlite3.connect("snippets.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO snippets (title, code, language, use_case, tags) VALUES (?, ?, ?, ?, ?)",
                   (title, code, language, use_case, tags))
    conn.commit()
    conn.close()

# Function to search code snippets
def search_snippets(keyword):
    conn = sqlite3.connect("snippets.db")
    cursor = conn.cursor()
    query = "SELECT * FROM snippets WHERE title LIKE ? OR language LIKE ? OR use_case LIKE ? OR tags LIKE ?"
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return results

# Function to get Gemini API recommendations
def get_gemini_recommendation(prompt):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting recommendation: {str(e)}"

# Initialize the database
init_db()

# Streamlit UI
st.title("📚 Code Snippet Library")
st.write("A searchable collection of verified code snippets.")

# Section: Add a New Code Snippet
st.subheader("➕ Add a New Code Snippet")
with st.form("add_snippet_form"):
    title = st.text_input("Title", placeholder="Enter a meaningful title...")
    code = st.text_area("Code Snippet", placeholder="Paste your code here...")
    language = st.text_input("Programming Language", placeholder="e.g., Python, SQL, JavaScript")
    use_case = st.text_input("Use Case", placeholder="Describe where this snippet is useful...")
    tags = st.text_input("Tags (comma-separated)", placeholder="e.g., database, optimization, API")

    submit = st.form_submit_button("Save Snippet")
    if submit:
        if title and code and language:
            add_snippet(title, code, language, use_case, tags)
            st.success("✅ Snippet added successfully!")
        else:
            st.error("⚠️ Title, Code, and Language are required!")

# Section: Search Code Snippets
st.subheader("🔍 Search Code Snippets")
search_query = st.text_input("Search for a snippet...", placeholder="Enter keyword (title, language, tags)")
if search_query:
    results = search_snippets(search_query)
    if results:
        for row in results:
            st.markdown(f"### 🏷 {row[1]}")
            st.code(row[2], language=row[3])
            st.write(f"**Language:** {row[3]}  |  **Use Case:** {row[4]}  |  **Tags:** {row[5]}")
            st.markdown("---")
    else:
        st.warning("🚫 No snippets found.")

# Section: Get AI-Powered Code Recommendations
st.subheader("🤖 Ask AURORA")
gemini_prompt = st.text_area("Describe what you need help with...", placeholder="e.g., How to write a SQL query for joins?")
if st.button("Get Recommendation"):
    recommendation = get_gemini_recommendation(gemini_prompt)
    st.write(recommendation)

# Run Streamlit
if __name__ == "__main__":
    st.write("🚀 Ready to use the code snippet library!")
