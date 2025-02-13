export interface TranslationRequest {
  text: string;
  sourceLang: string;
  targetLang: string;
  speakerId?: string;
}

export interface TranslationResponse {
  originalText: string;
  translatedText: string;
  speakerId?: string;
  audioData?: string; // Base64 encoded audio data
}

export interface Language {
  code: string;
  name: string;
}