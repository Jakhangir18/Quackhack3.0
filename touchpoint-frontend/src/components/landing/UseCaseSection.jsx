import React, { useRef, useState } from 'react';
import { motion, useInView } from 'framer-motion';

const USE_CASES = [
  {
    title: 'Accessibility',
    subtitle: 'Redefining Braille for the Digital Age',
    description: 'A wearable Braille output that goes everywhere the user does — no desktop device required. Real-time translation of any digital text into tactile sensation.',
    metric: '285M+',
    metricLabel: 'visually impaired people globally',
  },
  {
    title: 'Extended Reality',
    subtitle: 'Adding Touch to Virtual Worlds',
    description: 'Haptic feedback for VR/AR applications that goes beyond rumble motors. Feel textures, receive spatial cues, and interact with virtual objects through precision vibration.',
    metric: '$72B',
    metricLabel: 'projected XR market by 2028',
  },
  {
    title: 'Silent Communication',
    subtitle: 'Data Without Sound or Screen',
    description: 'Discreet, eyes-free notification and messaging through encoded vibrotactile patterns. Navigation cues, alerts, and messages — all through touch.',
    metric: '∞',
    metricLabel: 'applications in defense, medical, industrial',
  },
];

export default function UseCaseSection({ images }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [hoveredIndex, setHoveredIndex] = useState(null);

  return (
    <section id="use-cases" className="py-32 md:py-48" ref={ref}>
      <div className="max-w-7xl mx-auto px-6 md:px-10">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="mb-20 md:mb-28"
        >
          <p className="text-sm font-mono uppercase tracking-[0.3em] text-muted-foreground mb-4">
            Market Applications
          </p>
          <h2 className="font-serif text-4xl sm:text-5xl md:text-6xl lg:text-7xl tracking-tight text-foreground max-w-4xl leading-[0.95]">
            One device, <span className="italic text-primary">infinite</span> interfaces.
          </h2>
        </motion.div>

        {/* Use case cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-px bg-border">
          {USE_CASES.map((uc, i) => (
            <motion.div
              key={uc.title}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 + i * 0.15 }}
              className="bg-background relative overflow-hidden group cursor-default"
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Image */}
              <div className="relative aspect-[4/3] overflow-hidden">
                <img
                  src={images[i]}
                  alt={`${uc.title} use case for Touchpoint device`}
                  className="w-full h-full object-cover transition-all duration-700 group-hover:scale-105 group-hover:opacity-30"
                />
                {/* Overlay on hover */}
                <div
                  className={`absolute inset-0 flex flex-col justify-center items-center p-8 transition-opacity duration-500 ${
                    hoveredIndex === i ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  <p className="text-5xl md:text-6xl font-serif text-foreground mb-2">
                    {uc.metric}
                  </p>
                  <p className="text-sm font-mono uppercase tracking-wider text-muted-foreground text-center">
                    {uc.metricLabel}
                  </p>
                </div>
              </div>

              {/* Text content */}
              <div className="p-8 md:p-10">
                <p className="text-sm font-mono text-primary uppercase tracking-wider mb-3">
                  {uc.subtitle}
                </p>
                <h3 className="font-serif text-2xl md:text-3xl text-foreground mb-4">
                  {uc.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed" style={{ lineHeight: '1.6' }}>
                  {uc.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}