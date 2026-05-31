import React from 'react';
import { motion } from 'framer-motion';

const TEAM = [
  {
    name: 'William Tu',
    linkedin: 'https://www.linkedin.com/in/william-tu-17264438a/',
  },
  {
    name: 'Marcus Tin',
    linkedin: 'https://www.linkedin.com/in/marcustin',
  },
  {
    name: 'Jakhangir Tynshimov',
    linkedin: 'https://www.linkedin.com/in/tynshimov/',
  },
];

export default function TeamSection() {
  return (
    <section id="team" className="py-32 md:py-40 border-t border-border">
      <div className="max-w-7xl mx-auto px-6 md:px-10">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="mb-20"
        >
          <p className="text-sm font-mono uppercase tracking-[0.3em] text-muted-foreground mb-4">
            The Builders
          </p>
          <h2 className="font-serif text-4xl sm:text-5xl md:text-6xl tracking-tight text-foreground leading-[0.95]">
            Built at <span className="italic text-primary">QuackHacks 3.0.</span>
          </h2>
        </motion.div>

        {/* Team grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-border mb-16">
          {TEAM.map((member, i) => (
            <motion.a
              key={member.name}
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="bg-background p-10 md:p-12 group flex flex-col justify-between gap-8 hover:bg-secondary transition-colors duration-300"
            >
              <div>
                <p className="text-xs font-mono uppercase tracking-[0.25em] text-muted-foreground mb-4">
                  Team Member
                </p>
                <h3 className="font-serif text-2xl md:text-3xl text-foreground group-hover:text-primary transition-colors duration-300">
                  {member.name}
                </h3>
              </div>
              <span className="text-xs font-mono tracking-wide text-primary opacity-60 group-hover:opacity-100 transition-opacity duration-300">
                LinkedIn →
              </span>
            </motion.a>
          ))}
        </div>

        {/* GitHub link */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex items-center gap-6 flex-wrap"
        >
          <p className="text-sm text-muted-foreground font-mono">Open source on GitHub</p>
          <a
            href="https://github.com/Jakhangir18/Quackhack3.0"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 border border-foreground text-foreground px-7 py-3.5 text-sm font-medium tracking-wide hover:bg-foreground hover:text-background transition-colors duration-300"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            Jakhangir18/Quackhack3.0
          </a>
        </motion.div>

      </div>
    </section>
  );
}