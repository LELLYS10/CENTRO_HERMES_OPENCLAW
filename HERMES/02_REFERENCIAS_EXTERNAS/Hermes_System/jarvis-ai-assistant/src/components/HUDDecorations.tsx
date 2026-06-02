import { motion } from 'motion/react';

export function HUDDecorations() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* Theme Overlay Effects */}
      <div className="absolute inset-0 scanline z-50 opacity-15" />
      <div className="absolute inset-0 vignette z-40 opacity-40" />

      {/* Corner Brackets */}
      <div className="absolute top-8 left-8 w-16 h-16 border-t-2 border-l-2 border-neon/30 rounded-tl-lg" />
      <div className="absolute top-8 right-8 w-16 h-16 border-t-2 border-r-2 border-neon/30 rounded-tr-lg" />
      <div className="absolute bottom-12 left-8 w-16 h-16 border-b-2 border-l-2 border-neon/30 rounded-bl-lg" />
      <div className="absolute bottom-12 right-8 w-16 h-16 border-b-2 border-r-2 border-neon/30 rounded-br-lg" />

      {/* Grid Pattern */}
      <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#00FF9C_1px,transparent_1px),linear-gradient(to_bottom,#00FF9C_1px,transparent_1px)] bg-[size:40px_40px]" />

      {/* Scanning Gradients */}
      <motion.div 
        className="absolute inset-0 bg-gradient-to-b from-transparent via-neon/5 to-transparent h-40 w-full blur-2xl"
        animate={{ top: ['-20%', '120%'] }}
        transition={{ repeat: Infinity, duration: 8, ease: 'linear' }}
      />

      {/* Side Decorative Numbers */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 flex flex-col gap-4 text-[8px] font-mono text-neon/20 uppercase tracking-tighter">
        {[...Array(10)].map((_, i) => (
          <div key={i}>0{i} : SET_TRK_{Math.random().toString(16).slice(2, 6).toUpperCase()}</div>
        ))}
      </div>

      <div className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col gap-4 text-[8px] font-mono text-neon/20 uppercase tracking-tighter items-end">
        {[...Array(10)].map((_, i) => (
          <div key={i}>{Math.random().toString(10).slice(2, 8).toUpperCase()} : {i * 10}ms</div>
        ))}
      </div>
      
      {/* Animated Rotating Compass Style element */}
      <motion.div 
        className="absolute -bottom-20 -left-20 w-80 h-80 border border-neon/10 rounded-full flex items-center justify-center"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 40, ease: 'linear' }}
      >
        <div className="w-64 h-64 border border-dashed border-neon/20 rounded-full" />
        <div className="absolute top-0 h-4 w-[1px] bg-neon/40" />
        <div className="absolute bottom-0 h-4 w-[1px] bg-neon/40" />
        <div className="absolute left-0 w-4 h-[1px] bg-neon/40" />
        <div className="absolute right-0 w-4 h-[1px] bg-neon/40" />
      </motion.div>
    </div>
  );
}
