import React from 'react';

const MARQUEE_TEXT = 'TOUCHPOINT 2026 • QUACKHACKS 3.0 • BETTER WEB ACCESSIBILITY • ';

export default function MarqueeFooter() {
  const repeatedText = MARQUEE_TEXT.repeat(6);

  return (
    <footer className="bg-foreground text-background py-6 overflow-hidden">
      <div className="animate-marquee whitespace-nowrap">
        <span className="text-sm md:text-base font-mono tracking-[0.2em] uppercase opacity-60">
          {repeatedText}
        </span>
      </div>
    </footer>
  );
}