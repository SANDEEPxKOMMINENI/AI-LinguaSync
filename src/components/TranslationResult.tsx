import React, { useState, useRef } from 'react';
import { Copy, Check, Volume2, Loader2 } from 'lucide-react';

interface TranslationResultProps {
  originalText: string;
  translatedText: string;
  audioData?: string; // Base64 encoded audio data
}

export const TranslationResult: React.FC<TranslationResultProps> = ({
  originalText,
  translatedText,
  audioData,
}) => {
  const [copied, setCopied] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(translatedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const playAudio = () => {
    if (audioRef.current && audioData) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  return (
    <div className="space-y-4 bg-white rounded-lg shadow-lg p-6">
      {/* Original Text */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Original Text</h3>
        <p className="text-gray-900">{originalText || 'No speech detected'}</p>
      </div>

      {/* Translation */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-sm font-medium text-gray-500">Translation</h3>
          <div className="flex gap-2">
            {audioData && (
              <button
                onClick={playAudio}
                disabled={isPlaying}
                className="p-2 rounded-full hover:bg-gray-100 transition-colors disabled:opacity-50"
                title="Play translation audio"
              >
                {isPlaying ? (
                  <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                ) : (
                  <Volume2 className="w-4 h-4 text-gray-600" />
                )}
              </button>
            )}
            <button
              onClick={copyToClipboard}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              title="Copy translation"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4 text-gray-600" />
              )}
            </button>
          </div>
        </div>
        <p className="text-gray-900">{translatedText || 'No translation available'}</p>
      </div>

      {/* Hidden audio element for playback */}
      {audioData && (
        <audio
          ref={audioRef}
          src={`data:audio/wav;base64,${audioData}`}
          onEnded={() => setIsPlaying(false)}
          onError={(e) => {
            console.error('Audio playback error:', e);
            setIsPlaying(false);
          }}
        />
      )}
    </div>
  );
};