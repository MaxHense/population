import GermanySvg from '../assets/germany.svg';
import { motion } from 'framer-motion'
import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <motion.img
        src={GermanySvg}
        alt="SVG Image"
        className="w-64 h-64 cursor-pointer"
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
      />
    </div>
  );
};

export default Home;