# Medical Expert System - Differential Diagnosis Assistant

A Streamlit web application that provides AI-powered differential diagnosis suggestions based on patient symptoms for **educational purposes only**.

## ⚠️ Important Medical Disclaimer

**This tool is for EDUCATIONAL PURPOSES ONLY** and is NOT intended for actual medical diagnosis or treatment. Always consult with qualified healthcare professionals for medical advice, diagnosis, and treatment. Do not use this tool for medical emergencies - call emergency services immediately.

## Features

- **Symptom Input**: Easy-to-use interface for entering patient symptoms
- **Clinical Context**: Optional detailed clinical information collection
- **AI-Powered Analysis**: Integration with DxGPT and OpenAI APIs
- **Top 3 Differential Diagnoses**: Ranked suggestions with probability estimates
- **Educational Focus**: Detailed explanations and clinical reasoning
- **Safety Features**: Built-in red flag warnings and medical disclaimers

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- API access to either DxGPT or OpenAI GPT-4

### 2. Installation

```bash
# Clone or download the project
cd Yong-Medical-Expert-System-Agent

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root with your API keys:

```env
# DxGPT API Configuration (Primary)
DXGPT_SUBSCRIPTION_KEY=your_dxgpt_subscription_key_here
DXGPT_BASE_URL=https://dxgpt-apim.azure-api.net/api

# OpenAI API Configuration (Alternative)
OPENAI_API_KEY=sk-proj-your_openai_api_key_here
```

**Note**: You need at least one API key configured. Use `.env.example` as a template.

### 4. Run the Application

```bash
streamlit run DxGPT_Medical_Expert_System.py
```

The application will open in your web browser at `http://localhost:8501`

## How to Use

1. **Enter Symptoms**: Type 4-10 symptoms separated by commas in the main text area
2. **Add Clinical Context** (Optional): Expand the clinical context section and fill in relevant information like age, sex, symptom duration, etc.
3. **Choose AI Model**: Select either DxGPT (primary) or OpenAI GPT-4 (alternative)
4. **Generate Diagnosis**: Click the "Generate Differential Diagnosis" button
5. **Review Results**: Examine the top 3 differential diagnoses with probabilities, matching symptoms, and clinical reasoning

## Example Usage

**Symptoms**: `cough, fever, fatigue, shortness of breath, chest pain`

**Clinical Context**: 
- Age: Adult (18-64 years)
- Duration: 5 days
- Onset: Gradual
- Fever: Yes

The system will return the top 3 most likely diagnoses with explanations.

## API Requirements

### DxGPT API (Primary)
- Subscription key required
- Base URL: `https://dxgpt-apim.azure-api.net/api`
- Medical-specific AI model optimized for diagnosis

### OpenAI API (Alternative)
- API key required from OpenAI platform
- Uses GPT-4 model with medical prompting
- Fallback option if DxGPT is unavailable

## Safety Features

- **Medical Disclaimers**: Prominent warnings throughout the interface
- **Red Flag Warnings**: Automatic alerts for emergency situations
- **Educational Focus**: Clear messaging about educational use only
- **No Medical Advice**: Explicit statements that this is not medical advice

## File Structure

```
Yong-Medical-Expert-System-Agent/
├── DxGPT_Medical_Expert_System.py    # Main Streamlit application
├── requirements.txt                   # Python dependencies
├── .env.example                      # Environment variables template
├── README.md                         # This file
└── __pycache__/                      # Python cache (auto-generated)
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your `.env` file is in the correct location
   - Verify API keys are valid and active
   - Check that at least one API key is configured

2. **No Diagnoses Returned**
   - Try using the alternative API
   - Check your internet connection
   - Verify API keys are correctly formatted

3. **Module Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using Python 3.8 or higher

### Error Messages

- **"DxGPT subscription key not configured"**: Add `DXGPT_SUBSCRIPTION_KEY` to your `.env` file
- **"OpenAI API key not configured"**: Add `OPENAI_API_KEY` to your `.env` file
- **"Please enter at least one symptom"**: The symptom input field cannot be empty

## Development

### Key Components

- **MedicalExpertSystem Class**: Main application logic
- **API Integration**: DxGPT and OpenAI API clients
- **Symptom Processing**: Input validation and normalization
- **Probability Calculation**: Heuristic scoring based on symptom matching
- **Results Display**: Formatted output with clinical reasoning

### Adding Features

The code is designed to be easily extensible. Key areas for enhancement:

- Additional AI model integrations
- More sophisticated probability calculations
- Enhanced clinical context fields
- Multi-language support

## License and Usage

This project is for educational and research purposes. Users are responsible for:

- Obtaining proper API access and keys
- Complying with API terms of service
- Using the tool responsibly for educational purposes only
- Not using for actual medical diagnosis or treatment

## Support

For technical issues:
1. Check the troubleshooting section above
2. Verify your environment configuration
3. Review API documentation for DxGPT or OpenAI

## Contributing

When contributing:
- Maintain the educational focus and safety disclaimers
- Follow the existing code structure and patterns
- Test thoroughly with both API options
- Update documentation as needed

---

**Remember**: This tool is for educational purposes only and should never replace professional medical consultation.
