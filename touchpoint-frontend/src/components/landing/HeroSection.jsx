import React from 'react';
import { motion } from 'framer-motion';
import PulseMotif from './PulseMotif';

export default function HeroSection({ heroImage }) {
  return (
    <section className="relative min-h-screen flex flex-col justify-center pt-20 pb-16 md:pb-24 overflow-hidden">
      {/* Subtle grid lines */}
      <div className="absolute inset-0 pointer-events-none opacity-30">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className="absolute top-0 bottom-0 border-l border-border"
            style={{ left: `${(i + 1) * (100 / 13)}%` }}
          />
        ))}
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-10 w-full relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-8 items-center">
          {/* Copy side */}
          <div className="order-2 lg:order-1">
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-sm font-mono uppercase tracking-[0.3em] text-muted-foreground mb-6"
            >
              Vibrotactile Braille Interface
            </motion.p>

            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="font-serif text-5xl sm:text-6xl md:text-7xl lg:text-[5.5rem] leading-[0.95] tracking-tight text-foreground mb-8"
            >
              Touch.
              <br />
              <span className="italic text-primary">The New</span>
              <br />
              Bandwidth.
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="text-lg md:text-xl leading-relaxed text-muted-foreground max-w-lg mb-10"
              style={{ lineHeight: '1.6' }}
            >
              Learn Braille. Navigate the web. Built for the 285 million people worldwide 
              with visual impairments — especially those who can't afford a $2,000 Braille 
              display. Prototyped from <em className="text-foreground not-italic font-medium">affordable parts</em>.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.65 }}
              className="flex items-center gap-6"
            >
              <a
                href="#technology"
                className="inline-flex items-center gap-3 bg-foreground text-background px-7 py-3.5 text-sm font-medium tracking-wide hover:bg-foreground/90 transition-colors duration-300"
              >
                Explore the Technology
              </a>
              <a
                href="#connect"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-300 tracking-wide"
              >
                Get in Touch →
              </a>
            </motion.div>
          </div>

          {/* Image side */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="order-1 lg:order-2 relative"
          >
            <div className="relative">
              <img
                src={heroImage}
                alt="Touchpoint vibrotactile device on human hand showing four precision haptic nodes"
                className="w-full h-auto object-cover"
              />
              {/* Pulse motif overlay */}
              <div className="absolute bottom-8 right-8">
                <PulseMotif size={60} />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}