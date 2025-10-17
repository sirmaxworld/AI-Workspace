import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export function getQualityColor(score: number): string {
  if (score >= 0.9) return 'text-green-400 bg-green-500/20';
  if (score >= 0.75) return 'text-yellow-400 bg-yellow-500/20';
  if (score >= 0.50) return 'text-orange-400 bg-orange-500/20';
  return 'text-red-400 bg-red-500/20';
}

export function getQualityLabel(score: number): string {
  if (score >= 0.9) return 'Excellent';
  if (score >= 0.75) return 'Good';
  if (score >= 0.50) return 'Fair';
  return 'Poor';
}
