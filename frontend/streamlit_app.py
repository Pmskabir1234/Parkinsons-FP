import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Parkinson's Predictor", layout="wide")
st.title("🧠 Parkinson's Disease Prediction (API-Based)")


st.sidebar.header("Enter Voice Features")

def get_user_input():
    return {
        "Fo": st.sidebar.number_input("Fo", value=145.0),
        "Flo": st.sidebar.number_input("Flo", value=72.0),
        "RAP": st.sidebar.number_input("RAP", value=0.00047),
        "spread1": st.sidebar.number_input("spread1", value=-4.12),
        "spread2": st.sidebar.number_input("spread2", value=0.05),
        "D2": st.sidebar.number_input("D2", value=2.98),
        "PPE": st.sidebar.number_input("PPE", value=0.214),
    }

raw_input_data = get_user_input()


def transform_input(data):
    mapping = {
        "Fo": "MDVP:Fo(Hz)",
        "Flo": "MDVP:Flo(Hz)",
        "RAP": "MDVP:RAP",
        "spread1": "spread1",
        "spread2": "spread2",
        "D2": "D2",
        "PPE": "PPE"
    }

    transformed = {}

    for frontend_key, backend_key in mapping.items():
        try:
            transformed[backend_key] = float(data.get(frontend_key, 0))
        except:
            transformed[backend_key] = 0.0

    return transformed


col1, col2 = st.columns(2)

with col1:
    st.subheader("Raw Input (Frontend)")
    st.json(raw_input_data)


if st.button("Predict"):

    
    clean_data = transform_input(raw_input_data)

    with col2:
        st.subheader("Transformed Input (Model Format)")
        st.json(clean_data)

    
    payload = {
        "data": clean_data
    }

    st.subheader("Final Payload Sent to API")
    st.json(payload)

    
    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()

            if "error" in result:
                st.error(result["error"])
            else:

                st.subheader("Prediction Result")
                if result['Label'] == "Parkinson's Detected":
                    st.error("Parkinson's Detected")
                else:
                    st.success("Healthy")
                st.write(result['prediction'])
                

                
                st.subheader("📊 Feature Impact")

                df = pd.DataFrame({
                    "Feature": list(clean_data.keys()),
                    "Value": list(clean_data.values())
                })

                

                st.line_chart(df.set_index("Feature"))

                
                
               
                # st.subheader("Step-by-Step Processing")

                # c1, c2 = st.columns(2)

                # with c1:
                #     st.markdown("### 1. Raw Input (Backend)")
                #     st.write(result["raw_input"])

                # with c2:
                #     st.markdown("### 2. Scaled Input")
                #     st.write(result["scaled_input"])

                
                # st.subheader("📈 Feature Visualization")

                # df = pd.DataFrame([clean_data])
                # st.bar_chart(df.T)
                st.markdown("""
                            ---
                            <div style='text-align: center; font-size: 14px; color: grey;'>
                            Built by Kabir • ML Model API Inference & Backend Learning Project. Keep Learning and chilling!
                            </div>
                            """, unsafe_allow_html=True)


        else:
            st.error(f"API Error: {response.status_code}")
            st.json(response.json())

    except Exception as e:
        st.error(f"Connection Error: {e}")