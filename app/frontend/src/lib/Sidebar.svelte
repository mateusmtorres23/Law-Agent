<script>
    import { Scale, Plus, MessageSquare } from 'lucide-svelte';
    import { cases, activeCase, store } from './store.js';
</script>

<aside class="w-64 flex flex-col border-r border-slate-800 bg-slate-950">
    <div class="p-6 flex items-center gap-3">
        <Scale class="text-amber-500 w-8 h-8" />
        <h1 class="text-xl font-bold tracking-tight text-white">CJ LawAssist</h1>
    </div>

    <div class="px-4 mb-6">
        <button 
            onclick={() => store.createCase(`Matter ${$cases.length + 1}`)}
            class="w-full flex items-center justify-center gap-2 bg-amber-600 hover:bg-amber-700 text-white py-2.5 rounded-lg transition-all font-medium shadow-lg"
        >
            <Plus size={18} /> New Chat
        </button>
    </div>

    <nav class="flex-1 overflow-y-auto px-2 space-y-1">
        <div class="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-widest">History</div>
        {#each $cases as c}
            <button 
                onclick={() => store.selectCase(c)}
                class="w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm
                { $activeCase?.id === c.id ? 'bg-slate-800 text-amber-400' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200' } "
            >
                <MessageSquare size={16} />
                <span class="truncate">{c.title}</span>
            </button>
        {/each}
    </nav>
</aside>