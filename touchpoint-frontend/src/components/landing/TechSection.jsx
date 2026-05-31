import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const PARTS = [
  {
    image: 'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/fe8efefc8_raspberrypi5.jpg',
    label: 'Raspberry Pi 5',
    role: 'Central processor',
    desc: 'Runs the Python backend, drives Playwright to hit the accessibility API of any webpage\'s DOM, and orchestrates vibration output in real-time.',
  },
  {
    image: 'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/4f9be92c3_DIANN_vibrationmoros.jpg',
    label: 'Vibration Motors',
    role: 'Haptic output',
    desc: 'Coin-type ERM vibration motors — one per finger. Each maps to a Braille dot position, firing in sequence to encode Grade 1 Braille characters through touch.',
  },
  {
    image: 'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/a1cdaf3eb_breadboard.jpg',
    label: 'Breadboard',
    role: 'Rapid prototyping',
    desc: 'All components are wired together on a solderless breadboard, keeping the build accessible, modifiable, and reproducible with under $50 in parts.',
  },
];

const PIPELINE_STEPS = [
  { step: '01', title: 'You enter a URL', desc: 'Paste any web address into Touchpoint. A Wikipedia article, a news story, a form — anything on the open web.' },
  { step: '02', title: 'Playwright parses the page', desc: 'Our Python backend uses Playwright to hit the accessibility API of the DOM, extracting clean semantic text — no visual scraping.' },
  { step: '03', title: 'Text → Grade 1 Braille', desc: 'Each character is translated 1-to-1 into its Grade 1 Braille dot pattern. No contractions, no ambiguity.' },
  { step: '04', title: 'Fingers receive the signal', desc: 'Vibration motors fire in the precise dot sequence for each cell. Read character by character, at your own pace.' },
];

export default function TechSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <section id="technology" className="py-32 md:py-48 relative" ref={ref}>
      <div className="max-w-7xl mx-auto px-6 md:px-10">

        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="mb-20 md:mb-28"
        >
          <p className="text-sm font-mono uppercase tracking-[0.3em] text-muted-foreground mb-4">
            The Hardware
          </p>
          <h2 className="font-serif text-4xl sm:text-5xl md:text-6xl lg:text-7xl tracking-tight text-foreground max-w-4xl leading-[0.95]">
            Prototyped from <span className="italic text-primary">affordable parts.</span>
            <br />Braille displays cost $2,000.
          </h2>
        </motion.div>

        {/* Parts grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-border mb-28">
          {PARTS.map((part, i) => (
            <motion.div
              key={part.label}
              initial={{ opacity: 0, y: 24 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.15 + i * 0.12 }}
              className="bg-background flex flex-col"
            >
              <div className="aspect-[4/3] overflow-hidden bg-secondary flex items-center justify-center">
                <img
                  src={part.image}
                  alt={part.label}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-8 md:p-10 flex flex-col flex-1">
                <p className="text-xs font-mono uppercase tracking-[0.25em] text-primary mb-2">{part.role}</p>
                <h3 className="font-serif text-2xl md:text-3xl text-foreground mb-4">{part.label}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1" style={{ lineHeight: '1.7' }}>
                  {part.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* How it works pipeline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.4 }}
        >
          <p className="text-sm font-mono uppercase tracking-[0.3em] text-muted-foreground mb-12">
            How It Works
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-px bg-border">
            {PIPELINE_STEPS.map((step, i) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.5 + i * 0.1 }}
                className="bg-background p-8 md:p-10"
              >
                <span className="text-sm font-mono text-primary mb-4 block">{step.step}</span>
                <h3 className="font-serif text-xl md:text-2xl text-foreground mb-3">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed" style={{ lineHeight: '1.6' }}>
                  {step.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

      </div>
    </section>
  );
}