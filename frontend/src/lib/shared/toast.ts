import { writable } from 'svelte/store';

export type ToastKind = 'success' | 'error' | 'info';

export type Toast = {
	id: number;
	kind: ToastKind;
	message: string;
};

export const toasts = writable<Toast[]>([]);

export function showToast(message: string, kind: ToastKind = 'info') {
	const id = Date.now() + Math.floor(Math.random() * 1000);

	toasts.update((items) => [...items, { id, kind, message }]);
	window.setTimeout(() => dismissToast(id), 4200);
}

export function dismissToast(id: number) {
	toasts.update((items) => items.filter((toast) => toast.id !== id));
}
