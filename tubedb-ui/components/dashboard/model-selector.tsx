"use client";

import { Model } from "@/lib/api-client";

interface ModelSelectorProps {
  models: Model[];
  selectedModel: string;
  onSelect: (modelId: string) => void;
}

export function ModelSelector({
  models,
  selectedModel,
  onSelect,
}: ModelSelectorProps) {
  return (
    <div className="flex flex-col gap-2">
      <label
        htmlFor="model-select"
        className="text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        AI Model
      </label>
      <select
        id="model-select"
        value={selectedModel}
        onChange={(e) => onSelect(e.target.value)}
        className="block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name} ({model.provider})
          </option>
        ))}
      </select>
      {selectedModel && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {models.find((m) => m.id === selectedModel)?.description}
        </p>
      )}
    </div>
  );
}
