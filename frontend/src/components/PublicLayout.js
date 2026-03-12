import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'About Us', path: '/about' },
    { name: 'Events', path: '/events' },
    { name: 'Membership', path: '/membership' },
    { name: 'Contact', path: '/contact' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">A</span>
            </div>
            <span className="text-xl font-bold text-gray-800">ACTIV</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={`text-sm font-medium transition-colors duration-200 ${
                  isActive(link.path)
                    ? 'text-blue-600'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Desktop CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              to="/login"
              className="text-gray-600 hover:text-blue-600 font-medium text-sm transition-colors"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-medium text-sm transition-all duration-200 hover:shadow-lg"
            >
              Join Now
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="flex flex-col space-y-3">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  className={`px-3 py-2 rounded-lg font-medium ${
                    isActive(link.path)
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  {link.name}
                </Link>
              ))}
              <div className="flex flex-col space-y-2 pt-3 border-t">
                <Link
                  to="/login"
                  className="px-3 py-2 text-center text-gray-600 hover:bg-gray-50 rounded-lg font-medium"
                  onClick={() => setIsOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-3 py-2 text-center bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
                  onClick={() => setIsOpen(false)}
                >
                  Join Now
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">A</span>
              </div>
              <span className="text-2xl font-bold text-white">ACTIV</span>
            </div>
            <p className="text-gray-400 mb-4 max-w-md">
              A community-driven organization bringing together individuals passionate 
              about making a difference. Join us in our mission to create positive change.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors">
                <span className="sr-only">Facebook</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.77,7.46H14.5v-1.9c0-.9.6-1.1,1-1.1h3V.5h-4.33C10.24.5,9.5,3.44,9.5,5.32v2.15h-3v4h3v12h5v-12h3.85l.42-4Z"/>
                </svg>
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors">
                <span className="sr-only">Twitter</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.32,6.44a.5.5,0,0,0-.2-.87l-.79-.2A.5.5,0,0,1,22,4.67l.44-.89a.5.5,0,0,0-.58-.7l-2,.56a.5.5,0,0,1-.44-.08,5,5,0,0,0-2.92-1.7.5.5,0,0,0-.46.18,5.15,5.15,0,0,0-.67,3.3.5.5,0,0,1-.51.49l-2.56.3a.5.5,0,0,0-.26.88l.63.79a.51.51,0,0,1-.12.7,3.69,3.69,0,0,1-2.14.75,5.35,5.35,0,0,0-3.1-1,.5.5,0,0,0-.48.33,5.66,5.66,0,0,0,.45,4.52.5.5,0,0,1-.23.67l-2.38.67a.5.5,0,0,0-.28.89l2.71,1.13a.5.5,0,0,1,0,.88l-3.06,1a.5.5,0,0,0-.27.87l2.44,1.53a.5.5,0,0,1,0,.9l-2.44,1.54a.5.5,0,0,0-.28.86l3.84,2.41a.5.5,0,0,1,0,.88l-2.89,1.73a.5.5,0,0,0-.22.88l1.76,2.28a.5.5,0,0,1-.36.79,10.94,10.94,0,0,1-6.89.25.5.5,0,0,0-.58.56,7,7,0,0,0,.43,4.52.5.5,0,0,1-.53.62l-2.56-.67a.5.5,0,0,0-.59.57,8.37,8.37,0,0,0,2.72,3.63.5.5,0,0,1-.32.91l-2.17-.45a.5.5,0,0,0-.61.45,8.38,8.38,0,0,0,1.73,6.68.5.5,0,0,1-.14.67l-1.83-1.4a.5.5,0,0,0-.68.09A8.37,8.37,0,0,0,4.23,15.71a.5.5,0,0,1-.59.26l-1.94-.7a.5.5,0,0,0-.66.48,9.66,9.66,0,0,0,2.24,5.65.5.5,0,0,1-.45.71l-2.11.21a.5.5,0,0,0-.53.59A9.86,9.86,0,0,0,3.6,24,.5.5,0,0,0,4,24.5l2.24-.4a.5.5,0,0,1,.58.38,9.65,9.65,0,0,0,5.78,3.43.5.5,0,0,1,0,.94l-1.87-.39a.5.5,0,0,0-.53.59,9.93,9.93,0,0,0,6.63,5.83.5.5,0,0,1,0,.93l-2-.67a.5.5,0,0,0-.58.45,10.36,10.36,0,0,0,3.14,2.62.5.5,0,0,1,0,.93l-2.16-.72a.5.5,0,0,0-.59.53,10.06,10.06,0,0,0,2.39,6,.5.5,0,0,1-.45.71l-2.1-.43a.5.5,0,0,0-.57.58,9.61,9.61,0,0,0,2.53,4.62.5.5,0,0,1-.46.71H6.89a.51.51,0,0,0-.51.51,9.92,9.92,0,0,0,2.89,7.44.5.5,0,0,1-.47.72l-1.71-.57a.5.5,0,0,0-.53.59,10.58,10.58,0,0,0,3,6.23.5.5,0,0,1-.22.69l-1.5-1.63a.5.5,0,0,0-.68.12,10.46,10.46,0,0,0,1.08,4.42.5.5,0,0,1-.61.59l-.72-2a.5.5,0,0,0-.6.39,10.2,10.2,0,0,0,1.37,8,.5.5,0,0,1-.55.65l-1.74-.2a.5.5,0,0,0-.53.62,11.46,11.46,0,0,0,3.42,7.18.5.5,0,0,1-.37.88l-1.33-.88a.5.5,0,0,0-.66.19A11.39,11.39,0,0,0,4.63,20a.5.5,0,0,1-.48.86l-2,.07a.5.5,0,0,0-.48.64c.45,2.34,2.56,4.16,5.32,4.54a.5.5,0,0,0,.49-.47,10,10,0,0,0-1.22-6.17.5.5,0,0,1-.09-.64l.93-1.63a.5.5,0,0,0-.27-.67,9.58,9.58,0,0,1-4.26-3.52.5.5,0,0,0-.59-.25l-1.22.71a.5.5,0,0,1-.67-.19,9.36,9.36,0,0,0-3.53-2.9.5.5,0,0,1-.32-.69l.66-1.6a.5.5,0,0,0-.47-.61Z"/>
                </svg>
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors">
                <span className="sr-only">LinkedIn</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.5,2h-17A1.5,1.5,0,0,0,2,3.5v17A1.5,1.5,0,0,0,3.5,22h17a1.5,1.5,0,0,0,1.5-1.5v-17A1.5,1.5,0,0,0,20.5,2ZM8,19H5v-9h3ZM6.5,8.25A1.75,1.75,0,1,1,8.25,6.5,1.75,1.75,0,0,1,6.5,8.25ZM19,19H16v-4.5c0-1.38-1.12-2.5-2.5-2.5S11,13.12,11,14.5V19H8v-9h3v1.25a2.49,2.49,0,0,1,2.45-2.5c1.38,0,2.5,1.12,2.5,2.5V19Z"/>
                </svg>
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors">
                <span className="sr-only">Instagram</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,2.16c3.2,0,3.58,0,4.85.07,3.25.15,4.77,1.69,4.92,4.92.06,1.27.07,1.65.07,4.85s0,3.58-.07,4.85c-.15,3.23-1.66,4.77-4.92,4.92-1.27.06-1.65.07-4.85.07s-3.58,0-4.85-.07c-3.26-.15-4.77-1.7-4.92-4.92-.06-1.27-.07-1.65-.07-4.85s0-3.58.07-4.85C2.38,3.92,3.9,2.38,7.15,2.23,8.42,2.18,8.8,2.16,12,2.16ZM12,0C8.74,0,8.33,0,7.05.07c-4.35.2-6.78,2.62-7,7C0,8.33,0,8.74,0,12s0,3.67.07,4.95c.2,4.36,2.62,6.78,7,7C8.33,24,8.74,24,12,24s3.67,0,4.95-.07c4.35-.2,6.78-2.62,7-7C24,15.67,24,15.26,24,12s0-3.67-.07-4.95c-.2-4.35-2.62-6.78-7-7C15.67,0,15.26,0,12,0Zm0,5.84A6.16,6.16,0,1,0,18.16,12,6.16,6.16,0,0,0,12,5.84ZM12,16a4,4,0,1,1,4-4A4,4,0,0,1,12,16ZM18.41,4.15a1.44,1.44,0,1,0,1.44,1.44A1.44,1.44,0,0,0,18.41,4.15Z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li><Link to="/" className="hover:text-blue-400 transition-colors">Home</Link></li>
              <li><Link to="/about" className="hover:text-blue-400 transition-colors">About Us</Link></li>
              <li><Link to="/events" className="hover:text-blue-400 transition-colors">Events</Link></li>
              <li><Link to="/membership" className="hover:text-blue-400 transition-colors">Membership</Link></li>
              <li><Link to="/contact" className="hover:text-blue-400 transition-colors">Contact</Link></li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="text-white font-semibold mb-4">Contact Us</h4>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>123 Community Street,<br />New Delhi, India</span>
              </li>
              <li className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>contact@activ.org.in</span>
              </li>
              <li className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span>+91 98765 43210</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-500">
          <p>&copy; {currentYear} ACTIV. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

const PublicLayout = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-grow">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default PublicLayout;
