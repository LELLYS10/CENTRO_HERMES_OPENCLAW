import { motion } from 'motion/react';

interface JarvisCoreProps {
  state: 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'ERROR';
}

export function JarvisCore({ state }: JarvisCoreProps) {
  const getVariants = () => {
    switch (state) {
      case 'LISTENING':
        return {
          scale: [1, 1.2, 1],
          opacity: [0.5, 1, 0.5],
          rotate: [0, 180, 360],
          transition: { repeat: Infinity, duration: 1.5 }
        };
      case 'THINKING':
        return {
          rotate: [0, 360],
          scale: [1, 0.9, 1],
          transition: { repeat: Infinity, duration: 0.8, ease: "linear" as const }
        };
      case 'SPEAKING':
        return {
          scale: [1, 1.3, 1],
          boxShadow: [
            "0 0 20px rgba(0, 255, 156, 0.3)",
            "0 0 50px rgba(0, 255, 156, 0.6)",
            "0 0 20px rgba(0, 255, 156, 0.3)"
          ],
          transition: { repeat: Infinity, duration: 0.5 }
        };
      case 'ERROR':
        return {
          scale: 1,
          backgroundColor: '#ef4444',
          boxShadow: "0 0 30px rgba(239, 68, 68, 0.8)"
        };
      default:
        return {
          scale: 1,
          opacity: 0.8,
          transition: { duration: 1 }
        };
    }
  };

  return (
    <div className="relative flex items-center justify-center w-64 h-64">
      {/* Background Rings */}
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute border border-neon/20 rounded-full"
          style={{
            width: `${100 + i * 40}%`,
            height: `${100 + i * 40}%`,
          }}
          animate={{
            rotate: i % 2 === 0 ? 360 : -360,
            scale: [1, i === 1 ? 1.05 : 0.95, 1],
          }}
          transition={{
            rotate: { repeat: Infinity, duration: 10 + i * 5, ease: "linear" as const },
            scale: { repeat: Infinity, duration: 4 + i, ease: "easeInOut" as const }
          }}
        />
      ))}

      {/* Outer Glow */}
      <div className="absolute inset-0 rounded-full bg-neon/5 blur-3xl animate-pulse" />

      {/* The Nexus */}
      <motion.div
        className="relative z-10 w-[280px] h-[280px] rounded-full border-2 border-neon bg-ink/40 backdrop-blur-md flex items-center justify-center overflow-hidden shadow-[0_0_40px_rgba(0,255,156,0.2)]"
        animate={getVariants()}
      >
        <div className="absolute inset-0 bg-gradient-to-tr from-neon/10 to-transparent animate-pulse" />
        
        {/* Inner Details */}
        <div className="w-[220px] h-[220px] rounded-full border border-dashed border-neon/30 flex items-center justify-center">
          <div className="w-[120px] h-[120px] rounded-full bg-radial from-neon/60 to-transparent opacity-60 flex items-center justify-center">
            {/* Center Visual Core */}
            <motion.div 
              className="w-4 h-4 bg-neon rounded-sm shadow-[0_0_15px_rgba(0,255,156,0.8)]"
              animate={{ rotate: 45 }}
            />
          </div>
        </div>

        {/* Status Line */}
        <div className="absolute top-[80%] text-[10px] font-mono text-neon tracking-widest uppercase">
           {state === 'THINKING' ? 'Analizando...' : state === 'SPEAKING' ? 'Respondendo...' : state}
        </div>

        {/* Scanning Line */}
        <motion.div 
          className="absolute h-1 w-full bg-neon/50 blur-sm"
          animate={{ top: ['0%', '100%', '0%'] }}
          transition={{ repeat: Infinity, duration: 3, ease: 'linear' as const }}
        />
      </motion.div>

      {/* System Pulse Indicator */}
      <div className="absolute -bottom-24 flex flex-col items-center gap-2">
        <motion.span 
          className="text-neon font-mono text-xs tracking-[0.4em] uppercase"
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          {state === 'IDLE' ? 'Protocolo Jarv-4' : 'Atividade Localizada'}
        </motion.span>
        <div className="flex gap-1.5 h-1 items-center">
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-neon rounded-full"
              animate={{
                height: state === 'IDLE' ? 4 : [4, i % 2 === 0 ? 12 : 8, 4],
                opacity: state === 'IDLE' ? 0.2 : 1
              }}
              transition={{ repeat: Infinity, duration: 0.4, delay: i * 0.05 }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
