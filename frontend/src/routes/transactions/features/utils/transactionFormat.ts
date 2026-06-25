export function formatMoney(amountMinor: number) {
	return new Intl.NumberFormat('en-PH', {
		style: 'currency',
		currency: 'PHP'
	}).format(amountMinor / 100);
}

export function formatDate(value: string) {
	return new Date(value).toLocaleDateString('en-PH', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

export function formatGroupDate(value: string) {
	return new Date(value).toLocaleDateString('en-PH', {
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	});
}

export function dateInputValue(value: string) {
	return value.slice(0, 10);
}

export function todayInputValue() {
	return new Date().toISOString().slice(0, 10);
}

export function amountInputToMinor(value: string) {
	if (!value.trim()) return null;

	const amount = Number(value);

	if (!Number.isFinite(amount)) return null;
	return Math.round(amount * 100);
}
