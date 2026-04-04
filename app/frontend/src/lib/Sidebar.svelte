<script>
    import { Scale, Plus, MessageSquare, Trash2, Edit3, Check, X } from 'lucide-svelte';
    import { cases, activeCase, store } from './store.js';

    let editingId = $state(null);
    let tempTitle = $state("");

    function startEdit(c) {
        editingId = c.id;
        tempTitle = c.title;
    }

    function saveEdit() {
        if (tempTitle.trim()) {
            store.updateCase(editingId, tempTitle);
            editingId = null;
        }
    }
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
            <div class="group relative flex items-center rounded-md transition-colors 
                { $activeCase?.id === c.id ? 'bg-slate-800 text-amber-400' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200' }">
                
                {#if editingId === c.id}
                    <div class="flex-1 flex items-center gap-1 px-3 py-1.5">
                        <input 
                            bind:value={tempTitle} 
                            class="bg-transparent border-none focus:ring-0 text-sm text-white w-full h-7"
                            onkeydown={(e) => e.key === 'Enter' && saveEdit()}
                        />
                        <button onclick={saveEdit} class="text-emerald-400 hover:text-emerald-300">
                            <Check size={14} />
                        </button>
                        <button onclick={() => editingId = null} class="text-rose-400 hover:text-rose-300">
                            <X size={14} />
                        </button>
                    </div>
                {:else}
                    <button 
                        onclick={() => store.selectCase(c)}
                        class="flex-1 flex items-center gap-3 px-3 py-2 text-sm text-left truncate"
                    >
                        <MessageSquare size={16} class="shrink-0" />
                        <span class="truncate">{c.title}</span>
                    </button>
                    
                    <div class="hidden group-hover:flex items-center gap-1 pr-2">
                        <button 
                            onclick={(e) => { e.stopPropagation(); startEdit(c); }}
                            class="p-1 hover:bg-slate-700 rounded text-slate-500 hover:text-amber-500 transition-colors"
                        >
                            <Edit3 size={14} />
                        </button>
                        <button 
                            onclick={(e) => { e.stopPropagation(); store.deleteCase(c.id); }}
                            class="p-1 hover:bg-slate-700 rounded text-slate-500 hover:text-rose-500 transition-colors"
                        >
                            <Trash2 size={14} />
                        </button>
                    </div>
                {/if}
            </div>
        {/each}
    </nav>
</aside>