export type ApiResponse<T> = {
	ok: boolean;
	data?: T;
	error?: string;
};

type BridgeMethod = (...args: unknown[]) => Promise<ApiResponse<unknown>>;

declare global {
	interface Window {
		pywebview?: {
			api?: Record<string, BridgeMethod>;
		};
		py?: Record<string, BridgeMethod>;
	}
}

function getBridge(): Record<string, BridgeMethod> {
	if (typeof window === 'undefined') {
		throw new Error('Python bridge is not available during SSR.');
	}

	if (window.pywebview?.api) {
		return window.pywebview.api;
	}

	if (window.py) {
		return window.py;
	}

	throw new Error('Python bridge is not available.');
}

export async function callApi<T>(
	methodName: string,
	...args: unknown[]
): Promise<T> {
	const bridge = getBridge();
	const method = bridge[methodName];

	if (typeof method !== 'function') {
		throw new Error(`Python API method not found: ${methodName}`);
	}

	const result = await method(...args);

	if (!result || typeof result !== 'object' || !('ok' in result)) {
		throw new Error(`Invalid backend response from ${methodName}`);
	}

	if (!result.ok) {
		throw new Error(result.error || 'Unknown backend error');
	}

	return result.data as T;
}