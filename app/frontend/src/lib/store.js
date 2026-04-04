import { writable } from 'svelte/store';

export const activeCase = writable(null);
export const cases = writable([]);
export const messages = writable([]);
export const isUploading = writable(false);

const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

let socket;

export const store = {
    async fetchCases() {
        const res = await fetch(`${API_BASE}/api/cases`);
        const data = await res.json();
        cases.set(data);
    },

    async fetchMessages(caseId) {
        const res = await fetch(`${API_BASE}/api/cases/${caseId}/messages`);
        const data = await res.json();
        messages.set(data);
    },

    async createCase(title) {
        const res = await fetch(`${API_BASE}/api/cases?title=${encodeURIComponent(title)}`, { method: 'POST' });
        const newCase = await res.json();
        cases.update(c => [...c, newCase]);
        this.selectCase(newCase);
    },

    async selectCase(caseObj) {
        activeCase.set(caseObj);
        await this.fetchMessages(caseObj.id);
        this.connectWebSocket(caseObj.id);
    },

    connectWebSocket(caseId) {
        if (socket) socket.close();
        
        socket = new WebSocket(`${WS_BASE}/api/chat/${caseId}`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            messages.update(m => [...m, data]);
        };

        socket.onerror = (err) => {
            console.error("WebSocket Error:", err);
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
            await fetch(`${API_BASE}/api/cases/${caseId}/documents`, {
                method: 'POST',
                body: formData
            });
        } finally {
            isUploading.set(false);
        }
    },
    
    async updateCase(caseId, newTitle) {
        await fetch(`${API_BASE}/api/cases/${caseId}?title=${encodeURIComponent(newTitle)}`, { method: 'PUT' });
        cases.update(cList => cList.map(c => c.id === caseId ? { ...c, title: newTitle } : c));
        activeCase.update(curr => curr && curr.id === caseId ? { ...curr, title: newTitle } : curr);
    },

    async deleteCase(caseId) {
        await fetch(`${API_BASE}/api/cases/${caseId}`, { method: 'DELETE' });
        cases.update(cList => cList.filter(c => c.id !== caseId));
        activeCase.update(curr => {
            if (curr && curr.id === caseId) {
                messages.set([]);
                if (socket) socket.close();
                return null;
            }
            return curr;
        });
    }
};

