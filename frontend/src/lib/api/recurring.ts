import { callApi } from './client';

export type FrequencyUnit = 'day' | 'week' | 'month' | 'year';
export type RecurringStatus = 'active' | 'paused' | 'inactive';

export type RecurringRule = {
	recurring_rule_id: number;
	account_id: number;
	category_id: number;
	name: string;
	expected_amount: number | string;
	interval: number;
	frequency_unit: FrequencyUnit;
	start_date: string;
	next_due_date: string;
	end_date?: string | null;
	status: RecurringStatus;
};

export function getRecurringRules(userId: number) {
	return callApi<RecurringRule[]>('get_recurring_rules', userId);
}

export function getRecurringRule(recurringRuleId: number) {
	return callApi<RecurringRule | null>('get_recurring_rule', recurringRuleId);
}

export function getDueRecurringRules(asOf?: string | null) {
	return callApi<RecurringRule[]>('get_due_recurring_rules', asOf ?? null);
}

export function createRecurringRule(payload: {
	account_id: number;
	category_id: number;
	name: string;
	expected_amount: number | string;
	interval: number;
	frequency_unit: FrequencyUnit;
	start_date: string;
	next_due_date: string;
	end_date?: string | null;
}) {
	return callApi<{ recurring_rule_id: number }>(
		'create_recurring_rule',
		payload.account_id,
		payload.category_id,
		payload.name,
		payload.expected_amount,
		payload.interval,
		payload.frequency_unit,
		payload.start_date,
		payload.next_due_date,
		payload.end_date ?? null
	);
}

export function updateRecurringRule(
	recurringRuleId: number,
	payload: {
		account_id?: number | null;
		category_id?: number | null;
		name?: string | null;
		expected_amount?: number | string | null;
		interval?: number | null;
		frequency_unit?: FrequencyUnit | null;
		start_date?: string | null;
		next_due_date?: string | null;
		end_date?: string | null;
		status?: RecurringStatus | null;
	} = {}
) {
	return callApi<void>(
		'update_recurring_rule',
		recurringRuleId,
		payload.account_id ?? null,
		payload.category_id ?? null,
		payload.name ?? null,
		payload.expected_amount ?? null,
		payload.interval ?? null,
		payload.frequency_unit ?? null,
		payload.start_date ?? null,
		payload.next_due_date ?? null,
		payload.end_date ?? null,
		payload.status ?? null
	);
}

export function pauseRecurringRule(recurringRuleId: number) {
	return callApi<void>('pause_recurring_rule', recurringRuleId);
}

export function resumeRecurringRule(recurringRuleId: number) {
	return callApi<void>('resume_recurring_rule', recurringRuleId);
}

export function deactivateRecurringRule(recurringRuleId: number) {
	return callApi<void>('deactivate_recurring_rule', recurringRuleId);
}

export function generateTransaction(recurringRuleId: number) {
	return callApi<{ transaction_id: number }>('generate_transaction', recurringRuleId);
}
