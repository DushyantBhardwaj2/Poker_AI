import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

// Enforce multi-tenant isolation
api.interceptors.request.use((config) => {
  const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') || 'default-user-id' : 'default-user-id';
  config.headers['X-User-Id'] = userId;
  return config;
});

export const PokerAPI = {
  startSession: () => api.post('/game/session/start'),
  addPlayer: (sessionId: string, playerName: string, stack: number) =>
    api.post('/game/session/add_player', { session_id: sessionId, player_name: playerName, stack }),
  recordAction: (sessionId: string, playerName: string, actionType: string, amount: number) =>
    api.post('/game/session/record_action', { session_id: sessionId, player_name: playerName, action_type: actionType, amount }),
  nextStreet: (sessionId: string, nextStreet: string) =>
    api.post('/game/session/next_street', { session_id: sessionId, next_street: nextStreet }),
  showdown: (sessionId: string, payload: any) =>
    api.post('/game/session/showdown', payload),
  
  // AI Endpoints
  analyzeFull: (payload: any) => api.post('/ai/analyze-full', payload),
  
  getStats: () => api.get('/stats')
};
