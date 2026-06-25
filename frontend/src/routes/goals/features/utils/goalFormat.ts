export function formatMoney(amountMinor: number) {
	return new Intl.NumberFormat('en-PH', {
		style: 'currency',
		currency: 'PHP'
	}).format(amountMinor / 100);
}

export function formatDate(value: string | null | undefined) {
	if (!value) return 'No target date';

	return new Date(value).toLocaleDateString('en-PH', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

export function dateInputValue(value: string | null | undefined) {
	return value ? value.slice(0, 10) : '';
}

export function goalProgress(allocatedMinor: number, targetMinor: number) {
	if (targetMinor <= 0) return 0;
	return Math.min((allocatedMinor / targetMinor) * 100, 100);
}

export function sanitizeAmountInput(value: string) {
	return value
		.replace(/[^\d.]/g, '')
		.replace(/(\..*)\./g, '$1')
		.replace(/^(\d*)(\.\d{0,2}).*$/, '$1$2');
}
