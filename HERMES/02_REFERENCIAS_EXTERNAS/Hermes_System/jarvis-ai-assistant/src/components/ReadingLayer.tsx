import { motion, AnimatePresence } from 'motion/react';
import { Terminal } from 'lucide-react';

interface ReadingLayerProps {
  text: string;
  isModelResponding: boolean;
}

export function ReadingLayer({ text, isModelResponding }: ReadingLayerProps) {
  return (
    <AnimatePresence>
      {isModelResponding && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="fixed inset-0 z-40 flex items-center justify-center pointer-events-none p-10"
        >
          <div className="relative w-full max-w-4xl h-[60vh] bg-neon/5 backdrop-blur-sm border border-neon/20 overflow-hidden flex flex-col box-glow">
            {/* HUD Scanlines */}
            <div className="absolute inset-0 opacity-10 scanline" />
            
            <div className="flex items-center gap-3 p-4 border-b border-neon/20 bg-neon/10">
              <Terminal className="w-4 h-4 text-neon" />
              <span className="text-xs font-mono text-neon uppercase tracking-widest">Digital Information Stream</span>
              <div className="ml-auto flex gap-1">
                <div className="w-2 h-2 bg-neon/50 rounded-full animate-pulse" />
                <div className="w-8 h-1 bg-neon/30 rounded-full" />
              </div>
            </div>

            <div className="relative flex-1 p-6 font-mono text-sm text-neon leading-relaxed overflow-hidden">
              <div className="absolute top-0 right-0 p-2 text-[10px] opacity-30 select-none">
                LOC: AX-902 // STRM: 001x9
              </div>
              
              <motion.div 
                className="whitespace-pre-wrap"
                initial={{ y: 20 }}
                animate={{ y: 0 }}
              >
                {text}
                <motion.span
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ repeat: Infinity, duration: 0.8 }}
                  className="inline-block w-2 h-4 bg-neon ml-1"
                />
              </motion.div>

              {/* Decorative Tech Elements */}
              <div className="absolute bottom-4 right-4 flex flex-col gap-1 items-end">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="flex gap-1">
                    {[...Array(8)].map((_, j) => (
                      <div 
                        key={j} 
                        className="w-1 h-3 bg-neon/20"
                        style={{ opacity: Math.random() }}
                      />
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
