import { callApi } from './client';

export type SeedSampleDataResult = {
	status: string;
	message: string;
	summary: {
		accounts: number;
		budgets: number;
		recurring_rules: number;
		goals: number;
		transactions: number;
	};
};

export function seedSampleData() {
	return callApi<SeedSampleDataResult>('seed_sample_data');
}