import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2, Settings } from 'lucide-react';

interface AudioRecorderProps {
  onAudioData: (data: Blob) => void;
  isProcessing: boolean;
  disabled?: boolean;
}

interface AudioDevice {
  deviceId: string;
  label: string;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ 
  onAudioData, 
  isProcessing,
  disabled = false 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [devices, setDevices] = useState<AudioDevice[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [showDevices, setShowDevices] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    const loadDevices = async () => {
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioDevices = devices
          .filter(device => device.kind === 'audioinput')
          .map(device => ({
            deviceId: device.deviceId,
            label: device.label || `Microphone ${device.deviceId.slice(0, 5)}...`
          }));
        setDevices(audioDevices);
        
        if (!selectedDevice && audioDevices.length > 0) {
          setSelectedDevice(audioDevices[0].deviceId);
        }
      } catch (error) {
        console.error('Error accessing media devices:', error);
      }
    };

    loadDevices();

    navigator.mediaDevices.addEventListener('devicechange', loadDevices);
    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', loadDevices);
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: selectedDevice ? { exact: selectedDevice } : undefined,
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      // Convert audio to WAV format directly
      const audioContext = new AudioContext({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      const chunks: Float32Array[] = [];
      
      processor.onaudioprocess = (e) => {
        if (isRecording) {
          const inputData = e.inputBuffer.getChannelData(0);
          chunks.push(new Float32Array(inputData));
        }
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      setIsRecording(true);
      setShowDevices(false);
      
      // Store cleanup function
      mediaRecorderRef.current = {
        stop: () => {
          source.disconnect();
          processor.disconnect();
          stream.getTracks().forEach(track => track.stop());
          audioContext.close();
          
          // Convert chunks to WAV
          const audioData = Float32Array.from(chunks.reduce((acc, chunk) => {
            const temp = new Float32Array(acc.length + chunk.length);
            temp.set(acc, 0);
            temp.set(chunk, acc.length);
            return temp;
          }, new Float32Array()));
          
          // Create WAV file
          const wavBuffer = createWavBuffer(audioData, 16000);
          const audioBlob = new Blob([wavBuffer], { type: 'audio/wav' });
          onAudioData(audioBlob);
        },
        stream
      } as any;
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Function to create WAV buffer
  const createWavBuffer = (samples: Float32Array, sampleRate: number): ArrayBuffer => {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    // Write WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, samples.length * 2, true);

    // Write audio data
    floatTo16BitPCM(view, 44, samples);

    return buffer;
  };

  const writeString = (view: DataView, offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const floatTo16BitPCM = (view: DataView, offset: number, input: Float32Array) => {
    for (let i = 0; i < input.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, input[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative flex items-center gap-4">
        <button
          onClick={() => setShowDevices(!showDevices)}
          className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
          title="Select microphone"
        >
          <Settings className="w-5 h-5 text-gray-600" />
        </button>
        
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing || disabled || !selectedDevice}
          className={`p-4 rounded-full transition-colors ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600' 
              : 'bg-blue-500 hover:bg-blue-600'
          } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
          title={disabled ? 'Waiting for connection...' : 'Click to record'}
        >
          {isProcessing ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : isRecording ? (
            <MicOff className="w-6 h-6" />
          ) : (
            <Mic className="w-6 h-6" />
          )}
        </button>

        {showDevices && devices.length > 0 && (
          <div className="absolute left-0 top-full mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
            <div className="p-2">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Select Microphone</h3>
              <div className="space-y-1">
                {devices.map((device) => (
                  <button
                    key={device.deviceId}
                    onClick={() => {
                      setSelectedDevice(device.deviceId);
                      setShowDevices(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                      selectedDevice === device.deviceId
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    {device.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <span className="text-sm text-gray-600">
        {disabled ? 'Connecting to service...' : 
         isProcessing ? 'Processing...' : 
         isRecording ? 'Recording...' : 
         !selectedDevice ? 'No microphone detected' :
         'Click to start recording'}
      </span>
      
      {selectedDevice && (
        <span className="text-xs text-gray-500">
          Using: {devices.find(d => d.deviceId === selectedDevice)?.label}
        </span>
      )}
    </div>
  );
}