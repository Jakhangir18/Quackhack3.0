import React from 'react';
import { motion } from 'framer-motion';

// Grade 1 Braille — internationally standardised dot patterns
// Dot numbering (standard Braille cell):
//  1 4
//  2 5
//  3 6
// Array index: [d1, d2, d3, d4, d5, d6]
const BRAILLE_MAP = {
  A: [1,0,0,0,0,0],
  B: [1,1,0,0,0,0],
  C: [1,0,0,1,0,0],
  D: [1,0,0,1,1,0],
  E: [1,0,0,0,1,0],
  F: [1,1,0,1,0,0],
  G: [1,1,0,1,1,0],
  H: [1,1,0,0,1,0],
  I: [0,1,0,1,0,0],
  J: [0,1,0,1,1,0],
  K: [1,0,1,0,0,0],
  L: [1,1,1,0,0,0],
  M: [1,0,1,1,0,0],
  N: [1,0,1,1,1,0],
  O: [1,0,1,0,1,0],
  P: [1,1,1,1,0,0],
  Q: [1,1,1,1,1,0],
  R: [1,1,1,0,1,0],
  S: [0,1,1,1,0,0],
  T: [0,1,1,1,1,0],
  U: [1,0,1,0,0,1],
  V: [1,1,1,0,0,1],
  W: [0,1,0,1,1,1],
  X: [1,0,1,1,0,1],
  Y: [1,0,1,1,1,1],
  Z: [1,0,1,0,1,1],
};

// "TOUCHPOINT" — each letter maps 1:1 to Grade 1 Braille
const WORD = ['T','O','U','C','H','P','O','I','N','T'];

function BrailleCell({ letter, dots, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.35, delay: index * 0.055 }}
      className="flex flex-col items-center gap-3"
    >
      {/* Dot grid: 3 rows × 2 cols */}
      <div className="flex gap-3">
        {/* Left column: dots 1, 2, 3 */}
        <div className="flex flex-col gap-[7px]">
          {[0, 1, 2].map((row) => (
            <div
              key={row}
              className={`w-[9px] h-[9px] md:w-[11px] md:h-[11px] rounded-full transition-all duration-200 ${
                dots[row]
                  ? 'bg-primary shadow-[0_0_6px_rgba(0,85,255,0.4)]'
                  : 'bg-border'
              }`}
            />
          ))}
        </div>
        {/* Right column: dots 4, 5, 6 */}
        <div className="flex flex-col gap-[7px]">
          {[3, 4, 5].map((dotIdx) => (
            <div
              key={dotIdx}
              className={`w-[9px] h-[9px] md:w-[11px] md:h-[11px] rounded-full transition-all duration-200 ${
                dots[dotIdx]
                  ? 'bg-primary shadow-[0_0_6px_rgba(0,85,255,0.4)]'
                  : 'bg-border'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Letter label below */}
      <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        {letter}
      </span>
    </motion.div>
  );
}

export default function BrailleDisplay() {
  return (
    <div className="border-t border-b border-border py-16 md:py-20">
      <div className="max-w-7xl mx-auto px-6 md:px-10">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-10 sm:gap-16">
          {/* Side label */}
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-xs font-mono uppercase tracking-[0.25em] text-muted-foreground whitespace-nowrap"
          >
            Grade 1 Braille
          </motion.p>

          {/* Braille cells */}
          <div className="flex items-end gap-5 md:gap-7 flex-wrap">
            {WORD.map((letter, i) => (
              <BrailleCell
                key={i}
                letter={letter}
                dots={BRAILLE_MAP[letter]}
                index={i}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}