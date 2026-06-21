import { callApi } from './client';

export type FrequencyUnit = 'day' | 'week' | 'month' | 'year';
export type RecurringStatus = 'active' | 'paused' | 'inactive';

export type RecurringRule = {
	recurring_id: number;
	account_id: number;
	category_id: number;
	merchant?: string | null;
	amount_minor: number;
	interval: number;
	frequency_unit: FrequencyUnit;
	next_due: string;
	end_date?: string | null;
	status: RecurringStatus;
};

export function getRecurring(userId: number) {
	return callApi<RecurringRule[]>('get_recurring', userId);
}

export function getRecurringById(recurringId: number) {
	return callApi<RecurringRule | null>('get_recurring_by_id', recurringId);
}

export function getDueRecurring() {
	return callApi<RecurringRule[]>('get_due_recurring');
}

export function createRecurring(payload: {
	account_id: number;
	amount: number | string;
	interval: number;
	frequency_unit: FrequencyUnit;
	next_due: string;
	category_id: number;
	merchant?: string | null;
	end_date?: string | null;
}) {
	return callApi<{ recurring_id: number }>(
		'create_recurring',
		payload.account_id,
		payload.amount,
		payload.interval,
		payload.frequency_unit,
		payload.next_due,
		payload.category_id,
		payload.merchant ?? null,
		payload.end_date ?? null
	);
}

export function updateRecurring(
	recurringId: number,
	payload: {
		account_id?: number | null;
		amount?: number | string | null;
		interval?: number | null;
		frequency_unit?: FrequencyUnit | null;
		next_due?: string | null;
		category_id?: number | null;
		merchant?: string | null;
		end_date?: string | null;
		status?: RecurringStatus | null;
	} = {}
) {
	return callApi<void>(
		'update_recurring',
		recurringId,
		payload.account_id ?? null,
		payload.amount ?? null,
		payload.interval ?? null,
		payload.frequency_unit ?? null,
		payload.next_due ?? null,
		payload.category_id ?? null,
		payload.merchant ?? null,
		payload.end_date ?? null,
		payload.status ?? null
	);
}

export function pauseRecurring(recurringId: number) {
	return callApi<void>('pause_recurring', recurringId);
}

export function resumeRecurring(recurringId: number) {
	return callApi<void>('resume_recurring', recurringId);
}

export function deactivateRecurring(recurringId: number) {
	return callApi<void>('deactivate_recurring', recurringId);
}

export function generateTransaction(recurringId: number) {
	return callApi<{ transaction_id: number }>('generate_transaction', recurringId);
}