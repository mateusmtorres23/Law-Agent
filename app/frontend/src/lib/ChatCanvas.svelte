<script>
    import { messages, activeCase, store, isUploading } from './store.js';
    import { Send, Paperclip, Loader2, Scale } from 'lucide-svelte';

    let text = $state("");
    let fileInput = $state(null);

    function handleSend() {
        if (text.trim()) {
            store.sendMessage(text);
            text = "";
        }
    }

    async function handleFile(e) {
        const file = e.target.files[0];
        if (file && $activeCase) {
            await store.uploadDocument($activeCase.id, file);
        }
    }
</script>

<section class="flex-1 flex flex-col relative bg-slate-900">
    {#if $activeCase}
        <header class="h-16 border-b border-slate-800 flex items-center px-8 bg-slate-900/50 backdrop-blur">
            <h2 class="text-lg font-semibold text-white">{$activeCase.title}</h2>
        </header>

        <div class="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-thin scrollbar-thumb-slate-700">
            {#each $messages as msg}
                <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}">
                    <div class="max-w-[70%] p-4 rounded-2xl text-sm leading-relaxed 
                        {msg.role === 'user' ? 'bg-amber-600 text-white rounded-br-none' : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700 shadow-sm'}">
                        {msg.content}
                    </div>
                </div>
            {/each}
        </div>

        <div class="p-6">
            <div class="max-w-4xl mx-auto relative bg-slate-800 rounded-xl border border-slate-700 shadow-2xl">
                {#if $isUploading}
                    <div class="absolute -top-10 left-0 flex items-center gap-2 text-xs text-amber-400 font-medium">
                        <Loader2 class="animate-spin" size={14} /> 
                        <span>Parsing Legal Document Context...</span>
                    </div>
                {/if}
                <div class="flex items-center p-2">
                    <button 
                        onclick={() => fileInput.click()} 
                        class="p-2 text-slate-400 hover:text-amber-500 transition-colors"
                        title="Attach Legal Document"
                    >
                        <Paperclip size={20} />
                    </button>
                    <input 
                        type="file" 
                        bind:this={fileInput} 
                        onchange={handleFile} 
                        class="hidden" 
                        accept=".pdf" 
                    />
                    <input 
                        bind:value={text} 
                        onkeydown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Analyze case law or ask a question..." 
                        class="flex-1 bg-transparent border-none focus:ring-0 text-slate-200 text-sm px-3 py-2 placeholder:text-slate-500"
                    />
                    <button 
                        onclick={handleSend} 
                        class="p-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-all active:scale-95 shadow-md"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    {:else}
        <div class="flex-1 flex flex-col items-center justify-center text-slate-500 space-y-4">
            <div class="p-6 rounded-full bg-slate-800/50 border border-slate-700/50">
                <Scale size={48} class="opacity-20 text-amber-500" />
            </div>
            <div class="text-center">
                <p class="text-slate-400 font-medium">No Matter Selected</p>
                <p class="text-sm opacity-60">Create a new case or select an existing one from the sidebar.</p>
            </div>
        </div>
    {/if}
</section>