'use client';

import { useState, useRef, useEffect } from 'react';
import { MoreVertical } from 'lucide-react';
import PersonaDropdown from './PersonaDropdown';
import type { PersonaInfo } from '@/lib/store/pipelineStore';

interface PersonaMenuProps {
  personas: PersonaInfo[];
  selectedPersonaId: string;
  onSelect: (personaId: string) => void;
  disabled?: boolean;
}

export default function PersonaMenu({
  personas,
  selectedPersonaId,
  onSelect,
  disabled = false,
}: PersonaMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen]);

  const handleSelect = (personaId: string) => {
    onSelect(personaId);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          if (!disabled) {
            setIsOpen(!isOpen);
          }
        }}
        disabled={disabled}
        className={`
          p-1 rounded hover:bg-gray-100 transition-colors
          ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
        `}
        title="Select persona"
      >
        <MoreVertical className="w-4 h-4 text-gray-600" />
      </button>

      {isOpen && (
        <PersonaDropdown
          personas={personas}
          selectedPersonaId={selectedPersonaId}
          onSelect={handleSelect}
          disabled={disabled}
        />
      )}
    </div>
  );
}
