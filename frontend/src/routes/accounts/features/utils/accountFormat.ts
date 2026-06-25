import type { Account, AccountType } from '$lib/api/accounts';

export type AccountTypeOption = {
	value: AccountType;
	label: string;
};

export const accountTypes: AccountTypeOption[] = [
	{ value: 'checking', label: 'Checking' },
	{ value: 'savings', label: 'Savings' },
	{ value: 'cash', label: 'Cash' },
	{ value: 'credit_card', label: 'Credit Card' },
	{ value: 'line_of_credit', label: 'Line of Credit' },
	{ value: 'loan', label: 'Loan' },
	{ value: 'mortgage', label: 'Mortgage' },
	{ value: 'investment', label: 'Investment' },
	{ value: 'other_asset', label: 'Other Asset' },
	{ value: 'other_liability', label: 'Other Liability' }
];

const typeColors: Record<string, string> = {
	checking: '#6366f1',
	savings: '#10b981',
	cash: '#f59e0b',
	credit_card: '#f43f5e',
	line_of_credit: '#fb7185',
	loan: '#f97316',
	mortgage: '#ea580c',
	investment: '#8b5cf6',
	other_asset: '#06b6d4',
	other_liability: '#64748b'
};

export function typeColor(type: string) {
	return typeColors[type] ?? '#64748b';
}

export function typeLabel(type: string) {
	return accountTypes.find((accountType: AccountTypeOption) => accountType.value === type)?.label ?? type;
}

export function formatBalance(minor: number | undefined | null) {
	if (minor == null) return '—';
	return '₱' + (minor / 100).toLocaleString('en-PH', { minimumFractionDigits: 2 });
}

export function accountBalance(account: Account) {
	return account.current_balance_minor ?? account.opening_balance_minor;
}

export function openingBalanceForCurrentBalance(account: Account, currentBalance: string) {
	const desiredCurrentMinor = Math.round(Number(currentBalance || 0) * 100);
	const transactionTotalMinor = accountBalance(account) - account.opening_balance_minor;

	return ((desiredCurrentMinor - transactionTotalMinor) / 100).toFixed(2);
}

export function sanitizeBalance(value: string) {
	return value
		.replace(/[^\d.]/g, '')
		.replace(/(\..*)\./g, '$1')
		.replace(/^(\d*)(\.\d{0,2}).*$/, '$1$2');
}
