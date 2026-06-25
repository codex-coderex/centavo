<script lang="ts">
	import { showToast } from '$lib/shared/toast';

	let { error = '', notice = '' } = $props<{
		error?: string;
		notice?: string;
	}>();

	let lastError = $state('');
	let lastNotice = $state('');

	$effect(() => {
		if (error && error !== lastError) {
			lastError = error;
			showToast(error, 'error');
		}

		if (notice && notice !== lastNotice) {
			lastNotice = notice;
			showToast(notice, 'success');
		}
	});
</script>
