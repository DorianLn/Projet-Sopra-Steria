import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { HiMenu, HiX, HiOutlineMoon, HiOutlineSun } from "react-icons/hi";
import logo2 from "../assets/logos/logo2.png";
import { useDarkMode } from "../hooks/useDarkMode";
import { NAV_LINKS, ROUTES } from "../utils/constants";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { darkMode, toggleDarkMode } = useDarkMode();

  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <NavLink to="/" className="navbar-logo">
          <img src={logo2} alt="Sopra Steria" />
        </NavLink>

        {/* Menu Desktop */}
        <nav className="navbar-links">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                isActive ? "navbar-link navbar-link-active" : "navbar-link"
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        {/* Boutons Desktop */}
        <div className="navbar-actions">
          <button
            onClick={toggleDarkMode}
            className={`text-xl focus:outline-none ${
              darkMode ? "text-white" : "text-black"
            }`}
            aria-label="Toggle Dark Mode"
          >
            {darkMode ? <HiOutlineSun size={28} /> : <HiOutlineMoon size={28}  />}
          </button>

          <NavLink to={ROUTES.START} className="navbar-btn">
            Commencer
          </NavLink>
        </div>

        {/* Menu Mobile Toggle */}
        <div className="navbar-toggle">
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
            to="/example"
            onClick={() => setIsOpen(false)}
            className={({ isActive }) =>
              isActive ? "navbar-link navbar-link-active" : "navbar-link"
            }
          >
            Voir un exemple
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
