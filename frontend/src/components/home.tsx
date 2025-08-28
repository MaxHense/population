import GermanySvg from '../assets/germany.svg';
import { motion } from 'framer-motion'
import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-transparent">
      <motion.button
        whileHover={{ scale: 1.1 }}
        className="cursor-pointer"
        onClick={() => console.log("Clicked!")} // Add here the jump to the Map
      >
        <img
          src={GermanySvg}
          alt="Border of Germany"
          className="h-screen bg-cover bg-center bg-no-repeat"
        />
      </motion.button>
    </div>
  );
};

export default Home;