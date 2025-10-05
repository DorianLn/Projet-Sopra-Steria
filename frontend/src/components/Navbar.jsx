import React, { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { HiMenu, HiX, HiOutlineMoon, HiOutlineSun } from "react-icons/hi";
import logo2 from "../assets/logo2.png";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("darkMode") === "true"
  );

  // Applique la classe dark sur body
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <NavLink to="/" className="navbar-logo">
          <img src={logo2} alt="Sopra Steria" />
        </NavLink>

        {/* Menu Desktop */}
        <nav className="navbar-links">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/features"
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Fonctionnalités
          </NavLink>
          <NavLink
            to="/howitworks"
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Comment ça marche
          </NavLink>
        </nav>

        {/* Boutons Desktop */}
        <div className="hidden md:flex items-center gap-4 ">
          <button
            onClick={toggleDarkMode}
            className={`text-xl focus:outline-none ${
              darkMode ? "text-white" : "text-black"
            }`}
            aria-label="Toggle Dark Mode"
          >
            {darkMode ? <HiOutlineSun size={28} /> : <HiOutlineMoon size={28}  />}
          </button>

          <NavLink to="/start" className="navbar-btn">
            Commencer
          </NavLink>
        </div>

        {/* Menu Mobile Toggle */}
        <div className="md:hidden">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-gray-700 dark:text-gray-200 focus:outline-none"
          >
            {isOpen ? <HiX size={30} /> : <HiMenu size={30} />}
          </button>
        </div>
      </div>

      {/* Menu Mobile */}
      {isOpen && (
        <div className="navbar-mobile md:hidden">
          <NavLink
            to="/"
            onClick={() => setIsOpen(false)}
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/features"
            onClick={() => setIsOpen(false)}
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Fonctionnalités
          </NavLink>
          <NavLink
            to="/howitworks"
            onClick={() => setIsOpen(false)}
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Comment ça marche
          </NavLink>
          <NavLink
            to="/start"
            onClick={() => setIsOpen(false)}
            className="navbar-btn"
          >
            Commencer
          </NavLink>
          <button
            onClick={toggleDarkMode}
            className={`text-xl mt-2 self-start ${
              darkMode ? "text-white" : "text-black"
            }`}
            aria-label="Toggle Dark Mode"
          >
            {darkMode ? <HiOutlineSun /> : <HiOutlineMoon />}
          </button>
        </div>
      )}
    </header>
  );
};

export default Navbar;
