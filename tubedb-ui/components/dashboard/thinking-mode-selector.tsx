"use client";

interface ThinkingModeSelectorProps {
  selectedMode: string;
  onSelect: (mode: string) => void;
}

const THINKING_MODES = [
  {
    id: "quick",
    name: "Quick Analysis",
    description: "Fast responses for simple queries (5-10s)",
    icon: "⚡",
  },
  {
    id: "deep",
    name: "Deep Reasoning",
    description: "Multi-step analysis with cross-referencing (30-60s)",
    icon: "🧠",
  },
  {
    id: "critical",
    name: "Critical Analysis",
    description: "Systematic validation and risk assessment (60-120s)",
    icon: "🔍",
  },
];

export function ThinkingModeSelector({
  selectedMode,
  onSelect,
}: ThinkingModeSelectorProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Thinking Mode
      </label>
      <div className="grid grid-cols-3 gap-2">
        {THINKING_MODES.map((mode) => (
          <button
            key={mode.id}
            onClick={() => onSelect(mode.id)}
            className={`flex flex-col items-center gap-1 rounded-lg border-2 p-3 text-center transition-colors ${
              selectedMode === mode.id
                ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                : "border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600"
            }`}
          >
            <span className="text-2xl">{mode.icon}</span>
            <span className="text-xs font-medium">{mode.name}</span>
          </button>
        ))}
      </div>
      {selectedMode && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {THINKING_MODES.find((m) => m.id === selectedMode)?.description}
        </p>
      )}
    </div>
  );
}
