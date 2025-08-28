import GermanySvg from '../assets/germany.svg';
import { motion } from 'framer-motion'
import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="grid grid-cols-3 grid-rows-2 gap-4 p-8 w-full">
      {/* Grid Cell 1: Top-Left Corner */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        className="cursor-pointer flex items-center justify-center p-4 border-none bg-transparent"
        onClick={() => console.log("Clicked!")}
      >
        <img
          src={GermanySvg}
          alt="Border of Germany"
          className="w-full h-auto"
        />
      </motion.button>
      
      {/* The remaining cells will be empty by default, but the grid structure is maintained. */}
      {/* Add more motion.button components here to fill the grid */}
      <div className="empty-cell"></div>
      <div className="empty-cell"></div>
      <div className="empty-cell"></div>
      <div className="empty-cell"></div>
      <div className="empty-cell"></div>
    </div>
  );
};

export default Home;