import React from 'react';

export default function PulseMotif({ size = 40, className = '' }) {
  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      {/* Static center dot */}
      <div
        className="absolute rounded-full bg-primary"
        style={{
          width: size * 0.2,
          height: size * 0.2,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
        }}
      />
      {/* Animated rings */}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="absolute rounded-full border border-primary animate-pulse-ring"
          style={{
            width: size * 0.5,
            height: size * 0.5,
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            animationDelay: `${i * 0.6}s`,
          }}
        />
      ))}
    </div>
  );
}