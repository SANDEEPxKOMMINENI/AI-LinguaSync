import React, { useState, useCallback, useEffect } from 'react';
import useWebSocket from 'react-use-websocket';
import { AudioRecorder } from './components/AudioRecorder';
import { LanguageSelector } from './components/LanguageSelector';
import { TranslationResult } from './components/TranslationResult';
import { TranslationResponse } from './types/translation';
import { Headphones } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const WS_URL = BACKEND_URL.replace(/^http/, 'ws');
const CLIENT_ID = Math.random().toString(36).slice(2);

function App() {
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('es');
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [translation, setTranslation] = useState<TranslationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const { sendMessage, readyState } = useWebSocket(`${WS_URL}/ws/${CLIENT_ID}`, {
    onOpen: () => {
      setIsConnected(true);
      setError(null);
      setRetryCount(0);
    },
    onClose: () => {
      setIsConnected(false);
      setError('Connection to translation service lost. Please ensure the backend server is running.');
      setRetryCount(prev => prev + 1);
    },
    onMessage: useCallback((event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.error) {
          setError(response.error);
        } else {
          setTranslation({
            originalText: response.original_text || '',
            translatedText: response.translated_text || '',
            audioData: response.audio_data || null,
            speakerId: response.speaker_id
          });
          setError(null);
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
        setError('Error processing translation response');
      } finally {
        setIsProcessing(false);
      }
    }, []),
    onError: (error) => {
      console.error('WebSocket error:', error);
      setError('Failed to connect to translation service. Please ensure the backend server is running.');
      setIsProcessing(false);
      setIsConnected(false);
    },
    shouldReconnect: (closeEvent) => retryCount < 5,
    reconnectInterval: (attemptNumber) => Math.min(1000 * Math.pow(2, attemptNumber), 10000),
    reconnectAttempts: 5,
    share: true,
  });

  const handleTranslate = async () => {
    if (!inputText.trim()) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await axios.get(`${BACKEND_URL}/translate`, {
        params: {
          text: inputText,
          source_lang: sourceLang,
          target_lang: targetLang
        }
      });
      
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setTranslation({
          originalText: response.data.original_text,
          translatedText: response.data.translated_text,
          speakerId: 'user'
        });
      }
    } catch (e) {
      console.error('Translation error:', e);
      setError('Failed to translate text. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAudioData = useCallback((audioBlob: Blob) => {
    if (!isConnected) {
      setError('Not connected to translation service. Please ensure the backend server is running and refresh the page.');
      return;
    }
    setIsProcessing(true);
    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result instanceof ArrayBuffer) {
        sendMessage(reader.result);
      }
    };
    reader.readAsArrayBuffer(audioBlob);
  }, [sendMessage, isConnected]);

  useEffect(() => {
    const timer = setInterval(() => {
      setRetryCount(0);
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <Headphones className="w-12 h-12 text-blue-500 mx-auto mb-4" />
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Translator</h1>
          <p className="text-lg text-gray-600">
            Translate text instantly with our free translation service
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-xl p-6 mb-8">
          <div className="grid grid-cols-2 gap-6 mb-8">
            <LanguageSelector
              value={sourceLang}
              onChange={setSourceLang}
              label="Source Language"
            />
            <LanguageSelector
              value={targetLang}
              onChange={setTargetLang}
              label="Target Language"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="inputText" className="block text-sm font-medium text-gray-700 mb-2">
              Enter text to translate
            </label>
            <textarea
              id="inputText"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Type or paste your text here..."
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleTranslate}
                disabled={isProcessing || !inputText.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? 'Translating...' : 'Translate'}
              </button>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <p className="text-sm text-gray-500 mb-4">Or try voice translation (experimental)</p>
            <AudioRecorder
              onAudioData={handleAudioData}
              isProcessing={isProcessing}
              disabled={!isConnected}
            />
          </div>
        </div>

        {translation && (
          <TranslationResult
            originalText={translation.originalText}
            translatedText={translation.translatedText}
            audioData={translation.audioData}
          />
        )}
      </div>
    </div>
  );
}

export default App;