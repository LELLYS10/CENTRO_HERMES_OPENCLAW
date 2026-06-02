import { motion } from 'motion/react';
import { Calendar, CheckCircle2, Clock, MapPin } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface SidePanelProps {
  events: any[];
  isConnected: boolean;
  onConnect: () => void;
}

export function SidePanel({ events, isConnected, onConnect }: SidePanelProps) {
  return (
    <div className="w-80 h-full glass-panel border-l border-neon/10 flex flex-col p-6 hidden lg:flex">
      <div className="flex items-center justify-between mb-8 overflow-hidden">
        <h2 className="text-neon font-mono text-xs uppercase tracking-[0.3em] text-glow">Agenda de hoje</h2>
        <div className="w-2 h-2 rounded-full bg-neon shadow-[0_0_8px_rgba(0,255,156,0.8)]" />
      </div>

      {!isConnected ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
          <Calendar className="w-12 h-12 text-neon/20" />
          <p className="text-neon/60 text-xs font-mono uppercase">Google Calendar Offline</p>
          <button 
            onClick={onConnect}
            className="px-4 py-2 bg-neon/10 border border-neon/30 text-neon text-[10px] font-mono rounded-sm hover:bg-neon/20 transition-all uppercase tracking-widest"
          >
            Sincronizar JARVIS
          </button>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-6 pr-2 custom-scrollbar">
          {events.length === 0 ? (
            <p className="text-neon/40 text-[10px] font-mono text-center">Nenhum compromisso detectado para hoje.</p>
          ) : (
            events.map((event, i) => (
              <motion.div
                key={event.id || i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="group relative p-3 border border-neon/5 hover:border-neon/20 transition-all bg-neon/[0.02]"
              >
                <div className="absolute -left-[1px] top-0 bottom-0 w-[2px] bg-neon opacity-0 group-hover:opacity-100 transition-all" />
                <h3 className="text-gray-100 text-xs font-medium mb-2 truncate group-hover:text-neon transition-colors">{event.summary}</h3>
                
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-neon/60 text-[10px]">
                    <Clock className="w-3 h-3" />
                    <span className="font-mono">{event.start?.dateTime ? format(new Date(event.start.dateTime), 'HH:mm', { locale: ptBR }) : 'Dia todo'}</span>
                  </div>
                  {event.location && (
                    <div className="flex items-center gap-2 text-neon/60 text-[10px]">
                      <MapPin className="w-3 h-3" />
                      <span className="truncate">{event.location}</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}

      {/* System Status Metrics */}
      <div className="mt-8 pt-8 border-t border-neon/10 space-y-4">
        <div className="text-[10px] font-mono text-neon/40 uppercase mb-4">Métricas de Integração</div>
        {[
          { label: 'Calendar Engine', uptime: isConnected },
          { label: 'Gmail Uplink', uptime: isConnected },
          { label: 'Drive Storage', uptime: isConnected },
          { label: 'Neural Matrix', uptime: true }
        ].map((stat, i) => (
          <div key={i} className="flex justify-between items-center h-4">
            <span className="text-neon/60 text-[9px] uppercase font-mono tracking-tighter">{stat.label}</span>
            <div className={`w-1.5 h-1.5 rounded-full transition-all duration-500 ${stat.uptime ? 'bg-neon shadow-[0_0_8px_rgba(0,255,156,0.6)]' : 'bg-gray-800 shadow-none'}`} />
          </div>
        ))}
      </div>
    </div>
  );
}
