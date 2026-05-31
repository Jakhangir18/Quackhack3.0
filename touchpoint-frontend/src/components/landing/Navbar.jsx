import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Technology', href: '#technology' },
  { label: 'Use Cases', href: '#use-cases' },
  { label: 'Connect', href: '#connect' },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled ? 'bg-background/80 backdrop-blur-md border-b border-border' : ''
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-10 flex items-center justify-between h-16 md:h-20">
          <a href="#" className="font-serif text-2xl md:text-3xl text-foreground tracking-tight">
            Touchpoint
          </a>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-10">
            {NAV_ITEMS.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-300 tracking-wide uppercase"
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* Index button */}
          <button
            onClick={() => setMenuOpen(true)}
            className="md:hidden text-sm font-medium tracking-widest uppercase text-muted-foreground hover:text-foreground transition-colors"
          >
            Index
          </button>
        </div>
      </motion.nav>

      {/* Slide-out menu */}
      <AnimatePresence>
        {menuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-foreground/10 backdrop-blur-sm z-[60]"
              onClick={() => setMenuOpen(false)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed right-0 top-0 bottom-0 w-80 bg-primary z-[70] flex flex-col p-10"
            >
              <button
                onClick={() => setMenuOpen(false)}
                className="self-end text-primary-foreground/60 hover:text-primary-foreground transition-colors mb-16"
              >
                <X className="w-6 h-6" />
              </button>
              <div className="flex flex-col gap-8">
                {NAV_ITEMS.map((item, i) => (
                  <motion.a
                    key={item.label}
                    href={item.href}
                    onClick={() => setMenuOpen(false)}
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + i * 0.08 }}
                    className="text-3xl font-serif text-primary-foreground hover:text-primary-foreground/70 transition-colors"
                  >
                    {item.label}
                  </motion.a>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}