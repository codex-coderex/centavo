import type { BudgetPeriodType } from '$lib/api/budgets';

export function formatMoney(amountMinor: number) {
	return new Intl.NumberFormat('en-PH', {
		style: 'currency',
		currency: 'PHP'
	}).format(amountMinor / 100);
}

export function formatDate(value: string | null | undefined) {
	if (!value) return 'No end date';

	return new Date(value).toLocaleDateString('en-PH', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

export function dateInputValue(value: string | null | undefined) {
	return value ? value.slice(0, 10) : '';
}

export function todayInputValue() {
	return new Date().toISOString().slice(0, 10);
}

export function defaultBudgetName(date = new Date()) {
	return date.toLocaleDateString('en-PH', {
		year: 'numeric',
		month: 'long'
	});
}

export function periodLabel(period: BudgetPeriodType) {
	return period[0].toUpperCase() + period.slice(1);
}

export function sanitizeAmountInput(value: string) {
	return value
		.replace(/[^\d.]/g, '')
		.replace(/(\..*)\./g, '$1')
		.replace(/^(\d*)(\.\d{0,2}).*$/, '$1$2');
}
