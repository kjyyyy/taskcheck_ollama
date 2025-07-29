# 🌐 Multilingual Features - Construction Assistant

The Construction TaskCheck Assistant now supports multiple languages for enhanced accessibility across Southeast Asia and the UK markets.

## 🎯 Supported Languages & Regions

### 1. **English (en)**
- **Native Name**: English
- **Code**: `en`
- **Region**: UK
- **Usage**: Primary language for UK construction terminology

### 2. **Simplified Chinese (zh-cn)**
- **Native Name**: 简体中文
- **Code**: `zh-cn`
- **Region**: Singapore
- **Usage**: For construction projects in Singapore

### 3. **Traditional Chinese (zh-tw)**
- **Native Name**: 繁體中文
- **Code**: `zh-tw`
- **Region**: Hong Kong
- **Usage**: For construction projects in Hong Kong

### 4. **Tagalog (tl)**
- **Native Name**: Tagalog
- **Code**: `tl`
- **Region**: Philippines
- **Usage**: For construction projects in the Philippines

### 5. **Malay (ms)**
- **Native Name**: Bahasa Malaysia
- **Code**: `ms`
- **Region**: Malaysia
- **Usage**: For construction projects in Malaysia

## 🔧 Implementation Details

### Regional Focus
- **Hong Kong**: HK construction standards, Building Ordinance, HK construction materials and suppliers
- **Singapore**: Singapore Building and Construction Authority (BCA) standards, local materials and regulations
- **Malaysia**: Malaysian construction standards, CIDB requirements, local building codes
- **Philippines**: Philippine construction standards, DPWH regulations, local building codes
- **UK**: UK construction standards, Building Regulations, CDM, UK materials and suppliers

### Language Detection
- **Automatic Detection**: Uses `langdetect` library to automatically detect input language
- **Fallback**: Defaults to English if detection fails
- **Heuristic Detection**: For generic Chinese, uses character analysis to distinguish Simplified vs Traditional
- **Regional Mapping**: Maps languages to specific regions for context-appropriate advice

### Model Configuration
- **Updated Modelfile**: Enhanced system prompt with regional focus and multilingual instructions
- **Language Examples**: Provided examples in all supported languages with regional context
- **Cultural Context**: Maintains regional construction standards while supporting multiple languages

## 📡 API Endpoints

### 1. **Language Detection** (`/ask`)
```bash
POST /ask
{
    "question": "香港住宅擴建需要什麼材料？",
    "use_context": true,
    "language": "zh-tw"  # Optional - auto-detected if not provided
}
```

**Response:**
```json
{
    "answer": "香港住宅擴建需要以下材料...",
    "sources": ["source1", "source2"],
    "used_context": true,
    "model": "mistral",
    "detected_language": "zh-tw"
}
```

### 2. **Supported Languages** (`/languages`)
```bash
GET /languages
```

**Response:**
```json
{
    "supported_languages": [
        {
            "code": "en",
            "name": "English",
            "native_name": "English",
            "region": "UK"
        },
        {
            "code": "zh-cn",
            "name": "Simplified Chinese",
            "native_name": "简体中文",
            "region": "Singapore"
        },
        {
            "code": "zh-tw",
            "name": "Traditional Chinese",
            "native_name": "繁體中文",
            "region": "Hong Kong"
        },
        {
            "code": "tl",
            "name": "Tagalog",
            "native_name": "Tagalog",
            "region": "Philippines"
        },
        {
            "code": "ms",
            "name": "Malay",
            "native_name": "Bahasa Malaysia",
            "region": "Malaysia"
        }
    ],
    "default_language": "en",
    "auto_detection": true,
    "regional_focus": [
        "Hong Kong",
        "Singapore",
        "Malaysia",
        "Philippines",
        "UK"
    ]
}
```

## 🧪 Testing

### Running Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python webapp/app.py

# Run multilingual tests
python test_multilingual.py
```

### Test Cases
1. **Language Detection**: Tests automatic detection of input language
2. **Manual Specification**: Tests manual language override
3. **Supported Languages**: Tests the languages endpoint
4. **Regional Context**: Tests region-specific responses

## 🔄 Usage Examples

### English Input (UK)
```
Question: "What materials do I need for a residential extension in the UK?"
Response: "For a UK residential extension, you'll need..."
```

### Traditional Chinese Input (Hong Kong)
```
Question: "香港住宅擴建需要什麼材料？"
Response: "香港住宅擴建需要以下材料..."
```

### Simplified Chinese Input (Singapore)
```
Question: "新加坡住宅扩建需要什么材料？"
Response: "新加坡住宅扩建需要以下材料..."
```

### Tagalog Input (Philippines)
```
Question: "Anong mga materyales ang kailangan para sa residential extension sa Pilipinas?"
Response: "Para sa residential extension sa Pilipinas, kailangan mo ng..."
```

### Malay Input (Malaysia)
```
Question: "Apakah bahan-bahan yang diperlukan untuk pembesaran rumah di Malaysia?"
Response: "Untuk pembesaran rumah di Malaysia, anda memerlukan..."
```

## 🛠️ Installation

### Dependencies
Add to `requirements.txt`:
```
langdetect==1.0.9
```

### Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Rebuild the model** (if using Ollama):
   ```bash
   ollama create construction-multilingual -f Modelfile
   ```

3. **Start the server**:
   ```bash
   python webapp/app.py
   ```

## 🎨 Frontend Integration

### TypeScript/JavaScript Example
```typescript
// Detect language and send request
async function askQuestion(question: string, language?: string) {
    const payload = {
        question: question,
        use_context: true
    };
    
    if (language) {
        payload.language = language;
    }
    
    const response = await fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    return response.json();
}

// Get supported languages with regional information
async function getSupportedLanguages() {
    const response = await fetch('/languages');
    return response.json();
}
```

## 🔍 Language Detection Logic

### Detection Process
1. **Primary Detection**: Uses `langdetect` library
2. **Chinese Subtype**: Analyzes characters to distinguish Simplified vs Traditional
3. **Regional Mapping**: Maps languages to specific regions
4. **Fallback**: Defaults to English for unknown languages

### Character Analysis
- **Simplified Indicators**: 简, 体, 汉, 语
- **Traditional Indicators**: 簡, 體, 漢, 語
- **Decision Logic**: If traditional characters present and no simplified, use Traditional Chinese

### Regional Standards
- **Hong Kong**: Building Ordinance, HK construction standards
- **Singapore**: BCA standards, local regulations
- **Malaysia**: CIDB requirements, Malaysian building codes
- **Philippines**: DPWH regulations, Philippine standards
- **UK**: Building Regulations, CDM, UK standards

## 🚀 Future Enhancements

### Planned Features
1. **More Regional Languages**: Thai, Vietnamese, Indonesian support
2. **Regional Variants**: Different construction standards by specific regions
3. **Cultural Context**: Region-specific construction advice and practices
4. **Translation Memory**: Cache common translations for performance
5. **Local Currency**: Cost estimates in local currencies

### Performance Optimizations
1. **Caching**: Cache language detection results
2. **Batch Processing**: Handle multiple language requests efficiently
3. **Model Optimization**: Fine-tune models for specific regions

## 📊 Monitoring

### Logging
- Language detection results are logged
- Response language is tracked
- Regional context is recorded
- Performance metrics for each language

### Metrics
- Detection accuracy by region
- Response time by language
- Usage statistics per region
- Regional construction query patterns

## 🔧 Troubleshooting

### Common Issues
1. **Language Detection Fails**: Check `langdetect` installation
2. **Model Not Responding**: Verify Ollama model is built with new Modelfile
3. **Character Encoding**: Ensure UTF-8 encoding for all supported languages
4. **Regional Context Missing**: Verify regional standards are included in training

### Debug Commands
```bash
# Check language detection
python -c "from langdetect import detect; print(detect('香港住宅擴建'))"

# Test model response
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "香港住宅擴建需要什麼材料？"}'

# Check supported languages
curl -X GET http://localhost:5000/languages
```

## 📝 Notes

- **Regional Focus**: Assistant provides region-specific construction advice
- **Professional Advice**: Always includes disclaimers about consulting professionals
- **Cultural Sensitivity**: Provides appropriate advice for each regional market
- **Performance**: Language detection adds minimal overhead to response time
- **Standards Compliance**: Maintains regional construction standards and regulations 