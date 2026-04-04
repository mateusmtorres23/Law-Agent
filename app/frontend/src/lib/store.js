import { writable } from 'svelte/store';

export const activeCase = writable(null);
export const cases = writable([]);
export const messages = writable([]);
export const isUploading = writable(false);

let socket;

export const store = {
    async fetchCases() {
        const res = await fetch('/api/cases');
        const data = await res.json();
        cases.set(data);
    },

    async createCase(title) {
        const res = await fetch(`/api/cases?title=${encodeURIComponent(title)}`, { method: 'POST' });
        const newCase = await res.json();
        cases.update(c => [...c, newCase]);
        this.selectCase(newCase);
    },

    selectCase(caseObj) {
        activeCase.set(caseObj);
        messages.set([]); // Clear messages for new context
        this.connectWebSocket(caseObj.id);
    },

    connectWebSocket(caseId) {
        if (socket) socket.close();
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${protocol}//${window.location.host}/api/chat/${caseId}`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            messages.update(m => [...m, data]);
        };
    },

    sendMessage(text) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            const userMsg = { role: 'user', content: text };
            messages.update(m => [...m, userMsg]);
            socket.send(JSON.stringify({ text }));
        }
    },

    async uploadDocument(caseId, file) {
        isUploading.set(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            await fetch(`/api/cases/${caseId}/documents`, {
                method: 'POST',
                body: formData
            });
        } finally {
            isUploading.set(false);
        }
    }
};