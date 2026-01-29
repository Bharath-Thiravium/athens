# Voice Translator Setup Guide

## Overview
The Voice Translator feature allows users to speak in one language and get real-time translation to another language with text-to-speech output.

## Features
- Real-time speech recognition
- Multi-language translation (20+ languages)
- Text-to-speech output
- Support for English, Tamil, Hindi, Spanish, French, German, Chinese, Japanese, Korean, Arabic, and more
- Clean, responsive UI with Ant Design components

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Get Google Translate API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the "Cloud Translation API"
4. Create credentials (API Key)
5. Copy the API key

#### Configure Environment Variables
Add to your `.env` file:
```env
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key_here
```

#### Run Migrations (if needed)
```bash
python manage.py makemigrations voice_translator
python manage.py migrate
```

### 2. Frontend Setup

#### Install Dependencies
```bash
cd frontedn
npm install
# or
pnpm install
```

### 3. Usage

#### Access the Voice Translator
1. Login to your dashboard
2. Navigate to `/dashboard/voice-translator`
3. Select source and target languages
4. Click "Start Listening" and speak
5. View translation and click the speaker icon to hear it

#### Supported Languages
- English (en)
- Tamil (ta)
- Hindi (hi)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Russian (ru)
- Portuguese (pt)
- Italian (it)
- Dutch (nl)
- Polish (pl)
- Turkish (tr)
- Thai (th)
- Vietnamese (vi)
- Indonesian (id)
- Malay (ms)

## API Endpoints

### POST /api/translate/
Translates text from one language to another.

**Request:**
```json
{
  "text": "Hello, how are you?",
  "from": "en",
  "to": "ta"
}
```

**Response:**
```json
{
  "translatedText": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
  "originalText": "Hello, how are you?",
  "fromLanguage": "en",
  "toLanguage": "ta"
}
```

### GET /api/languages/
Returns list of supported languages.

**Response:**
```json
{
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "ta", "name": "Tamil"},
    ...
  ]
}
```

## Browser Compatibility

### Speech Recognition Support
- Chrome/Chromium: Full support
- Firefox: Limited support
- Safari: Limited support
- Edge: Full support

### Speech Synthesis Support
- Chrome/Chromium: Full support
- Firefox: Full support
- Safari: Full support
- Edge: Full support

## Troubleshooting

### Common Issues

1. **Speech recognition not working**
   - Ensure you're using HTTPS (required for microphone access)
   - Check browser permissions for microphone
   - Use Chrome/Edge for best compatibility

2. **Translation API errors**
   - Verify Google Translate API key is correct
   - Check API key has proper permissions
   - Ensure billing is enabled on Google Cloud project

3. **Audio playback issues**
   - Check browser audio permissions
   - Ensure speakers/headphones are working
   - Try different browsers

### Error Messages

- "Speech recognition not supported": Use Chrome/Edge browser
- "Translation failed": Check API key and internet connection
- "Microphone access denied": Allow microphone permissions in browser

## Security Notes

- API key should be kept secure and not exposed in frontend code
- Use environment variables for sensitive configuration
- Consider rate limiting for production use
- Implement proper authentication for API endpoints

## Cost Considerations

Google Translate API pricing:
- First 500,000 characters per month: Free
- Additional characters: $20 per 1M characters
- Monitor usage in Google Cloud Console

## Future Enhancements

- Offline translation support
- Custom vocabulary/domain-specific translations
- Voice cloning for consistent speaker identity
- Real-time conversation mode
- Integration with other translation services
