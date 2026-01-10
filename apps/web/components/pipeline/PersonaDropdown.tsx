'use client';

import { Check } from 'lucide-react';
import type { PersonaInfo } from '@/lib/store/pipelineStore';

interface PersonaDropdownProps {
  personas: PersonaInfo[];
  selectedPersonaId: string;
  onSelect: (personaId: string) => void;
  disabled?: boolean;
}

export default function PersonaDropdown({
  personas,
  selectedPersonaId,
  onSelect,
  disabled = false,
}: PersonaDropdownProps) {
  return (
    <div className="absolute right-0 top-8 z-50 min-w-[240px] rounded-md border border-gray-200 bg-white shadow-lg">
      <div className="px-3 py-2 text-xs font-semibold text-gray-500 border-b border-gray-100">
        Select Persona
      </div>
      <div className="py-1">
        {personas.map((persona) => (
          <button
            key={persona.id}
            onClick={() => {
              if (!disabled) {
                onSelect(persona.id);
              }
            }}
            disabled={disabled}
            className={`
              w-full px-3 py-2 text-left text-sm transition-colors
              ${
                disabled
                  ? 'cursor-not-allowed opacity-50'
                  : 'hover:bg-gray-50 cursor-pointer'
              }
              ${selectedPersonaId === persona.id ? 'bg-blue-50' : ''}
            `}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-900 flex items-center gap-2">
                  {persona.name}
                  {selectedPersonaId === persona.id && (
                    <Check className="w-4 h-4 text-blue-600 flex-shrink-0" />
                  )}
                </div>
                {persona.description && (
                  <div className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                    {persona.description}
                  </div>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
