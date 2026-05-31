import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Runtime-overridable Pi URL — paste your ngrok URL into the input at the bottom of the demo.
// Falls back to the env var, then to mDNS for local use.
const DEFAULT_PI_URL = import.meta.env.VITE_PI_URL || 'https://antennae-comma-kissable.ngrok-free.dev';

// ngrok free tier shows an interstitial page unless this header/param is present.
const NGROK_HEADERS = { 'ngrok-skip-browser-warning': 'true' };

const BRAILLE_MAP = {
  a:[1,0,0,0,0,0], b:[1,1,0,0,0,0], c:[1,0,0,1,0,0],
  d:[1,0,0,1,1,0], e:[1,0,0,0,1,0], f:[1,1,0,1,0,0],
  g:[1,1,0,1,1,0], h:[1,1,0,0,1,0], i:[0,1,0,1,0,0],
  j:[0,1,0,1,1,0], k:[1,0,1,0,0,0], l:[1,1,1,0,0,0],
  m:[1,0,1,1,0,0], n:[1,0,1,1,1,0], o:[1,0,1,0,1,0],
  p:[1,1,1,1,0,0], q:[1,1,1,1,1,0], r:[1,1,1,0,1,0],
  s:[0,1,1,1,0,0], t:[0,1,1,1,1,0], u:[1,0,1,0,0,1],
  v:[1,1,1,0,0,1], w:[0,1,0,1,1,1], x:[1,0,1,1,0,1],
  y:[1,0,1,1,1,1], z:[1,0,1,0,1,1], ' ':[0,0,0,0,0,0],
};

// Single animated Braille cell — 2 columns × 3 rows
function BrailleCell({ char, pattern, dim = false }) {
  const dots = pattern || BRAILLE_MAP[char?.toLowerCase()] || [0,0,0,0,0,0];
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="flex gap-2">
        {/* left column: dots 0,1,2 */}
        <div className="flex flex-col gap-[5px]">
          {[0,1,2].map(i => (
            <div
              key={i}
              className={`w-3 h-3 rounded-full transition-all duration-100 ${
                !dim && dots[i]
                  ? 'bg-primary shadow-[0_0_10px_rgba(0,85,255,0.6)]'
                  : 'bg-border'
              }`}
            />
          ))}
        </div>
        {/* right column: dots 3,4,5 */}
        <div className="flex flex-col gap-[5px]">
          {[3,4,5].map(i => (
            <div
              key={i}
              className={`w-3 h-3 rounded-full transition-all duration-100 ${
                !dim && dots[i]
                  ? 'bg-primary shadow-[0_0_10px_rgba(0,85,255,0.6)]'
                  : 'bg-border'
              }`}
            />
          ))}
        </div>
      </div>
      <span className="text-[9px] font-mono uppercase tracking-widest text-muted-foreground">
        {char === ' ' ? '·' : (char || '?')}
      </span>
    </div>
  );
}

const PHASE_LABELS = {
  extracting: 'Extracting page…',
  ranking:    'Gemini ranking…',
  buzzing:    'Buzzing Braille…',
};

export default function LiveBrailleDemo() {
  const [url, setUrl]           = useState('');
  const [piUrl, setPiUrl]       = useState(DEFAULT_PI_URL);
  const [showPiInput, setShowPiInput] = useState(false);
  const [phase, setPhase]       = useState('idle'); // idle|extracting|ranking|buzzing|done|error
  const [phaseMsg, setPhaseMsg] = useState('');
  const [tree, setTree]         = useState(null);   // llm_build_tree output
  const [currentItem, setCurrent] = useState(null); // {section, item, section_idx, item_idx, total_items}
  const [currentChar, setCurrentChar] = useState(null); // {char, pattern}
  const [log, setLog]           = useState([]);     // completed items
  const [errorMsg, setErrorMsg] = useState('');
  const sseRef = useRef(null);

  const resetState = () => {
    setPhase('idle');
    setPhaseMsg('');
    setTree(null);
    setCurrent(null);
    setCurrentChar(null);
    setLog([]);
    setErrorMsg('');
  };

  const openStream = useCallback((activePiUrl) => {
    if (sseRef.current) sseRef.current.close();
    // ngrok free tier: bypass interstitial via query param (EventSource can't set headers)
    const streamUrl = `${activePiUrl}/stream?ngrok-skip-browser-warning=true`;
    const es = new EventSource(streamUrl);
    sseRef.current = es;

    es.onmessage = (e) => {
      const event = JSON.parse(e.data);

      if (event.type === 'ping') return;

      if (event.type === 'status') {
        setPhase(event.phase);
        setPhaseMsg(event.message);
      }

      if (event.type === 'tree_ready') {
        setTree(event.tree);
        setPhase('buzzing');
      }

      if (event.type === 'item') {
        setCurrent(event);
        setCurrentChar(null);
        setLog(prev => [...prev, event]);
      }

      if (event.type === 'char') {
        setCurrentChar(event);
      }

      if (event.type === 'done') {
        setPhase('done');
        es.close();
      }

      if (event.type === 'error') {
        setErrorMsg(event.message);
        setPhase('error');
        es.close();
      }
    };

    es.onerror = () => {
      setErrorMsg('Could not connect to Pi. Is the server running?');
      setPhase('error');
      es.close();
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    resetState();
    setPhase('extracting');

    // Open SSE first so we don't miss early events
    openStream(piUrl);

    try {
      const res = await fetch(`${piUrl}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...NGROK_HEADERS },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
    } catch (err) {
      setErrorMsg(err.message);
      setPhase('error');
      if (sseRef.current) sseRef.current.close();
    }
  };

  useEffect(() => () => sseRef.current?.close(), []);

  const isActive = phase !== 'idle' && phase !== 'done' && phase !== 'error';

  return (
    <section id="demo" className="border-t border-border py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-6 md:px-10">

        {/* Header */}
        <div className="mb-12">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-xs font-mono uppercase tracking-[0.3em] text-muted-foreground mb-4"
          >
            Live Demo
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="font-serif text-3xl sm:text-4xl md:text-5xl text-foreground leading-tight"
          >
            Read any webpage
            <br />
            <span className="italic text-primary">in Braille.</span>
          </motion.h2>
        </div>

        {/* Pi URL settings toggle */}
        <div className="mb-6 max-w-2xl">
          <button
            type="button"
            onClick={() => setShowPiInput(v => !v)}
            className="text-xs font-mono text-muted-foreground hover:text-foreground transition-colors tracking-wide flex items-center gap-2"
          >
            <span className={`inline-block transition-transform duration-150 ${showPiInput ? 'rotate-90' : ''}`}>▶</span>
            Pi server: {piUrl}
          </button>
          <AnimatePresence>
            {showPiInput && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="flex gap-2 mt-3">
                  <input
                    type="url"
                    defaultValue={piUrl}
                    onBlur={e => setPiUrl(e.target.value.replace(/\/$/, ''))}
                    placeholder="https://yourname.ngrok-free.app"
                    className="flex-1 bg-background border border-border px-3 py-2 text-xs font-mono text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-colors"
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1.5">
                  Paste your ngrok URL here — no rebuild needed.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* URL Input */}
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-3 mb-16 max-w-2xl"
        >
          <input
            type="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://andrewkelley.me"
            className="flex-1 bg-background border border-border px-4 py-3 text-sm font-mono text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-colors"
          />
          <button
            type="submit"
            disabled={isActive || !url.trim()}
            className="bg-foreground text-background px-6 py-3 text-sm font-medium tracking-wide hover:bg-foreground/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {isActive ? 'Reading…' : 'Read Page'}
          </button>
        </motion.form>

        {/* Output area */}
        <AnimatePresence mode="wait">

          {phase === 'idle' && (
            <motion.p key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="text-sm font-mono text-muted-foreground">
              Enter a URL above to see live Braille output.
            </motion.p>
          )}

          {(phase === 'extracting' || phase === 'ranking') && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex items-center gap-3">
              <span className="text-xs font-mono uppercase tracking-[0.3em] text-muted-foreground">
                {phaseMsg || PHASE_LABELS[phase]}
              </span>
              <div className="flex gap-1">
                {[0,1,2].map(i => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"
                    style={{ animationDelay: `${i * 0.2}s` }} />
                ))}
              </div>
            </motion.div>
          )}

          {phase === 'error' && (
            <motion.p key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="text-sm font-mono text-red-500">
              Error: {errorMsg}
            </motion.p>
          )}

          {(phase === 'buzzing' || phase === 'done') && (
            <motion.div key="buzzing" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-10">

              {/* Left: live Braille cell + current item */}
              <div className="space-y-8">
                <div>
                  <p className="text-xs font-mono uppercase tracking-[0.25em] text-muted-foreground mb-5">
                    {phase === 'done' ? 'Complete' : 'Now buzzing'}
                  </p>

                  {/* Giant current character */}
                  {currentChar ? (
                    <motion.div
                      key={currentChar.char}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.08 }}
                      className="flex items-start gap-8"
                    >
                      {/* Big Braille cell */}
                      <div className="flex gap-3 shrink-0">
                        <div className="flex flex-col gap-2">
                          {[0,1,2].map(i => (
                            <div key={i}
                              className={`w-5 h-5 rounded-full transition-all duration-75 ${
                                currentChar.pattern[i]
                                  ? 'bg-primary shadow-[0_0_14px_rgba(0,85,255,0.7)]'
                                  : 'bg-border'
                              }`}
                            />
                          ))}
                        </div>
                        <div className="flex flex-col gap-2">
                          {[3,4,5].map(i => (
                            <div key={i}
                              className={`w-5 h-5 rounded-full transition-all duration-75 ${
                                currentChar.pattern[i]
                                  ? 'bg-primary shadow-[0_0_14px_rgba(0,85,255,0.7)]'
                                  : 'bg-border'
                              }`}
                            />
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-5xl font-mono font-bold text-foreground leading-none mb-2">
                          {currentChar.char === ' ' ? '·' : currentChar.char.toUpperCase()}
                        </p>
                        <p className="text-xs font-mono text-muted-foreground">
                          {currentChar.pattern.join(' ')}
                        </p>
                      </div>
                    </motion.div>
                  ) : (
                    <div className="h-16 flex items-center">
                      <div className="flex gap-1">
                        {[0,1,2].map(i => (
                          <div key={i} className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"
                            style={{ animationDelay: `${i * 0.15}s` }} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Current item info */}
                {currentItem && (
                  <div className="border border-border p-4 space-y-1">
                    <p className="text-xs font-mono uppercase tracking-[0.2em] text-muted-foreground">
                      {currentItem.section}
                    </p>
                    <p className="text-sm font-medium text-foreground">{currentItem.item}</p>
                    <p className="text-xs text-muted-foreground">
                      item {currentItem.item_idx + 1} / {currentItem.total_items}
                    </p>
                  </div>
                )}

                {/* Inline character strip for current item */}
                {currentItem && (
                  <div className="flex flex-wrap gap-3">
                    {currentItem.item.toLowerCase().split('').map((ch, i) => (
                      <BrailleCell
                        key={i}
                        char={ch}
                        dim={
                          currentChar
                            ? i > currentItem.item.toLowerCase().indexOf(currentChar.char, 0)
                            : true
                        }
                      />
                    ))}
                  </div>
                )}
              </div>

              {/* Right: scrolling log of completed / upcoming items */}
              <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
                <p className="text-xs font-mono uppercase tracking-[0.25em] text-muted-foreground sticky top-0 bg-background pb-2">
                  Navigation tree
                </p>
                {tree?.sections?.map((sec, si) => (
                  <div key={si} className="space-y-1">
                    <p className="text-xs font-mono uppercase tracking-[0.2em] text-muted-foreground">
                      {sec.heading}
                    </p>
                    {sec.items?.map((item, ii) => {
                      const isDone = log.some(
                        l => l.section_idx === si && l.item_idx === ii
                      );
                      const isCurrent =
                        currentItem?.section_idx === si && currentItem?.item_idx === ii;
                      return (
                        <div
                          key={ii}
                          className={`text-sm pl-3 border-l-2 py-0.5 transition-colors duration-200 ${
                            isCurrent
                              ? 'border-primary text-foreground font-medium'
                              : isDone
                              ? 'border-border text-muted-foreground line-through'
                              : 'border-border text-muted-foreground'
                          }`}
                        >
                          {item.text}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>

            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </section>
  );
}
