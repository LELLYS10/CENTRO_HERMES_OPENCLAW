import { useState, useCallback, useEffect, useRef } from 'react';
import { chatWithJarvis } from '../services/gemini.ts';

export type JarvisState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'ERROR';

export function useJarvis(tokens: any) {
  const [state, setState] = useState<JarvisState>('IDLE');
  const [messages, setMessages] = useState<{ role: 'user' | 'jarvis', text: string }[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [readingText, setReadingText] = useState('');
  const [handsFree, setHandsFree] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceName, setSelectedVoiceName] = useState<string | null>(() => localStorage.getItem('jarvis_voice'));
  
  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef(false);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);
  const handleSendMessageRef = useRef<any>(null);

  handleSendMessageRef.current = async (text: string) => {
    if (!text.trim()) return;
    setState('THINKING');
    const newUserMsg = { role: 'user' as const, text };
    setMessages(prev => [...prev, newUserMsg]);

    try {
      const response = await chatWithJarvis([...messages, newUserMsg], history);
      
      let finalResponseText = response.text || '';
      
      if (response.functionCalls) {
        for (const fc of response.functionCalls) {
          let service = 'calendar';
          if (fc.name.includes('Email') || fc.name.includes('Gmail')) service = 'gmail';
          if (fc.name.includes('Drive')) service = 'drive';
          if (fc.name.includes('Sheet')) service = 'sheets';
          if (fc.name === 'checkSystemIntegrity') service = 'system';

          const action = fc.name === 'checkSystemIntegrity' ? 'integrity' :
                         fc.name.toLowerCase().includes('list') ? 'list' : 
                         fc.name.toLowerCase().includes('create') ? 'create' :
                         fc.name.toLowerCase().includes('draft') ? 'draft' :
                         fc.name.toLowerCase().includes('search') ? 'search' :
                         fc.name.toLowerCase().includes('read') ? 'read' :
                         fc.name.toLowerCase().includes('delete') ? 'delete' : '';

          try {
            const apiResponse = await fetch('/api/google/proxy', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ tokens, service, action, data: fc.args })
            });

            if (!apiResponse.ok) {
              if (apiResponse.status === 401) {
                finalResponseText = "Senhor Lellis, recebi um aviso de acesso negado. Parece que nosso link neural com o Google expirou. Por favor, reinicie a sincronização.";
                break;
              }
              throw new Error(`Status: ${apiResponse.status}`);
            }
            
            const result = await apiResponse.json();
            
            const toolFollowup = await chatWithJarvis(
              [...messages, newUserMsg], 
              [...history, { role: 'user', parts: [{ text }] }, { role: 'model', parts: [{ functionCall: fc }] }, { role: 'user', parts: [{ functionResponse: { name: fc.name, response: result } }] }]
            );
            finalResponseText = toolFollowup.text || '';
            setHistory(prev => [...prev, { role: 'user', parts: [{ text }] }, { role: 'model', parts: [{ functionCall: fc }] }, { role: 'user', parts: [{ functionResponse: { name: fc.name, response: result } }] }, { role: 'model', parts: [{ text: finalResponseText }] }]);
          } catch (apiError) {
            console.error('API Context Error:', apiError);
            finalResponseText = "Senhor, encontrei uma falha ao acessar os servidores do Google. Por favor, verifique a conexão.";
            break; 
          }
        }
      } else {
        setHistory(prev => [...prev, { role: 'user', parts: [{ text }] }, { role: 'model', parts: [{ text: finalResponseText }] }]);
      }

      setMessages(prev => [...prev, { role: 'jarvis', text: finalResponseText }]);
      speak(finalResponseText);
    } catch (error) {
      console.error('Jarvis Thinking Error:', error);
      setState('ERROR');
      speak("Sinto muito, senhor. Encontrei um erro em meus processadores neurais.");
    }
  };

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition && !recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'pt-BR';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        isListeningRef.current = true;
        setState('LISTENING');
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (handleSendMessageRef.current) handleSendMessageRef.current(transcript);
      };

      recognition.onend = () => {
        isListeningRef.current = false;
        setState(prev => prev === 'LISTENING' ? 'IDLE' : prev);
      };

      recognition.onerror = (event: any) => {
        isListeningRef.current = false;
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
          console.error('Speech Error:', event.error);
          setState('ERROR');
        } else {
          setState('IDLE');
        }
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const listen = useCallback(() => {
    if (recognitionRef.current) {
      if (isListeningRef.current) return;
      
      try {
        window.speechSynthesis.cancel();
        setState('LISTENING');
        recognitionRef.current.start();
      } catch (e) {
        console.warn('Recognition start failed:', e);
      }
    } else {
      alert('Seu navegador não suporta reconhecimento de voz.');
    }
  }, []);

  const speak = useCallback((text: string) => {
    if (!window.speechSynthesis) return;
    
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.0; // Slightly faster for confidence
    utterance.pitch = 0.95; // Slightly lower for male tone
    
    // Prioritize specific high-quality male voices or standard ones
    const voice = voices.find(v => v.name === selectedVoiceName) || 
                  voices.find(v => v.lang.startsWith('pt') && (v.name.includes('Daniel') || v.name.includes('António') || v.name.includes('Male') || v.name.includes('Ricardo') || v.name.includes('Standard-B'))) ||
                  voices.find(v => v.lang.startsWith('pt') && v.name.includes('Natural')) ||
                  voices.find(v => v.lang.startsWith('pt'));

    if (voice) utterance.voice = voice;

    utterance.onstart = () => setState('SPEAKING');
    utterance.onend = () => {
      setState('IDLE');
      if (handsFree) {
        setTimeout(() => listen(), 400); 
      }
    };
    utterance.onerror = () => setState('IDLE');

    synthesisRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    
    let charIndex = 0;
    setReadingText('');
    const interval = setInterval(() => {
      if (charIndex < text.length) {
        setReadingText(prev => prev + text[charIndex]);
        charIndex++;
      } else {
        clearInterval(interval);
      }
    }, 25);
  }, [handsFree, voices, listen, selectedVoiceName]);

  const handleSendMessage = useCallback(async (text: string) => {
    if (handleSendMessageRef.current) await handleSendMessageRef.current(text);
  }, []);

  useEffect(() => {
    const updateVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
      
      if (!localStorage.getItem('jarvis_voice')) {
        const best = 
          availableVoices.find(v => v.lang.startsWith('pt') && v.name.includes('Natural')) ||
          availableVoices.find(v => v.lang.startsWith('pt') && v.name.includes('Premium')) ||
          availableVoices.find(v => v.lang.startsWith('pt') && v.name.includes('Google')) ||
          availableVoices.find(v => v.lang.startsWith('pt'));
        
        if (best) {
          setSelectedVoiceName(best.name);
          localStorage.setItem('jarvis_voice', best.name);
        }
      }
    };
    if (window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = updateVoices;
      updateVoices();
    }
  }, []);

  return {
    state,
    messages,
    readingText,
    handsFree,
    setHandsFree,
    voices,
    selectedVoiceName,
    setVoice: (name: string) => {
      setSelectedVoiceName(name);
      localStorage.setItem('jarvis_voice', name);
    },
    listen,
    sendMessage: handleSendMessage,
    stopSpeaking: () => {
      window.speechSynthesis.cancel();
      setState('IDLE');
    }
  };
}
