import streamlit as st
import requests
import json
import uuid
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import openai

load_dotenv()

DXGPT_BASE_URL = os.getenv("DXGPT_BASE_URL", "https://dxgpt-apim.azure-api.net/api")
DXGPT_SUBSCRIPTION_KEY = os.getenv("DXGPT_SUBSCRIPTION_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MEDICAL_DISCLAIMER = """
⚠️ **IMPORTANT MEDICAL DISCLAIMER** ⚠️
This tool is for EDUCATIONAL PURPOSES ONLY and is NOT intended for actual medical diagnosis or treatment.
Always consult with qualified healthcare professionals for medical advice, diagnosis, and treatment.
Do not use this tool for medical emergencies - call emergency services immediately.
"""

RED_FLAGS_WARNING = """
🚨 **SEEK IMMEDIATE MEDICAL ATTENTION IF YOU EXPERIENCE:**
- Chest pain or difficulty breathing
- Severe abdominal pain
- High fever (>101.3°F/38.5°C) with confusion
- Signs of stroke (face drooping, arm weakness, speech difficulties)
- Severe allergic reactions
- Loss of consciousness
- Severe bleeding or trauma
"""

st.set_page_config(
    page_title="Medical Expert System - Differential Diagnosis Assistant",
    page_icon="🏥",
    #layout="wide",
    
)

class MedicalExpertSystem:
    
    
    # def __init__(self):
        
    #     pass
        
    def normalize_symptom_list(self, symptoms_csv) :
        
        if not symptoms_csv:
            return []
        symptoms = [s.strip() for s in symptoms_csv.split(',')]
        return [s for s in symptoms if s]
        
    def build_context_section(self, age_group, sex, duration, 
                            onset, fever, comorbid, meds,
                            allergies, smoking, travel, 
                            pregnancy, noticed):
       
        context_parts = []
        
        if age_group and age_group != "Select age group":
            context_parts.append(f"Age group: {age_group}")
        if sex and sex != "Select sex":
            context_parts.append(f"Sex: {sex}")
        if pregnancy and pregnancy != "Not applicable":
            context_parts.append(f"Pregnancy status: {pregnancy}")
        if duration:
            context_parts.append(f"Symptom duration: {duration}")
        if onset and onset != "Select onset pattern":
            context_parts.append(f"Onset: {onset}")
        if fever and fever != "Unknown":
            context_parts.append(f"Fever: {fever}")
        if comorbid:
            context_parts.append(f"Comorbidities: {comorbid}")
        if meds:
            context_parts.append(f"Current medications: {meds}")
        if allergies:
            context_parts.append(f"Known allergies: {allergies}")
        if smoking and smoking != "Unknown":
            context_parts.append(f"Smoking status: {smoking}")
        if travel:
            context_parts.append(f"Recent travel: {travel}")
        if noticed:
            context_parts.append(f"Additional observations: {noticed}")
            
        return ". ".join(context_parts) if context_parts else ""
        
    def call_dxgpt_diagnose(self, description):
        
        if not DXGPT_SUBSCRIPTION_KEY:
            raise RuntimeError("DxGPT subscription key not configured. Please set DXGPT_SUBSCRIPTION_KEY environment variable.")
            
        url = f"{DXGPT_BASE_URL}/diagnose"
        headers = {
            "Ocp-Apim-Subscription-Key": DXGPT_SUBSCRIPTION_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "description": description,
            "myuuid": str(uuid.uuid4()),
            "timezone": "Asia/Karachi",
            "lang": "en",
            "model": "gpt4o",
            "response_mode": "direct"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"DxGPT API error: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse DxGPT response: {str(e)}")
            
    def extract_diagnosis_items(self, dxgpt_response):
        
        if isinstance(dxgpt_response, list):
            return dxgpt_response
            
        if not isinstance(dxgpt_response, dict):
            return []
        
        data = dxgpt_response.get("data")
        if isinstance(data, dict) and "data" in data:
            return data["data"] if isinstance(data["data"], list) else []
        if isinstance(data, list):
            return data
        
        for key in ("diagnoses", "diagnosis"):
            if key in dxgpt_response:
                result = dxgpt_response[key]
                return result if isinstance(result, list) else [result] if result else []
        
        return []
        
    def calculate_heuristic_probabilities(self, items, original_symptoms):
        
        if not items:
            return []
        
        original_lower = set(s.lower().strip() for s in original_symptoms)
            
        scores = []
        for item in items:
            api_matching = item.get("symptoms_in_common") or item.get("matching_symptoms") or []
            non_matching = item.get("symptoms_not_in_common") or item.get("non_matching_symptoms") or []
            
            if isinstance(api_matching, list):
                api_matching_lower = set(s.lower().strip() for s in api_matching)
                actual_common = len(original_lower & api_matching_lower)
            else:
                actual_common = 0
            
            if isinstance(non_matching, list):
                non_matching_lower = set(s.lower().strip() for s in non_matching)
                actual_mismatches = len(original_lower & non_matching_lower)
            else:
                actual_mismatches = 0
            
            score = max(0, actual_common - actual_mismatches)
            scores.append(score)
            
        total_score = sum(scores)
        if total_score == 0:
            equal_prob = 100.0 / len(items)
            return [equal_prob] * len(items)
            
        probabilities = [(score / total_score) * 100 for score in scores]
        
        if probabilities:
            diff = 100.0 - sum(probabilities)
            probabilities[0] += diff
            
        return probabilities
        
    def call_openai_diagnose(self, description):
        
        if not OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        system_prompt = """You are a medical expert system for educational purposes only. Based on the symptoms provided, return the top 3 most likely differential diagnoses in strict JSON format as below.
                             Rules:

Focus on common and likely conditions; avoid rare ones unless strongly indicated.

For each diagnosis, include:

matching_symptoms: symptoms supporting it

non_matching_symptoms: provided symptoms that do not fit

rationale: brief clinical explanation

Do not provide treatments or advice.

Output only valid JSON.

JSON format:

{
"diagnoses": [
{
"name": "Diagnosis Name",
"matching_symptoms": ["symptom1","symptom2"],
"non_matching_symptoms": ["symptom3"],
"rationale": "Brief clinical reasoning"
},
{
"name": "Diagnosis Name 2",
"matching_symptoms": ["..."],
"non_matching_symptoms": ["..."],
"rationale": "..."
},
{
"name": "Diagnosis Name 3",
"matching_symptoms": ["..."],
"non_matching_symptoms": ["..."],
"rationale": "..."
}
],
"
}  
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": description}
                ],
                max_tokens=1000,
                temperature=0
            )
            
            content = response.choices[0].message.content.strip()
            
            json_content = self.extract_json_from_response(content)
            
            return json.loads(json_content)
            
        except openai.OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from OpenAI. Error: {str(e)}")
        except (AttributeError, KeyError) as e:
            raise RuntimeError(f"Unexpected response structure from OpenAI: {str(e)}")
    
    def extract_json_from_response(self, content):
       
        content = content.strip()
        
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
            
        if content.endswith('```'):
            content = content[:-3]
            
        content = content.strip()
        
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return content[start_idx:end_idx + 1]
        
        return content
    
            
    def format_diagnosis_results(self, items, probabilities, 
                               original_symptoms):
        
        diagnoses = []
        
        for i, (item, prob) in enumerate(zip(items, probabilities)):
            name = item.get("diagnosis") or item.get("name") or item.get("disease") or f"Diagnosis {i+1}"
            
            matching = item.get("symptoms_in_common") or item.get("matching_symptoms") or []
            non_matching = item.get("symptoms_not_in_common") or item.get("non_matching_symptoms") or []
            
            rationale = item.get("rationale", "")
            
            diagnosis = {
                "name": name,
                "probability_percent": round(prob, 1),
                "rationale": rationale,
                "matching_symptoms": matching,
                "not_typical_symptoms": non_matching
            }
            diagnoses.append(diagnosis)
            
        return {
            "diagnoses": diagnoses,
            "red_flags": RED_FLAGS_WARNING,
            "disclaimer": MEDICAL_DISCLAIMER
        }
        
    def render_ui(self):
        
        st.title("🏥 Medical Expert System")
        st.subheader("Differential Diagnosis Assistant")
        
        st.error(MEDICAL_DISCLAIMER)
        
        st.markdown("### 📝 Enter Patient Symptoms")
        st.markdown("*Enter 4-10 symptoms separated by commas for best results*")
        
        symptoms_input = st.text_area(
            "Patient Symptoms",
            placeholder="Example: cough, fever, fatigue, shortness of breath, chest pain",
            height=100,
            help="Enter symptoms separated by commas. Recommend 4-10 symptoms for accurate analysis."
        )
        
        with st.expander("📋 Clinical Context (Optional but Recommended)", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                age_group = st.selectbox(
                    "Age Group",
                    ["Select age group", "Infant (0-1 year)", "Child (1-12 years)", 
                     "Adolescent (13-17 years)", "Adult (18-64 years)", "Older adult (65+ years)"]
                )
                
                sex = st.selectbox(
                    "Sex",
                    ["Select sex", "Female", "Male", "Intersex", "Prefer not to say"]
                )
                
                pregnancy = st.selectbox(
                    "Pregnancy Status",
                    ["Not applicable", "Pregnant", "Not pregnant", "Possibly pregnant"]
                )
                
                duration = st.text_input("Symptom Duration", placeholder="e.g., 3 days, 2 weeks")
                
                onset = st.selectbox(
                    "Onset Pattern",
                    ["Select onset pattern", "Sudden", "Gradual", "Intermittent"]
                )
                
                fever = st.selectbox("Fever Present", ["Unknown", "Yes", "No"])
                
            with col2:
                comorbid = st.text_area(
                    "Comorbidities", 
                    placeholder="e.g., diabetes, hypertension, asthma",
                    height=60
                )
                
                meds = st.text_area(
                    "Current Medications",
                    placeholder="e.g., metformin, lisinopril, albuterol",
                    height=60
                )
                
                allergies = st.text_area(
                    "Known Allergies",
                    placeholder="e.g., penicillin, shellfish, latex",
                    height=60
                )
                
                smoking = st.selectbox(
                    "Smoking Status",
                    ["Unknown", "Never", "Former", "Current"]
                )
                
                travel = st.text_input(
                    "Recent Travel",
                    placeholder="e.g., international travel, endemic areas"
                )
                
        noticed = st.text_area(
            "Additional Notes (Non-clinical)",
            placeholder="Any other observations or context...",
            height=80
        )
        
        st.markdown("### 🔧 AI Model Selection")
        api_choice = st.radio(
            "Choose AI Model",
            ["DxGPT (Primary)", "OpenAI GPT-4 (Alternative)"],
            help="DxGPT is the primary medical AI model. OpenAI GPT-4 is an alternative option."
        )
        
        if st.button("🔍 Generate Differential Diagnosis", type="primary"):
            self.process_diagnosis_request(
                symptoms_input, age_group, sex, duration, onset, fever,
                comorbid, meds, allergies, smoking, travel, pregnancy,
                noticed, api_choice
            )
            
    def process_diagnosis_request(self, symptoms_input, age_group, sex,
                                duration, onset, fever, comorbid,
                                meds, allergies, smoking, travel,
                                pregnancy, noticed, api_choice):
        
        
        if not symptoms_input.strip():
            st.error("Please enter at least one symptom.")
            return
            
        symptoms = self.normalize_symptom_list(symptoms_input)
        
        if len(symptoms) < 2:
            st.warning("For better accuracy, please enter at least 2 symptoms.")
            
        context = self.build_context_section(
            age_group, sex, duration, onset, fever, comorbid,
            meds, allergies, smoking, travel, pregnancy, noticed
        )
        
        description = f"Patient with symptoms: {', '.join(symptoms)}"
        if context:
            description += f". Clinical context: {context}"
            
        with st.spinner("🔄 Analyzing symptoms and generating differential diagnoses..."):
            try:
                if api_choice == "DxGPT (Primary)":
                    response = self.call_dxgpt_diagnose(description)
                    items = self.extract_diagnosis_items(response)
                else:
                    response = self.call_openai_diagnose(description)
                    items = response.get("diagnoses", [])
                
                if not items:
                    api_name = "DxGPT" if api_choice == "DxGPT (Primary)" else "OpenAI"
                    st.error(f"No diagnoses returned from {api_name}. Please try again or use the alternative API.")
                    return
                
                items = items[:3]
                probabilities = self.calculate_heuristic_probabilities(items, symptoms)
                results = self.format_diagnosis_results(items, probabilities, symptoms)
                    
                self.display_results(results)
                
            except RuntimeError as e:
                st.error(f"Error generating diagnosis: {str(e)}")
                st.info("Please check your API configuration and try again.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.info("Please try again or contact support if the issue persists.")
                
    def display_results(self, results):
        st.markdown("---")
        st.markdown("## 📊 Differential Diagnosis Results")
        
        st.markdown("### Summary")
        diagnoses = results["diagnoses"]
        
        if diagnoses:
            summary_data = []
            for i, dx in enumerate(diagnoses, 1):
                summary_data.append({
                    "Rank": i,
                    "Diagnosis": dx["name"],
                    "Probability (%)": f"{dx['probability_percent']:.1f}%",
                    "Matching Symptoms": len(dx["matching_symptoms"]),
                    "Rationale (Preview)": (dx["rationale"])
                })
                
            st.dataframe(summary_data, use_container_width=True)
            
            st.markdown("### 🔍 Detailed Analysis")
            
            for i, dx in enumerate(diagnoses, 1):
                with st.expander(f"#{i} {dx['name']} ({dx['probability_percent']:.1f}%)", expanded=i==1):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🎯 Matching Symptoms:**")
                        if dx["matching_symptoms"]:
                            for symptom in dx["matching_symptoms"]:
                                st.markdown(f"✅ {symptom}")
                        else:
                            st.markdown("*No specific matching symptoms listed*")
                            
                    with col2:
                        st.markdown("**❓ Non-typical Symptoms:**")
                        if dx["not_typical_symptoms"]:
                            for symptom in dx["not_typical_symptoms"]:
                                st.markdown(f"❌ {symptom}")
                        else:
                            st.markdown("*No non-typical symptoms noted*")
                            
                    st.markdown("**🧠 Clinical Reasoning:**")
                    st.markdown(dx["rationale"])
                    
        st.markdown("---")
        st.error(results["red_flags"])
        
        st.markdown("---")
        st.info(results["disclaimer"])
        
def main():
    app = MedicalExpertSystem()
    app.render_ui()

if __name__ == "__main__":
    main()