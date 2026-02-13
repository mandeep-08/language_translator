# Language Translator Desktop App

A modern, feature-rich desktop language translator built with Python and Tkinter.

![Language Translator](screenshot.png)

## Features

- 🌍 **60+ Languages** - Translate between over 60 languages with auto-detection
- 🎤 **Speech-to-Text** - Record your voice and translate it instantly
- 🔊 **Text-to-Speech** - Listen to translations with play/pause controls
- 📋 **Copy to Clipboard** - One-click copy of translated text
- 📜 **Translation History** - View and manage your past translations
- ⇄ **Language Swap** - Quickly swap source and target languages
- 🎨 **Modern UI** - Clean, minimal design with responsive layout
- ⌨️ **Keyboard Shortcuts** - Fast workflow with hotkeys

## Screenshots

![alt text](image-1.png)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR-USERNAME/language-translator.git
cd language-translator
```

2. Install required packages:
```bash
pip install deep-translator gtts pygame pyperclip SpeechRecognition pyaudio
```

3. Run the application:
```bash
python language_translator.py
```

## Keyboard Shortcuts

- `Ctrl + Enter` - Translate
- `Ctrl + L` - Clear
- `Ctrl + C` - Copy translation
- `Ctrl + H` - View history
- `Ctrl + M` - Start microphone
- `Ctrl + S` - Swap languages

## Technologies Used

- **Python** - Core programming language
- **Tkinter** - GUI framework
- **deep-translator** - Translation API
- **gTTS** - Text-to-speech conversion
- **SpeechRecognition** - Speech-to-text conversion
- **pygame** - Audio playback

## Features in Detail

### Translation
- Auto-detect source language
- Support for 60+ languages
- Real-time character count
- Error handling and validation

### Audio Controls
- Generate speech from translation
- Play/pause audio controls
- Background processing for long text
- Support for 40+ languages in TTS

### User Interface
- Floating language selector with search
- Hover effects and visual feedback
- Responsive design
- Clean, modern aesthetics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

Mandeep Singh Bhullar
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)
- GitHub: [@your-username](https://github.com/your-username)

## Acknowledgments

- Translation powered by Google Translate API via deep-translator
- Text-to-speech powered by Google TTS