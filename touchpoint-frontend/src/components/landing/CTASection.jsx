import React from 'react';
import { motion } from 'framer-motion';
import PulseMotif from './PulseMotif';

export default function CTASection() {
  return (
    <section
      id="connect"
      className="relative bg-primary py-32 md:py-48 overflow-hidden"
    >
      {/* Decorative pulse motifs */}
      <div className="absolute top-16 left-16 opacity-20">
        <PulseMotif size={100} />
      </div>
      <div className="absolute bottom-16 right-16 opacity-20">
        <PulseMotif size={80} />
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-10 text-center relative z-10">
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-sm font-mono uppercase tracking-[0.3em] text-primary-foreground/50 mb-8"
        >
          Get in Touch
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="font-serif text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-primary-foreground tracking-tight leading-[0.95] mb-12"
        >
          Accessibility
          <br />
          <span className="italic">for everyone.</span>
        </motion.h2>

        <motion.a
          href="mailto:hello@touchpoint.dev"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="inline-flex items-center gap-3 bg-primary-foreground text-primary px-8 py-4 text-sm font-medium tracking-wide hover:bg-primary-foreground/90 transition-colors duration-300"
        >
          hello@touchpoint.dev
        </motion.a>
      </div>
    </section>
  );
}