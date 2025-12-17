// src/features/signin/components/ContentTextDisplay.tsx

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SlideContent {
  title: string;
  description: string;
}

interface ContentTextDisplayProps {
  content: SlideContent;
  direction: number;
}

// Animation variants for the text content to slide in and out
const textVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? '100%' : '-100%',
    opacity: 0,
  }),
  center: { 
    x: 0, 
    opacity: 1 
  },
  exit: (direction: number) => ({
    x: direction < 0 ? '100%' : '-100%',
    opacity: 0,
  }),
};

const ContentTextDisplay: React.FC<ContentTextDisplayProps> = ({ content, direction }) => {
  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
        <AnimatePresence mode="wait" custom={direction}>
            <motion.div
                key={content.title} // Use a unique key like title to trigger animation
                custom={direction}
                variants={textVariants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{ duration: 0.8, ease: [0.43, 0.13, 0.23, 0.96] }}
                className="text-center p-4 absolute" // Use absolute positioning within the container
            >
                <h1 className="text-2xl lg:text-3xl font-bold mb-2">
                {content.title}
                </h1>
                <p className="text-base opacity-80 max-w-xl mx-auto">
                {content.description}
                </p>
            </motion.div>
        </AnimatePresence>
    </div>
  );
};

export default ContentTextDisplay;