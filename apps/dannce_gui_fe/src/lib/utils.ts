import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function timestampString(ts: number) {
  return new Date(ts * 1000).toLocaleString('en-US');
}
