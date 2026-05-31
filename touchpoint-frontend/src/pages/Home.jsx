import React from 'react';
import Navbar from '../components/landing/Navbar';
import HeroSection from '../components/landing/HeroSection';
import TechSection from '../components/landing/TechSection';
import CTASection from '../components/landing/CTASection';
import TeamSection from '../components/landing/TeamSection';
import MarqueeFooter from '../components/landing/MarqueeFooter';
import BrailleDisplay from '../components/landing/BrailleDisplay';
import LiveBrailleDemo from '../components/landing/LiveBrailleDemo';

const IMAGES = {
  hero: 'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/38d2dc0ff_generated_ffc2da26.png',
  blueprint: 'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/38fddd951_generated_bd5d9f9e.png',
  useCases: [
    'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/61855dc5d_generated_c89cfc35.png',
    'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/e9b403268_generated_de9ea4b8.png',
    'https://media.base44.com/images/public/6a1b57b5cf422cb9c4fc3f05/9fda2dbb3_generated_0149dca2.png',
  ],
};

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection heroImage={IMAGES.hero} />
      <BrailleDisplay />
      <LiveBrailleDemo />
      <TechSection />
      <TeamSection />
      <CTASection />
      <MarqueeFooter />
    </div>
  );
}