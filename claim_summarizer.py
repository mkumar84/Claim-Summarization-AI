import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import time
import base64
from io import BytesIO
import zipfile

# Set page config
st.set_page_config(
    page_title="Claim Summarization AI",
    page_icon="📄",
    layout="wide"
)

# Generate synthetic claims data (10,000+ claims)
@st.cache_data
def generate_claims_dataset(num_claims=10000):
    claim_types = ["Auto Collision", "Property Damage", "Medical", "Theft", "Natural Disaster"]
    statuses = ["Submitted", "In Review", "Approved", "Denied", "Paid"]
    document_types = ["Police Report", "Medical Records", "Repair Estimate", "Photos", 
                     "Witness Statement", "Insurance Policy", "Claim Form", "Invoices"]
    
    claims = []
    for i in range(num_claims):
        claim_date = datetime.now() - timedelta(days=random.randint(0, 365*2))
        claim_amount = round(random.uniform(500, 50000), 2)
        
        # Generate random documents for this claim (3-8 documents per claim)
        docs = random.sample(document_types, k=random.randint(3, 8))
        
        claims.append({
            "Claim ID": f"CLM-{100000 + i}",
            "Type": random.choice(claim_types),
            "Date Filed": claim_date.strftime("%Y-%m-%d"),
            "Amount": claim_amount,
            "Status": random.choice(statuses),
            "Policy Holder": f"Customer {random.randint(1, 5000)}",
            "Documents": ", ".join(docs),
            "Document Count": len(docs)
        })
    
    return pd.DataFrame(claims)

# Generate synthetic document content
def generate_document_content(doc_type, claim_id):
    if doc_type == "Police Report":
        content = f"""POLICE REPORT - CLAIM {claim_id}
Date: {datetime.now().strftime('%Y-%m-%d')}
Officer: Officer {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}
        
Incident Description:
The claimant reported a {random.choice(['minor', 'moderate', 'major'])} 
{random.choice(['collision', 'hit-and-run', 'parking lot incident'])} 
occurring at approximately {random.randint(1, 12)}:{random.randint(0, 59):02d} 
{random.choice(['AM', 'PM'])} on {random.choice(['Main St', 'Oak Ave', 'Highway 101'])}.
        
Parties Involved:
- Claimant: {random.choice(['cooperative', 'uncooperative', 'injured'])}
- Other Driver: {random.choice(['insured', 'uninsured', 'fled scene'])}
        
Officer Notes:
{random.choice(['No signs of impairment', 'Possible distracted driving', 
'Weather conditions may have contributed'])}. 
{random.choice(['Citation issued', 'No citations issued'])}."""
    
    elif doc_type == "Medical Records":
        content = f"""MEDICAL RECORDS - CLAIM {claim_id}
Patient: {random.choice(['John Doe', 'Jane Smith', 'Robert Johnson'])}
Provider: {random.choice(['City General Hospital', 'Regional Medical Center', 'Urgent Care Clinic'])}
        
Diagnosis:
- {random.choice(['Whiplash', 'Concussion', 'Sprained wrist', 'Lacerations'])}
- Severity: {random.choice(['Mild', 'Moderate', 'Severe'])}
        
Treatment:
- {random.choice(['Pain medication prescribed', 'Physical therapy recommended', 
'Surgery performed', 'Follow-up required'])}
        
Estimated Recovery Time: {random.randint(2, 12)} weeks"""
    
    elif doc_type == "Repair Estimate":
        content = f"""REPAIR ESTIMATE - CLAIM {claim_id}
Shop: {random.choice(['City Auto Body', 'Precision Repairs', 'Collision Experts'])}
Date: {datetime.now().strftime('%Y-%m-%d')}
        
Vehicle: {random.choice(['2018 Toyota Camry', '2020 Honda Accord', '2019 Ford F-150'])}
VIN: {''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ1234567890', k=17))}
        
Damage Assessment:
- {random.choice(['Front bumper damage', 'Passenger side dent', 'Rear collision damage'])}
- {random.choice(['Headlight assembly broken', 'Paint scratches', 'Frame damage'])}
        
Parts: ${random.randint(500, 2500):.2f}
Labor: ${random.randint(1000, 5000):.2f}
Total Estimate: ${random.randint(1500, 7500):.2f}"""
    
    elif doc_type == "Photos":
        content = f"""PHOTO DOCUMENTATION - CLAIM {claim_id}
{random.randint(3, 12)} photos attached showing:
- {random.choice(['Vehicle damage', 'Property damage', 'Injury documentation'])}
- {random.choice(['Close-up of damage', 'Wide shot of scene', 'License plate visible'])}
        
Photo Notes:
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Location: {random.choice(['GPS coordinates recorded', 'Landmark visible', 'Street sign shown'])}"""
    
    elif doc_type == "Witness Statement":
        content = f"""WITNESS STATEMENT - CLAIM {claim_id}
Witness: {random.choice(['Mary Johnson', 'David Wilson', 'Sarah Miller'])}
Contact: {random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}
        
Statement:
"I observed {random.choice(['the collision', 'the incident', 'the aftermath'])} at approximately 
{random.randint(1, 12)}:{random.randint(0, 59):02d} {random.choice(['AM', 'PM'])}. 
The other vehicle appeared to be at fault. 
I stayed until authorities arrived."""
    
    elif doc_type == "Insurance Policy":
        content = f"""POLICY DETAILS - CLAIM {claim_id}
Policy Holder: {random.choice(['John Smith', 'Emily Johnson', 'Michael Williams'])}
Policy Number: {random.randint(1000000, 9999999)}
        
Coverage:
- Liability: ${random.choice([25000, 50000, 100000])}
- Collision: {random.choice(['$500 deductible', '$1000 deductible', 'Not covered'])}
- Comprehensive: {random.choice(['Included', 'Not included'])}
        
Effective Dates: {random.choice(['01/01/2023 - 01/01/2024', '03/15/2023 - 03/15/2024'])}
Status: {random.choice(['Active', 'Pending renewal', 'Cancelled'])}"""
    
    elif doc_type == "Claim Form":
        content = f"""CLAIM FORM - CLAIM {claim_id}
Date of Loss: {(datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')}
Time: {random.randint(1, 12)}:{random.randint(0, 59):02d} {random.choice(['AM', 'PM'])}
Location: {random.choice(['123 Main St', '456 Oak Ave', 'Highway 101 at Exit 42'])}
        
Description of Loss:
{random.choice(['Rear-ended at stop light', 'Hail damage to roof', 
'Theft from parked vehicle', 'Slip and fall at business'])}
        
Injuries: {random.choice(['None reported', 'Whiplash', 'Back pain', 'Broken arm'])}
Police Report: {random.choice(['Yes', 'No', 'Pending'])}"""
    
    elif doc_type == "Invoices":
        content = f"""INVOICES - CLAIM {claim_id}
Provider: {random.choice(['City Hospital', 'Towing Services Inc', 'Auto Body Specialists'])}
Date: {datetime.now().strftime('%Y-%m-%d')}
        
Services:
- {random.choice(['Emergency room visit', 'Vehicle tow', 'Repair labor'])}: ${random.randint(200, 2000):.2f}
- {random.choice(['X-rays', 'Storage fees', 'Parts'])}: ${random.randint(100, 1500):.2f}
- {random.choice(['Medication', 'Rental car', 'Diagnostics'])}: ${random.randint(50, 800):.2f}
        
Total: ${random.randint(350, 4300):.2f}
Paid by: {random.choice(['Patient', 'Insurance', 'Pending'])}"""
    
    else:
        content = "Document content not available"
    
    return content

# AI Summarization Simulation
def generate_summary(doc_type, content):
    time.sleep(1)  # Simulate processing time
    
    summary_templates = {
        "Police Report": [
            "Incident Type: " + random.choice(["Collision", "Hit-and-run", "Property damage"]),
            "Parties Involved: " + random.choice(["2 vehicles", "Vehicle and pedestrian", "Single vehicle"]),
            "Fault Indication: " + random.choice(["Other driver cited", "No determination", "Shared responsibility"]),
            "Key Details: " + random.choice(["Police report supports claim", "Discrepancies noted", "Consistent with claimant statement"])
        ],
        "Medical Records": [
            "Injury Type: " + random.choice(["Whiplash", "Soft tissue", "Fracture"]),
            "Treatment: " + random.choice(["Conservative", "Surgical", "Ongoing"]),
            "Recovery Time: " + random.choice(["2-4 weeks", "6-8 weeks", "3+ months"]),
            "Relation to Claim: " + random.choice(["Directly related", "Potentially related", "Unclear connection"])
        ],
        "Repair Estimate": [
            "Damage Severity: " + random.choice(["Minor", "Moderate", "Severe"]),
            "Repair Cost: " + f"${random.randint(1000, 10000)}",
            "Parts Required: " + random.choice(["OEM", "Aftermarket", "Salvaged"]),
            "Validation: " + random.choice(["Reasonable", "Above market rate", "Needs review"])
        ],
        "Photos": [
            "Damage Visible: " + random.choice(["Yes, clearly", "Partially", "Minimal"]),
            "Consistency: " + random.choice(["Matches claim", "Some discrepancies", "Needs clarification"]),
            "Key Evidence: " + random.choice(["License plate visible", "Date stamps match", "Location identifiable"])
        ],
        "Witness Statement": [
            "Credibility: " + random.choice(["High", "Medium", "Low"]),
            "Corroboration: " + random.choice(["Supports claimant", "Contradicts claimant", "Neutral"]),
            "Key Points: " + random.choice(["Identified at-fault party", "Described sequence", "Noted conditions"])
        ],
        "Insurance Policy": [
            "Coverage Status: " + random.choice(["Active", "Lapsed", "Pending"]),
            "Limits: " + random.choice(["Adequate", "Marginal", "Insufficient"]),
            "Deductible: " + random.choice(["$500", "$1000", "$2000"]),
            "Special Provisions: " + random.choice(["None", "Rental coverage", "Roadside assistance"])
        ],
        "Claim Form": [
            "Completeness: " + random.choice(["Complete", "Missing details", "Partially filled"]),
            "Consistency: " + random.choice(["Consistent", "Minor discrepancies", "Major issues"]),
            "Timeliness: " + random.choice(["Filed promptly", "Delayed", "Within window"])
        ],
        "Invoices": [
            "Reasonableness: " + random.choice(["Market rates", "Above average", "Below average"]),
            "Necessity: " + random.choice(["Clearly related", "Some unrelated", "Needs review"]),
            "Duplication: " + random.choice(["None found", "Possible duplicates", "Exact duplicates"])
        ]
    }
    
    summary = {
        "document_type": doc_type,
        "key_points": summary_templates.get(doc_type, ["No summary available"]),
        "ai_assessment": random.choice(["Valid", "Questionable", "Requires investigation"]),
        "confidence_score": f"{random.randint(70, 95)}%"
    }
    
    return summary

# Download helper functions
def create_download_link(content, filename):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download {filename}</a>'

def create_zip_file(files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, file_content in files.items():
            zip_file.writestr(file_name, file_content)
    zip_buffer.seek(0)
    return zip_buffer

# Main App
def main():
    st.title("📄 Insurance Claim Document Summarization AI")
    st.markdown("""
    This prototype demonstrates AI-powered summarization of insurance claim documents. 
    Select a claim and documents to generate concise summaries.
    """)
    
    # Load or generate claims data
    claims_df = generate_claims_dataset()
    
    # Sidebar filters
    st.sidebar.header("Claim Filters")
    claim_type = st.sidebar.selectbox("Claim Type", ["All"] + list(claims_df["Type"].unique()))
    claim_status = st.sidebar.selectbox("Status", ["All"] + list(claims_df["Status"].unique()))
    
    # Apply filters
    filtered_claims = claims_df.copy()
    if claim_type != "All":
        filtered_claims = filtered_claims[filtered_claims["Type"] == claim_type]
    if claim_status != "All":
        filtered_claims = filtered_claims[filtered_claims["Status"] == claim_status]
    
    # Select claim
    selected_claim_id = st.sidebar.selectbox(
        "Select Claim", 
        filtered_claims["Claim ID"].unique()
    )
    
    selected_claim = filtered_claims[filtered_claims["Claim ID"] == selected_claim_id].iloc[0]
    
    # Display claim info
    st.sidebar.markdown(f"""
    **Selected Claim:**
    - ID: {selected_claim['Claim ID']}
    - Type: {selected_claim['Type']}
    - Status: {selected_claim['Status']}
    - Amount: ${selected_claim['Amount']:,.2f}
    - Documents: {selected_claim['Document Count']}
    """)
    
    # Main tabs
    tab1, tab2 = st.tabs(["Single Document Summary", "Multi-Document Summary"])
    
    with tab1:
        st.header("Single Document Summarization")
        st.markdown("Select one document to analyze and summarize.")
        
        # Get document types for this claim
        doc_types = selected_claim["Documents"].split(", ")
        selected_doc = st.selectbox("Select Document Type", doc_types)
        
        if st.button("Generate Document Content", key="gen_single"):
            with st.spinner(f"Generating {selected_doc} content..."):
                doc_content = generate_document_content(selected_doc, selected_claim_id)
                
                st.subheader(f"Document Content: {selected_doc}")
                st.text_area("Full Document", doc_content, height=300)
                
                # Download button
                st.markdown(create_download_link(doc_content, f"{selected_claim_id}_{selected_doc}.txt"), unsafe_allow_html=True)
                
                # Generate summary
                if st.button("Generate AI Summary", key="sum_single"):
                    with st.spinner("AI is analyzing the document..."):
                        summary = generate_summary(selected_doc, doc_content)
                        
                        st.subheader("AI Summary")
                        st.markdown(f"**Document Type:** {summary['document_type']}")
                        st.markdown("**Key Points:**")
                        for point in summary["key_points"]:
                            st.markdown(f"- {point}")
                        st.markdown(f"**AI Assessment:** {summary['ai_assessment']}")
                        st.markdown(f"**Confidence Score:** {summary['confidence_score']}")
    
    with tab2:
        st.header("Multi-Document Summarization")
        st.markdown("Select multiple documents to analyze and compare summaries.")
        
        # Get document types for this claim
        doc_types = selected_claim["Documents"].split(", ")
        selected_docs = st.multiselect("Select Document Types", doc_types)
        
        if st.button("Generate Documents Content", key="gen_multi"):
            if not selected_docs:
                st.warning("Please select at least one document type")
            else:
                docs_content = {}
                with st.spinner("Generating documents..."):
                    for doc_type in selected_docs:
                        docs_content[doc_type] = generate_document_content(doc_type, selected_claim_id)
                
                # Create zip file for download
                zip_file = create_zip_file({
                    f"{selected_claim_id}_{doc_type}.txt": content 
                    for doc_type, content in docs_content.items()
                })
                
                st.download_button(
                    label="Download All Documents",
                    data=zip_file,
                    file_name=f"{selected_claim_id}_documents.zip",
                    mime="application/zip"
                )
                
                # Display tabs for each document
                tabs = st.tabs(selected_docs)
                for i, doc_type in enumerate(selected_docs):
                    with tabs[i]:
                        st.text_area(f"Full {doc_type}", docs_content[doc_type], height=200)
                
                # Generate summaries
                if st.button("Generate AI Summaries", key="sum_multi"):
                    summaries = {}
                    with st.spinner("AI is analyzing documents..."):
                        for doc_type in selected_docs:
                            summaries[doc_type] = generate_summary(doc_type, docs_content[doc_type])
                    
                    st.subheader("Comparative Summaries")
                    for doc_type, summary in summaries.items():
                        with st.expander(f"{doc_type} Summary"):
                            st.markdown("**Key Points:**")
                            for point in summary["key_points"]:
                                st.markdown(f"- {point}")
                            st.markdown(f"**AI Assessment:** {summary['ai_assessment']}")
                            st.markdown(f"**Confidence Score:** {summary['confidence_score']}")
                    
                    # Create summary report
                    report = f"Claim {selected_claim_id} - Summary Report\n\n"
                    for doc_type, summary in summaries.items():
                        report += f"=== {doc_type} ===\n"
                        report += "Key Points:\n"
                        report += "\n".join(f"- {point}" for point in summary["key_points"]) + "\n"
                        report += f"Assessment: {summary['ai_assessment']}\n"
                        report += f"Confidence: {summary['confidence_score']}\n\n"
                    
                    st.download_button(
                        label="Download Full Summary Report",
                        data=report,
                        file_name=f"{selected_claim_id}_summary_report.txt",
                        mime="text/plain"
                    )

if __name__ == "__main__":
    main()