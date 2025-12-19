
import React, { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import { Occasion, CardState, ImageFilters, Language } from './types';
import { OCCASION_CONFIGS, getSeasonalPrompt, MONTH_NAMES, TRANSLATIONS } from './constants';
import * as gemini from './services/gemini';
import * as htmlToImage from 'html-to-image';

const STORAGE_KEY = 'cardia_ia_v4_progress';

const VOICES = [
  { id: 'Zephyr', name: 'Zephyr (Juvenil)' },
  { id: 'Puck', name: 'Puck (Entusiasta)' },
  { id: 'Charon', name: 'Charon (Profundo)' },
  { id: 'Kore', name: 'Kore (Suave)' },
  { id: 'Fenrir', name: 'Fenrir (Serio)' },
];

const DEFAULT_FILTERS: ImageFilters = {
  brightness: 100,
  contrast: 100,
  saturation: 100,
  sepia: 0,
  blur: 0,
};

// Inline SVG components
const IconQuoteLeft = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M14.017 21L14.017 18C14.017 16.8954 14.9124 16 16.017 16H19.017C20.1216 16 21.017 15.1046 21.017 14V11C21.017 9.89543 20.1216 9 19.017 9H16.017C14.9124 9 14.017 8.10457 14.017 7V4H17.017C19.2261 4 21.017 5.79086 21.017 8V14C21.017 16.2091 19.2261 18 17.017 18H16.017L16.017 21H14.017ZM3 21L3 18C3 16.8954 3.89543 16 5 16H8C9.10457 16 10 15.1046 10 14V11C10 9.89543 9.10457 9 8 9H5C3.89543 9 3 8.10457 3 7V4H6C8.20914 4 10 5.79086 10 8V14C10 16.2091 8.20914 18 6 18H5L5 21H3Z" />
  </svg>
);

const IconQuoteRight = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M9.983 3L9.983 6C9.983 7.10457 9.08757 8 7.983 8H4.983C3.87843 8 2.983 8.89543 2.983 10V13C2.983 14.1046 3.87843 15 4.983 15H7.983C9.08757 15 9.983 15.8954 9.983 17V20H6.983C4.77386 20 2.983 18.2091 2.983 16V10C2.983 7.79086 4.77386 6 6.983 6H7.983L7.983 3H9.983ZM21 3L21 6C21 7.10457 20.1046 8 19 8H16C14.8954 8 14 8.89543 14 10V13C14 14.1046 14.8954 15 16 15H19C20.1046 15 21 15.8954 21 17V20H18C15.7909 20 14 18.2091 14 16V10C14 7.79086 15.7909 6 18 6H19L19 3H21Z" />
  </svg>
);

const IconPlay = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 5V19L19 12L8 5Z" />
  </svg>
);

const IconPause = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 19H10V5H6V19ZM14 5V19H18V5H14Z" />
  </svg>
);

const IconPointer = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 11.24V7.5C9 6.12 10.12 5 11.5 5C12.88 5 14 6.12 14 7.5V11.24C15.13 10.7 16 9.57 16 8.25V7.5C16 5.01 13.99 3 11.5 3C9.01 3 7 5.01 7 7.5V8.25C7 9.57 7.87 10.7 9 11.24ZM18.84 15.87L14.3 13.61C13.84 13.38 13.31 13.38 12.86 13.61L9.66 15.21V10.75C9.66 10.06 9.1 9.5 8.41 9.5C7.72 9.5 7.16 10.06 7.16 10.75V20.75C7.16 21.44 7.72 22 8.41 22C8.61 22 8.79 21.96 8.96 21.88L18.42 17.15C19.14 16.79 19.34 15.91 18.84 15.87Z" />
  </svg>
);

const App: React.FC = () => {
  const [state, setState] = useState<CardState>({
    occasion: Occasion.Birthday,
    language: Language.Spanish,
    sender: "Alex",
    recipient: "Sam",
    message: "Te deseo lo mejor en este día tan especial.",
    isGenerating: false,
    isEditing: false,
    filters: { ...DEFAULT_FILTERS }
  });

  const [selectedVoice, setSelectedVoice] = useState('Puck');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isVideoGenerating, setIsVideoGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  
  const audioContextRef = useRef<AudioContext | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cardFrontRef = useRef<HTMLDivElement>(null);
  const cardBackRef = useRef<HTMLDivElement>(null);
  const activeSourceRef = useRef<AudioBufferSourceNode | null>(null);

  const t = TRANSLATIONS[state.language];

  // Load state from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        setState(prev => ({
          ...prev,
          ...parsed,
          isGenerating: false,
          isEditing: false,
          filters: parsed.filters || { ...DEFAULT_FILTERS }
        }));
      } catch (e) {
        console.error("Error loading saved progress", e);
      }
    }
  }, []);

  // Save state to localStorage
  useEffect(() => {
    const { isGenerating, isEditing, ...persistentState } = state;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(persistentState));
      setIsSaved(true);
      const timer = setTimeout(() => setIsSaved(false), 2000);
      return () => clearTimeout(timer);
    } catch (e) {
      console.warn("Could not save to localStorage", e);
    }
  }, [state]);

  // Date Context
  const today = useMemo(() => new Date(), []);
  const currentMonthName = MONTH_NAMES[today.getMonth()];
  const currentDay = today.getDate();
  const seasonalPrompt = useMemo(() => getSeasonalPrompt(today.getMonth()), [today]);

  const handleReset = () => {
    if (window.confirm("¿Estás seguro de que quieres borrar el progreso?")) {
      localStorage.removeItem(STORAGE_KEY);
      (window as any).__lastAudio = null;
      setState({
        occasion: Occasion.Birthday,
        language: Language.Spanish,
        sender: "Alex",
        recipient: "Sam",
        message: "Te deseo lo mejor en este día tan especial.",
        isGenerating: false,
        isEditing: false,
        filters: { ...DEFAULT_FILTERS }
      });
      setVideoUrl(null);
      setIsFlipped(false);
    }
  };

  const handleGenerate = async () => {
    setState(prev => ({ ...prev, isGenerating: true }));
    setVideoUrl(null);
    try {
      const config = OCCASION_CONFIGS[state.occasion];
      const improvedMsg = await gemini.improveMessage(state.message, config.tone, t.promptImprove);
      const finalImagePrompt = `${state.occasion}, ${config.basePrompt}, ${seasonalPrompt}, context of ${currentDay} ${currentMonthName}`;
      const imageUrl = await gemini.generateCardImage(finalImagePrompt, t.promptImage);
      
      const ttsScript = state.language === Language.Spanish 
        ? `Hola ${state.recipient}. ${improvedMsg}. De parte de ${state.sender}.`
        : `Hi ${state.recipient}. ${improvedMsg}. From ${state.sender}.`;
      
      const ttsData = await gemini.generateTTS(ttsScript, selectedVoice);

      setState(prev => ({
        ...prev,
        message: improvedMsg,
        imageUrl,
        isGenerating: false,
        seasonalContext: seasonalPrompt
      }));

      (window as any).__lastAudio = ttsData;
      setIsFlipped(false);
    } catch (error) {
      console.error("Generation failed", error);
      alert("Error generating card.");
      setState(prev => ({ ...prev, isGenerating: false }));
    }
  };

  const handleDownloadImage = async () => {
    if (!cardFrontRef.current || !cardBackRef.current) return;
    const exportConfig = { pixelRatio: 2, cacheBust: true };
    try {
      const dataUrlFront = await htmlToImage.toPng(cardFrontRef.current, exportConfig);
      const dataUrlBack = await htmlToImage.toPng(cardBackRef.current, exportConfig);
      
      const linkFront = document.createElement('a');
      linkFront.download = `front-cardia-${state.recipient.toLowerCase()}.png`;
      linkFront.href = dataUrlFront;
      linkFront.click();

      const linkBack = document.createElement('a');
      linkBack.download = `message-cardia-${state.recipient.toLowerCase()}.png`;
      linkBack.href = dataUrlBack;
      linkBack.click();
    } catch (err) {
      console.error('Error exporting image', err);
    }
  };

  const handleDownloadAudio = () => {
    const ttsData = (window as any).__lastAudio;
    if (!ttsData) return;
    const wavBlob = gemini.pcmToWav(ttsData, 24000);
    const url = URL.createObjectURL(wavBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `voice-cardia-${state.recipient.toLowerCase()}.wav`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleGenerateVideo = async () => {
    if (!(window as any).aistudio || !(await (window as any).aistudio.hasSelectedApiKey())) {
      await (window as any).aistudio.openSelectKey();
    }
    setIsVideoGenerating(true);
    try {
      const config = OCCASION_CONFIGS[state.occasion];
      const videoPrompt = `${state.occasion}, ${config.basePrompt}, ${seasonalPrompt}. Cinematic lighting, emotional.`;
      const url = await gemini.generateVideo(videoPrompt, t.promptVideo);
      setVideoUrl(url);
    } catch (err) {
      console.error('Error generating video', err);
    } finally {
      setIsVideoGenerating(false);
    }
  };

  const playAudio = async (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const ttsData = (window as any).__lastAudio;
    if (!ttsData) return;

    if (isPlaying && activeSourceRef.current) {
      activeSourceRef.current.stop();
      setIsPlaying(false);
      return;
    }

    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
    }
    const ctx = audioContextRef.current;
    if (ctx.state === 'suspended') await ctx.resume();

    const buffer = await gemini.decodeAudioData(ttsData, ctx);
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);
    source.onended = () => {
      setIsPlaying(false);
      activeSourceRef.current = null;
    };
    activeSourceRef.current = source;
    source.start();
    setIsPlaying(true);
  };

  const handleFilterChange = (key: keyof ImageFilters, value: number) => {
    setState(prev => ({ ...prev, filters: { ...prev.filters, [key]: value } }));
  };

  const applyPreset = (preset: Partial<ImageFilters>) => {
    setState(prev => ({ ...prev, filters: { ...DEFAULT_FILTERS, ...preset } }));
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setState(prev => ({ ...prev, imageUrl: reader.result as string }));
      reader.readAsDataURL(file);
    }
  };

  const handleWhatsAppShare = () => {
    const linkTarjeta = window.location.href;
    const text = state.language === Language.Spanish 
      ? `Hola ${state.recipient}, te hice esta tarjeta mágica con audio: ${linkTarjeta}`
      : `Hi ${state.recipient}, I made this magic card for you: ${linkTarjeta}`;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
  };

  const currentConfig = OCCASION_CONFIGS[state.occasion];
  const filterStyle = {
    filter: `brightness(${state.filters.brightness}%) contrast(${state.filters.contrast}%) saturate(${state.filters.saturation}%) sepia(${state.filters.sepia}%) blur(${state.filters.blur}px)`
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 md:py-12">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold text-rose-600 flex items-center justify-center gap-3">
          <i className="fa-solid fa-heart animate-pulse text-rose-500"></i>
          {t.title}
        </h1>
        <p className="text-gray-600 mt-2 text-lg italic">{t.subtitle}</p>
        <div className="mt-4 flex flex-wrap justify-center items-center gap-3">
          <div className="inline-flex items-center gap-2 bg-white/60 backdrop-blur px-4 py-2 rounded-full border border-rose-100 shadow-sm text-sm text-gray-500">
             <i className="fa-solid fa-calendar-check text-rose-400"></i>
             {state.language === Language.Spanish ? `Hoy es ${currentDay} de ${currentMonthName}` : `Today is ${currentMonthName} ${currentDay}`}
          </div>
          <div className="inline-flex rounded-full overflow-hidden border border-rose-200 shadow-sm">
             <button 
                onClick={() => setState(prev => ({...prev, language: Language.Spanish}))}
                className={`px-3 py-1.5 text-[10px] font-black tracking-widest uppercase transition-all ${state.language === Language.Spanish ? 'bg-rose-500 text-white' : 'bg-white text-rose-400 hover:bg-rose-50'}`}
             >ESP</button>
             <button 
                onClick={() => setState(prev => ({...prev, language: Language.English}))}
                className={`px-3 py-1.5 text-[10px] font-black tracking-widest uppercase transition-all ${state.language === Language.English ? 'bg-rose-500 text-white' : 'bg-white text-rose-400 hover:bg-rose-50'}`}
             >ENG</button>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-xl border border-rose-100">
            <h2 className="text-xl font-bold flex items-center gap-2 mb-6 text-gray-800">
              <i className="fa-solid fa-wand-magic-sparkles text-rose-500"></i>
              {t.title}
            </h2>
            
            <div className="space-y-5">
              <div className="bg-rose-50/50 p-4 rounded-2xl border border-rose-100">
                <label className="block text-[10px] font-black text-rose-400 uppercase tracking-widest mb-2">{t.occasion}</label>
                <select 
                  className="w-full p-3 rounded-xl border-none focus:ring-2 focus:ring-rose-500 outline-none bg-white shadow-sm font-semibold"
                  value={state.occasion}
                  onChange={(e) => setState(prev => ({ ...prev, occasion: e.target.value as Occasion }))}
                >
                  {Object.values(Occasion).map(o => <option key={o} value={o}>{o}</option>)}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded-2xl border border-gray-100">
                  <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">{t.from}</label>
                  <input type="text" className="w-full bg-transparent border-none focus:ring-0 text-sm font-bold" value={state.sender} onChange={(e) => setState(prev => ({ ...prev, sender: e.target.value }))} />
                </div>
                <div className="bg-gray-50 p-3 rounded-2xl border border-gray-100">
                  <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">{t.to}</label>
                  <input type="text" className="w-full bg-transparent border-none focus:ring-0 text-sm font-bold" value={state.recipient} onChange={(e) => setState(prev => ({ ...prev, recipient: e.target.value }))} />
                </div>
              </div>

              <div className="bg-indigo-50/50 p-4 rounded-2xl border border-indigo-100">
                <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">{t.voice}</label>
                <div className="flex flex-wrap gap-2">
                   {VOICES.map(v => (
                     <button key={v.id} onClick={() => setSelectedVoice(v.id)}
                       className={`flex-1 min-w-[80px] text-[10px] font-black py-2 px-1 rounded-lg border transition-all ${selectedVoice === v.id ? 'bg-indigo-500 text-white border-indigo-600 shadow-md scale-105' : 'bg-white text-indigo-500 border-indigo-100 hover:bg-indigo-50'}`}
                     >{v.name.split(' ')[0]}</button>
                   ))}
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">{t.message}</label>
                <textarea className="w-full bg-transparent border-none focus:ring-0 text-sm font-medium h-24 resize-none italic" value={state.message} onChange={(e) => setState(prev => ({ ...prev, message: e.target.value }))} />
              </div>

              <div className="bg-white p-4 rounded-2xl border-2 border-dashed border-gray-100">
                <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                  <i className="fa-solid fa-sliders"></i> {t.photoLab}
                </h3>
                <div className="space-y-4">
                  <div className="flex gap-2 mb-2 overflow-x-auto pb-2 scrollbar-hide">
                    <button onClick={() => applyPreset({ brightness: 120, saturation: 140 })} className="px-3 py-1.5 bg-rose-50 text-rose-500 rounded-full text-[9px] font-black whitespace-nowrap uppercase">Vibrant</button>
                    <button onClick={() => applyPreset({ sepia: 60, contrast: 110 })} className="px-3 py-1.5 bg-amber-50 text-amber-500 rounded-full text-[9px] font-black whitespace-nowrap uppercase">Vintage</button>
                    <button onClick={() => applyPreset(DEFAULT_FILTERS)} className="px-3 py-1.5 bg-blue-50 text-blue-500 rounded-full text-[9px] font-black whitespace-nowrap uppercase">Reset</button>
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleImageUpload} />
                <button onClick={() => fileInputRef.current?.click()} className="w-full py-3 mb-3 border-2 border-dashed border-gray-100 rounded-2xl text-gray-400 hover:border-rose-300 hover:text-rose-500 transition-all flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-widest">
                  <i className="fa-solid fa-upload"></i> {t.upload}
                </button>
                <button onClick={handleGenerate} disabled={state.isGenerating}
                  className="w-full py-4 bg-gradient-to-r from-rose-500 to-indigo-600 text-white rounded-2xl font-black shadow-xl hover:shadow-rose-200 hover:-translate-y-1 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {state.isGenerating ? <i className="fa-solid fa-spinner animate-spin"></i> : <i className="fa-solid fa-sparkles"></i>}
                  {t.generate}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-8 flex flex-col items-center">
          {state.imageUrl ? (
            <div className="w-full max-w-md animate-in fade-in zoom-in-95 duration-700">
              <div className={`card-container-3d ${isFlipped ? 'flipped' : ''}`} onClick={() => setIsFlipped(!isFlipped)}>
                <div className="card-body-3d">
                  <div ref={cardFrontRef} className="card-face card-front relative shadow-2xl overflow-hidden bg-white border-4 border-white">
                    <img src={state.imageUrl} crossOrigin="anonymous" alt="Portada" className="w-full h-full object-cover transition-all duration-500" style={filterStyle} />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-10">
                       <p className="text-white text-[10px] font-black tracking-[0.3em] uppercase mb-2 opacity-60">{t.cardCoverMsg}</p>
                       <h2 className="text-white text-4xl font-bold drop-shadow-2xl">{state.recipient}</h2>
                    </div>
                    <div className="absolute top-6 right-6">
                       <div className="bg-white/20 backdrop-blur-md rounded-full w-12 h-12 flex items-center justify-center text-white border border-white/30 shadow-xl"><IconPointer /></div>
                    </div>
                  </div>

                  <div ref={cardBackRef} className="card-face card-back border-t-8 border-b-8" style={{ borderColor: currentConfig.color }}>
                    <div className="flex justify-between items-start mb-6">
                      <span className="text-6xl drop-shadow-lg">{currentConfig.emoji}</span>
                      <button onClick={playAudio} className={`w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all ${isPlaying ? 'bg-rose-500 text-white animate-pulse' : 'bg-white text-rose-500 hover:scale-110 active:scale-90'}`}>
                        {isPlaying ? <IconPause /> : <IconPlay />}
                      </button>
                    </div>

                    <div className="flex-1 flex flex-col justify-center items-center text-center">
                      <h3 className="text-2xl font-bold text-gray-800 mb-6 font-cursive">{t.cardInsideDear} {state.recipient},</h3>
                      <div className="relative group/text">
                        <div className="absolute -top-8 -left-8 text-rose-100 opacity-50"><IconQuoteLeft /></div>
                        <p className="text-2xl font-cursive italic text-gray-700 leading-relaxed px-4 relative z-10">{state.message}</p>
                        <div className="absolute -bottom-8 -right-8 text-rose-100 opacity-50"><IconQuoteRight /></div>
                      </div>
                      <div className="mt-12 text-center">
                        <div className="w-16 h-1 bg-gradient-to-r from-rose-200 to-indigo-200 mx-auto mb-4 rounded-full"></div>
                        <p className="text-2xl font-bold text-gray-900 tracking-tight">— {state.sender}</p>
                        <p className="text-[10px] text-gray-400 mt-2 font-sans font-black tracking-[0.4em] uppercase">{currentDay} {currentMonthName} 2025</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-12 w-full grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-6 rounded-[2.5rem] shadow-xl border border-rose-100">
                  <h4 className="font-black text-[10px] tracking-widest text-rose-400 mb-4 flex items-center gap-2 uppercase">
                    <i className="fa-solid fa-share-nodes"></i> {t.share}
                  </h4>
                  <button onClick={handleWhatsAppShare} className="w-full py-4 bg-[#25D366] text-white rounded-2xl font-bold hover:brightness-110 shadow-lg shadow-green-100 flex items-center justify-center gap-3 transition-all active:scale-95">
                    <i className="fa-brands fa-whatsapp text-2xl"></i> {t.whatsapp}
                  </button>
                </div>

                <div className="bg-white p-6 rounded-[2.5rem] shadow-xl border border-indigo-100">
                  <h4 className="font-black text-[10px] tracking-widest text-indigo-400 mb-4 flex items-center gap-2 uppercase">
                    <i className="fa-solid fa-cloud-arrow-down"></i> {t.downloads}
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                     <button onClick={handleDownloadImage} className="py-3 bg-indigo-600 text-white rounded-xl font-bold hover:brightness-110 shadow-md text-xs">{t.btnPng}</button>
                     <button onClick={handleDownloadAudio} className="py-3 bg-rose-500 text-white rounded-xl font-bold hover:brightness-110 shadow-md text-xs">{t.btnAudio}</button>
                     <button onClick={handleGenerateVideo} disabled={isVideoGenerating} className="col-span-2 py-3 bg-gray-900 text-white rounded-xl font-bold hover:brightness-110 shadow-md text-xs flex items-center justify-center gap-2">
                       {isVideoGenerating ? <i className="fa-solid fa-circle-notch animate-spin"></i> : t.btnVideo}
                     </button>
                  </div>
                </div>
              </div>

              {videoUrl && (
                <div className="w-full bg-white p-8 rounded-[3rem] shadow-2xl border-4 border-rose-50 mt-8 animate-in slide-in-from-bottom-12 duration-1000">
                  <video src={videoUrl} controls className="w-full rounded-[2rem] shadow-inner mb-6 aspect-[9/16] object-cover bg-black" />
                  <a href={videoUrl} download="regalo-cardia.mp4" className="block w-full text-center py-5 bg-black text-white rounded-2xl font-black shadow-xl hover:scale-[1.02] transition-all">
                    <i className="fa-solid fa-download mr-2"></i> {t.btnVideoDone}
                  </a>
                </div>
              )}
            </div>
          ) : (
            <div className="w-full max-w-md h-[600px] flex flex-col items-center justify-center text-center p-14 bg-white/40 rounded-[3rem] border-4 border-dashed border-rose-200 group hover:bg-white/60 transition-all duration-700">
              <div className="w-32 h-32 bg-rose-100 rounded-full flex items-center justify-center mb-8"><i className="fa-solid fa-heart text-5xl text-rose-300"></i></div>
              <h3 className="text-3xl font-black text-rose-400 mb-4">{t.title}</h3>
              <p className="text-gray-500 text-lg leading-relaxed">{t.subtitle}</p>
            </div>
          )}
        </div>
      </div>

      <footer className="mt-24 pb-16 text-center text-gray-300 text-[10px] font-black uppercase tracking-[0.4em]">
        <p>{t.footerText}</p>
      </footer>
    </div>
  );
};

export default App;
