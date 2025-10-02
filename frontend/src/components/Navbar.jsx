import React, { useState } from "react";
import { Link } from "react-router-dom";
import { HiMenu, HiX } from "react-icons/hi";
import logo from "../assets/sopra-steria-logo.svg";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-md fixed w-full z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-24">
          
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/">
              <img src={logo} alt="Logo" className="h-24 w-auto" /> 
            </Link>
          </div>

          {/* Menu desktop */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="font-bold text-gray-700 dark:text-gray-200 hover:text-[#FF5614]">
              Home
            </Link>
            <Link to="/features" className="font-bold text-gray-700 dark:text-gray-200 hover:text-[#FF5614]">
              Fonctionnalités
            </Link>
            <Link to="/howitworks" className="font-bold text-gray-700 dark:text-gray-200 hover:text-[#FF5614]">
              Comment ça marche
            </Link>
          </div>

          {/* Bouton desktop */}
          <div className="hidden md:flex">
            <Link
              to="/start"
              className="bg-[#FF5614] text-white px-4 py-2 rounded-lg shadow hover:bg-[#FF671D] transition font-semibold"
            >
              Commencer
            </Link>
          </div>

          {/* Menu mobile */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-700 dark:text-gray-200 focus:outline-none"
            >
              {isOpen ? <HiX size={24} /> : <HiMenu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Dropdown mobile */}
      {isOpen && (
        <div className="md:hidden bg-white dark:bg-gray-900 px-4 pb-4 space-y-2">
          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="block font-bold text-gray-700 dark:text-gray-200 hover:text-[#FF5614]"
          >
            Home
          </Link>
          <Link
            to="/features"
            onClick={() => setIsOpen(false)}
            className="block font-bold text-gray-700 dark:text-gray-200 hover:text-[#FF5614]"
          >
            Fonctionnalités
          </Link>
          <Link
            to="/howitworks"
            onClick={() => setIsOpen(false)}
            className="block font-bold text-gray-700 dark:text-gray-200 hover:text-[#FF5614]"
          >
            Comment ça marche
          </Link>
          <Link
            to="/start"
            onClick={() => setIsOpen(false)}
            className="block bg-[#5044E5] text-white px-4 py-2 rounded-lg shadow hover:bg-[#4036c9] transition text-center font-semibold"
          >
            Commencer
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
