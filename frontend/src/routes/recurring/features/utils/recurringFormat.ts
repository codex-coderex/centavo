import type { FrequencyUnit, RecurringRule } from '$lib/api/recurring';

export function formatMoney(amountMinor: number) {
	return new Intl.NumberFormat('en-PH', {
		style: 'currency',
		currency: 'PHP'
	}).format(amountMinor / 100);
}

export function formatDate(value: string | null | undefined) {
	if (!value) return '—';

	return new Date(value).toLocaleDateString('en-CA');
}

export function todayInputValue() {
	return new Date().toISOString().slice(0, 10);
}

export function amountInputValue(amountMinor: number) {
	return (amountMinor / 100).toFixed(2);
}

export function frequencyLabel(interval: number, unit: FrequencyUnit) {
	const plural = interval === 1 ? unit : `${unit}s`;
	return `Every ${interval} ${plural}`;
}

export function isRuleDue(rule: RecurringRule, today = todayInputValue()) {
	return rule.status === 'active' && rule.next_due_date.slice(0, 10) <= today;
}

export function sanitizeSignedAmount(value: string) {
	const negative = value.trim().startsWith('-');
	const cleaned = value
		.replace(/[^\d.]/g, '')
		.replace(/(\..*)\./g, '$1')
		.replace(/^(\d*)(\.\d{0,2}).*$/, '$1$2');

	return `${negative ? '-' : ''}${cleaned}`;
}
