/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Mic, MicOff, Send, LogOut, Settings, History, Info, Square, RefreshCcw, LayoutDashboard, Calendar as CalendarIcon, Activity } from 'lucide-react';
import { JarvisCore } from './components/JarvisCore';
import { ReadingLayer } from './components/ReadingLayer';
import { SidePanel } from './components/SidePanel';
import { HUDDecorations } from './components/HUDDecorations';
import { useJarvis } from './hooks/useJarvis';
import { Toaster, toast } from 'react-hot-toast';

export default function App() {
  const [tokens, setTokens] = useState<any>(() => {
    const saved = localStorage.getItem('jarvis_tokens');
    return saved ? JSON.parse(saved) : null;
  });
  const [activeTab, setActiveTab] = useState<'CHAT' | 'HISTORY' | 'SETTINGS'>('CHAT');
  const [inputText, setInputText] = useState('');
  const [calendarEvents, setCalendarEvents] = useState<any[]>([]);
  const [currentTime, setCurrentTime] = useState(new Date());

  const { state, messages, readingText, handsFree, setHandsFree, listen, sendMessage, stopSpeaking, voices, selectedVoiceName, setVoice } = useJarvis(tokens);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, readingText]);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'OAUTH_AUTH_SUCCESS') {
        setTokens(event.data.tokens);
        localStorage.setItem('jarvis_tokens', JSON.stringify(event.data.tokens));
        toast.success("Link neural estabelecido. Bem-vindo de volta, Lellis.", {
          style: { background: '#020806', color: '#00FF9C', border: '1px solid rgba(0, 255, 156, 0.2)' }
        });
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const fetchCalendar = async () => {
    if (!tokens) return;
    try {
      const response = await fetch('/api/calendar/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tokens, action: 'list' })
      });
      const data = await response.json();
      if (Array.isArray(data)) setCalendarEvents(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (tokens) fetchCalendar();
  }, [tokens]);

  const handleAuth = async () => {
    const res = await fetch('/api/auth/url');
    const { url } = await res.json();
    window.open(url, 'Jarvis Auth', 'width=600,height=700');
  };

  const handleSendText = () => {
    if (!inputText.trim()) return;
    sendMessage(inputText);
    setInputText('');
  };

  return (
    <div className="relative min-h-screen bg-ink text-white selection:bg-neon/30 overflow-hidden flex flex-col font-sans">
      <Toaster position="top-right" />
      <HUDDecorations />

      {/* Header - Geometric Balance Style */}
      <header className="relative z-10 px-8 h-16 flex items-center justify-between border-b-2 border-neon backdrop-blur-md bg-ink/50">
        <div className="flex items-center gap-6">
          <div className="text-neon font-mono text-[10px] tracking-widest uppercase opacity-80 hidden md:block">System: Active</div>
          <div className="text-neon font-orbitron font-black text-xl tracking-[0.2em] italic text-glow">JARVIS v4.0.2</div>
        </div>
        
        <div className="hidden lg:flex items-center gap-8 text-neon font-mono text-[10px] tracking-widest uppercase opacity-80">
          <div className="flex items-center gap-2">
            <Activity className="w-3 h-3 animate-pulse" />
            <span>Neural Sync: 99.8%</span>
          </div>
          <div>{currentTime.toLocaleTimeString('pt-BR')} // {currentTime.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()}</div>
        </div>

        <div className="flex items-center gap-4">
           {/* Hands-free mode toggle */}
           <button 
             onClick={() => {
               setHandsFree(!handsFree);
               toast(handsFree ? "Modo mãos-livres desativado." : "Modo mãos-livres ativado. Jarvis ouvindo...", {
                 icon: handsFree ? '🔇' : '🎙️',
                 style: { background: '#020806', color: '#00FF9C', border: '1px solid rgba(0, 255, 156, 0.2)', fontSize: '10px' }
               });
             }}
             className={`flex items-center gap-2 px-3 py-1.5 rounded border transition-all ${
               handsFree 
               ? 'bg-neon/20 border-neon text-neon shadow-[0_0_10px_rgba(0,255,156,0.3)]' 
               : 'border-neon/30 text-neon/40 hover:border-neon/60'
             }`}
           >
             <div className={`w-1.5 h-1.5 rounded-full ${handsFree ? 'bg-neon animate-pulse' : 'bg-gray-600'}`} />
             <span className="text-[10px] font-mono uppercase tracking-tighter">Hands-Free</span>
           </button>

           <button onClick={handleAuth} className="p-2 text-neon/40 hover:text-neon transition-colors"><Settings className="w-4 h-4" /></button>
        </div>
      </header>

      {/* Main Content Area - HUD Grid Style */}
      <main className="relative z-10 flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-[280px_1fr_280px] p-6 gap-6">
        
        {/* Sidebar Left: Status & Shortcuts */}
        <aside className="hidden lg:flex flex-col gap-6">
          <div className="glass-panel rounded flex flex-col p-5 relative min-h-[160px]">
             {/* Corner Decorations */}
             <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-neon" />
             <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-neon" />
             <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-neon" />
             <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-neon" />
             
             <div className="text-neon/50 text-[10px] font-mono uppercase tracking-widest border-b border-neon/10 pb-2 mb-4">Módulos Ativos</div>
             <div className="space-y-3">
               {[
                 { label: 'Chat Link', active: true, icon: Mic },
                 { label: 'Calendar Engine', active: !!tokens, icon: CalendarIcon },
                 { label: 'Neural Memory', active: true, icon: History }
               ].map((mod, i) => (
                 <div key={i} className="flex items-center justify-between">
                   <div className="flex items-center gap-3">
                     <mod.icon className={`w-3.5 h-3.5 ${mod.active ? 'text-neon' : 'text-gray-600'}`} />
                     <span className={`text-[11px] font-mono uppercase ${mod.active ? 'text-neon/80' : 'text-gray-600'}`}>{mod.label}</span>
                   </div>
                   <div className={`w-1.5 h-1.5 rounded-full ${mod.active ? 'bg-neon shadow-[0_0_5px_#00FF9C]' : 'bg-gray-800'}`} />
                 </div>
               ))}
             </div>
          </div>

          <div className="glass-panel rounded p-5 flex-1 relative flex flex-col">
             <div className="text-neon/50 text-[10px] font-mono uppercase tracking-widest border-b border-neon/10 pb-2 mb-4 mt-6">Matriz de Voz</div>
             <div className="space-y-2">
                <select 
                  value={selectedVoiceName || ''}
                  onChange={(e) => setVoice(e.target.value)}
                  className="w-full bg-black/40 border border-neon/20 rounded p-1.5 text-[9px] font-mono text-neon outline-none focus:border-neon/50 appearance-none cursor-pointer"
                >
                  {voices.filter(v => v.lang.startsWith('pt')).map(voice => (
                    <option key={voice.name} value={voice.name} className="bg-ink">
                      {voice.name.replace('Google ', '').replace('Microsoft ', '').split(' - ')[0]}
                    </option>
                  ))}
                </select>
                <div className="text-[8px] font-mono text-neon/30 uppercase text-center">Sintetizador Neural</div>
             </div>

             <div className="text-neon/50 text-[10px] font-mono uppercase tracking-widest border-b border-neon/10 pb-2 mb-4 mt-6">Protocolos de Resposta</div>
             <div className="space-y-2">
                {[
                  { label: 'Limpar Memória', action: () => sendMessage("Limpar histórico de conversa") },
                  { label: 'Recalibrar Voz', action: () => sendMessage("Teste de áudio Jarvis") },
                  { label: 'Resumo do Dia', action: () => sendMessage("Jarvis, qual meu resumo de hoje?") }
                ].map((btn, i) => (
                  <button 
                    key={i}
                    onClick={btn.action}
                    className="w-full text-left p-2 text-[10px] font-mono uppercase text-neon/40 hover:text-neon hover:bg-neon/10 border border-transparent hover:border-neon/20 transition-all"
                  >
                    {">"} {btn.label}
                  </button>
                ))}
             </div>
             
             <div className="mt-auto pt-6">
                <div className="text-[32px] font-orbitron text-white leading-none">24°C</div>
                <div className="text-[10px] font-mono text-neon/60 uppercase tracking-widest mt-1">Ambiente: Otimizado</div>
             </div>
          </div>
        </aside>

        {/* Center: Core Visualizer & Active Conversation */}
        <section className="flex flex-col relative h-full">
          <div className="flex-1 flex flex-col items-center justify-center relative min-h-[400px]">
            <JarvisCore state={state} />
            <ReadingLayer text={readingText} isModelResponding={state === 'SPEAKING' || state === 'THINKING'} />
          </div>

          {/* Chat Interaction - Geometric Balance Style */}
          <div className="mt-auto w-full max-w-3xl mx-auto flex flex-col gap-4 pb-4">
             {/* Recent Messages Preview */}
             <div className="max-h-[200px] overflow-y-auto px-4 space-y-4 custom-scrollbar">
                {messages.slice(-3).map((msg, i) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-3 text-sm font-mono leading-relaxed relative ${
                      msg.role === 'user' 
                      ? 'border-r-3 border-white text-right pr-4 opacity-70' 
                      : 'border-l-3 border-neon bg-neon/5 pl-4'
                    }`}
                  >
                    <div className={`text-[8px] font-bold uppercase mb-1 ${msg.role === 'user' ? 'text-white/40' : 'text-neon/40'}`}>
                      {msg.role === 'user' ? 'Operator' : 'Jarvis'}
                    </div>
                    {msg.text}
                  </motion.div>
                ))}
                <div ref={messagesEndRef} />
             </div>

             {/* Input Controls */}
             <div className="flex flex-col gap-2">
                <div className="flex items-center gap-3">
                  <div className="flex-1 glass-panel rounded p-1 flex items-center">
                    <input 
                      type="text"
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
                      placeholder="DIRETRIZ DE COMANDO..."
                      className="flex-1 bg-transparent border-none text-neon font-mono text-xs p-3 focus:ring-0 uppercase placeholder:text-neon/20"
                    />
                    <button 
                      onClick={handleSendText}
                      className="p-3 text-neon hover:text-white transition-colors"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>

                  <button 
                    onClick={listen}
                    disabled={state === 'LISTENING' || state === 'THINKING'}
                    className={`w-12 h-12 rounded flex items-center justify-center transition-all border ${
                      state === 'LISTENING' 
                      ? 'bg-red-500/20 border-red-500 text-red-500 animate-pulse' 
                      : 'glass-panel border-neon/30 text-neon hover:bg-neon/20'
                    }`}
                  >
                    {state === 'LISTENING' ? <Square className="w-4 h-4" /> : <Mic className="w-5 h-5" />}
                  </button>
                </div>

                {/* Status Bar for Input */}
                <div className="flex justify-between items-center px-1">
                   <div className="flex gap-4">
                     <div className="flex items-center gap-2">
                        <div className="w-1 h-3 bg-neon/30" />
                        <span className="text-[8px] font-mono text-neon/40 uppercase tracking-widest">Uplink: Synchronized</span>
                     </div>
                     <div className="flex items-center gap-2">
                        <div className="w-1 h-3 bg-neon/30" />
                        <span className="text-[8px] font-mono text-neon/40 uppercase tracking-widest">Buffer: Clear</span>
                     </div>
                   </div>
                   <div className="flex gap-2">
                     {[...Array(4)].map((_, i) => (
                       <div key={i} className={`w-3 h-1 ${i === 0 ? 'bg-neon' : 'bg-neon/20'}`} />
                     ))}
                   </div>
                </div>
             </div>
          </div>
        </section>

        {/* Sidebar Right: Agenda & History Summary */}
        <aside className="hidden lg:flex flex-col gap-6 overflow-hidden">
          <SidePanel 
            events={calendarEvents} 
            isConnected={!!tokens} 
            onConnect={handleAuth} 
          />

          <div className="glass-panel rounded p-5 relative">
             <div className="text-neon/50 text-[10px] font-mono uppercase tracking-widest border-b border-neon/10 pb-2 mb-4">Registros Recentes</div>
             <div className="space-y-4 max-h-[200px] overflow-y-auto custom-scrollbar">
                {messages.length === 0 ? (
                  <p className="text-[10px] font-mono text-neon/20 italic uppercase">Sem entradas no log.</p>
                ) : (
                  messages.map((msg, i) => (
                    <div key={i} className="border-l border-neon/10 pl-3">
                       <div className="text-[8px] text-neon/30 font-mono mb-1">LOG_{i.toString().padStart(3, '0')}</div>
                       <p className="text-[10px] text-gray-400 line-clamp-1 group-hover:line-clamp-none transition-all">{msg.text}</p>
                    </div>
                  ))
                )}
             </div>
          </div>
        </aside>
        
      </main>

      {/* Persistent Global Status Bar */}
      <footer className="relative z-10 h-8 border-t border-neon/10 flex items-center justify-between px-8 bg-ink/80 text-[8px] font-mono text-neon/40 uppercase tracking-[0.2em]">
         <div className="flex items-center gap-8">
           <div className="flex items-center gap-2">
             <div className="w-1.5 h-1.5 bg-neon rounded-full" />
             <span>Core Load: 12.4%</span>
           </div>
           <div className="flex items-center gap-2">
             <div className="w-1.5 h-1.5 bg-amber-500 rounded-full" />
             <span>Security: Max Protocol</span>
           </div>
         </div>
         <div className="flex items-center gap-4">
            <LayoutDashboard className="w-3 h-3 opacity-50" />
            <span>X-Project Jarvis | Global Hub</span>
         </div>
      </footer>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 2px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 255, 156, 0.05);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 255, 156, 0.2);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 255, 156, 0.4);
        }
      `}</style>
    </div>
  );
}
