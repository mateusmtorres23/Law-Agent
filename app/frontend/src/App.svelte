<script>
    import { onMount } from 'svelte';
    import Sidebar from './lib/Sidebar.svelte';
    import ChatCanvas from './lib/ChatCanvas.svelte';
    import { store } from './lib/store.js';

    onMount(() => {
        store.fetchCases();
    });
</script>

<main class="flex h-screen w-full bg-slate-900 text-slate-200 overflow-hidden font-sans">
    <Sidebar />
    <ChatCanvas />
</main>