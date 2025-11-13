'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  FolderOpen,
  User,
  LogOut,
  Menu,
  X,
  Search,
  HelpCircle,
  BarChart3,
  Sparkles,
  Plus,
} from 'lucide-react';
import { NotificationCenter, Button, Badge } from './';
import { clearApiKey } from '@/lib/auth';

/**
 * Navigation Component for ConsultantOS
 *
 * Provides responsive header with navigation links, user menu, and notifications
 */

interface NavigationProps {
  className?: string;
}

interface NavLink {
  href: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

export const Navigation: React.FC<NavigationProps> = ({ className = '' }) => {
  const pathname = usePathname();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);

  // Load user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (e) {
        console.error('Failed to parse user data');
      }
    }
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  // Navigation links
  const navLinks: NavLink[] = [
    { href: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { href: '/mvp-demo', label: 'MVP Demo', icon: <Sparkles size={20} /> },
    { href: '/analysis', label: 'Create Analysis', icon: <FileText size={20} /> },
    { href: '/reports', label: 'Reports', icon: <FolderOpen size={20} /> },
    { href: '/jobs', label: 'Jobs', icon: <Briefcase size={20} /> },
    { href: '/templates', label: 'Templates', icon: <FolderOpen size={20} /> },
    { href: '/analytics', label: 'Analytics', icon: <BarChart3 size={20} /> },
  ];

  // User menu items
  const userMenuItems = [
    { href: '/profile', label: 'Profile & Settings', icon: <User size={16} /> },
    { href: '/help', label: 'Help & Support', icon: <HelpCircle size={16} /> },
  ];

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  const handleLogout = () => {
    // Clear API key from memory (not localStorage - it's not stored there)
    clearApiKey();
    localStorage.removeItem('user');
    router.push('/login');
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user?.name) return 'U';
    const names = user.name.split(' ');
    return names.map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <nav className={`bg-white border-b border-gray-200 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left side - Logo and nav links */}
          <div className="flex">
            {/* Logo */}
            <Link href="/" className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">CO</span>
                </div>
                <span className="text-xl font-bold text-gray-900 hidden sm:block">
                  ConsultantOS
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:ml-8 md:flex md:space-x-1" aria-label="Main navigation">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href as any}
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive(link.href)
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                  aria-current={isActive(link.href) ? 'page' : undefined}
                >
                  <span className="mr-2" aria-hidden="true">{link.icon}</span>
                  {link.label}
                  {link.badge !== undefined && link.badge > 0 && (
                    <Badge variant="primary" className="ml-2" aria-label={`${link.badge} notifications`}>
                      {link.badge}
                    </Badge>
                  )}
                </Link>
              ))}
            </nav>
          </div>

          {/* Right side - New Analysis button, Notifications and user menu */}
          <div className="flex items-center space-x-4">
            {/* + New Analysis button (desktop only) */}
            <Button
              onClick={() => router.push('/analysis')}
              className="hidden md:flex items-center bg-blue-600 text-white hover:bg-blue-700"
              aria-label="Create new analysis"
            >
              <Plus size={16} className="mr-1.5" aria-hidden="true" />
              New Analysis
            </Button>
            {/* Search (desktop only) */}
            <button
              onClick={() => router.push('/reports')}
              className="hidden lg:flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
              aria-label="Search reports"
              title="Search reports"
            >
              <Search size={20} />
            </button>

            {/* Notifications */}
            {user && (
              <NotificationCenter
                userId={user.email}
              />
            )}

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-3 hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors"
                aria-label="User menu"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {getUserInitials()}
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || 'Guest'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.email || 'Not logged in'}
                  </p>
                </div>
              </button>

              {/* User Dropdown */}
              {isUserMenuOpen && (
                <>
                  {/* Backdrop */}
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setIsUserMenuOpen(false)}
                  />

                  {/* Dropdown Menu */}
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 z-20">
                    <div className="p-3 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {user?.name || 'Guest'}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {user?.email || 'Not logged in'}
                      </p>
                    </div>

                    <div className="py-1">
                      {userMenuItems.map((item) => (
                        <Link
                          key={item.href}
                          href={item.href as any}
                          onClick={() => setIsUserMenuOpen(false)}
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <span className="mr-3 text-gray-400">{item.icon}</span>
                          {item.label}
                        </Link>
                      ))}
                    </div>

                    <div className="border-t border-gray-100 py-1">
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <LogOut size={16} className="mr-3" />
                        Sign out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-50"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200" role="navigation" aria-label="Mobile navigation">
          <nav className="px-2 pt-2 pb-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href as any}
                className={`flex items-center px-3 py-2 text-base font-medium rounded-md ${
                  isActive(link.href)
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                }`}
                aria-current={isActive(link.href) ? 'page' : undefined}
              >
                <span className="mr-3" aria-hidden="true">{link.icon}</span>
                {link.label}
                {link.badge !== undefined && link.badge > 0 && (
                  <Badge variant="primary" className="ml-auto" aria-label={`${link.badge} notifications`}>
                    {link.badge}
                  </Badge>
                )}
              </Link>
            ))}
          </nav>

          {/* Mobile user section */}
          <div className="border-t border-gray-200 pt-4 pb-3">
            <div className="px-4 flex items-center space-x-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                {getUserInitials()}
              </div>
              <div>
                <p className="text-base font-medium text-gray-900">
                  {user?.name || 'Guest'}
                </p>
                <p className="text-sm text-gray-500">
                  {user?.email || 'Not logged in'}
                </p>
              </div>
            </div>

            <div className="space-y-1 px-2">
              {userMenuItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href as any}
                  className="flex items-center px-3 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                >
                  <span className="mr-3 text-gray-400">{item.icon}</span>
                  {item.label}
                </Link>
              ))}

              <button
                onClick={handleLogout}
                className="flex items-center w-full px-3 py-2 text-base font-medium text-red-600 hover:bg-red-50 rounded-md"
              >
                <LogOut size={20} className="mr-3" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;
