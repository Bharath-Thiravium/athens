// src/features/signin/components/ImageDisplayCarousel.tsx

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SlideImage {
  image: string;
  title: string; // Used for alt text
}

interface ImageDisplayCarouselProps {
  slides: SlideImage[];
  interval?: number;
}

// Animation variants for a smooth cross-fade effect
const imageVariants = {
  enter: { opacity: 0 },
  center: { zIndex: 1, opacity: 1 },
  exit: { zIndex: 0, opacity: 0 },
};

const ImageDisplayCarousel: React.FC<ImageDisplayCarouselProps> = ({ slides, interval = 5000 }) => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      // Loop to the next slide
      setCurrent((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
    }, interval);
    return () => clearTimeout(timer);
  }, [current, interval, slides.length]);


  return (
    // The container fills the entire right panel
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
      <AnimatePresence initial={false}>
        <motion.img
          key={current}
          src={slides[current]?.image}
          alt={slides[current]?.title}
          className="absolute inset-0 w-full h-full object-cover"
          variants={imageVariants}
          initial="enter"
          animate="center"
          exit="exit"
          // A longer, softer transition suits the fade effect
          transition={{ duration: 2.5, ease: "easeInOut" }}
        />
      </AnimatePresence>
    </div>
  );
};

export default ImageDisplayCarousel;