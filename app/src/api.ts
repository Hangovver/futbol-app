import Constants from 'expo-constants';
const API_BASE = (Constants?.expoConfig?.extra as any)?.API_BASE || 'http://127.0.0.1:8000';
async function getJSON(path: string){ const r = await fetch(API_BASE + path); if(!r.ok) throw new Error('HTTP '+r.status); return await r.json(); }
async function postJSON(path: string, body: any){ const r = await fetch(API_BASE + path, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)}); if(!r.ok) throw new Error('HTTP '+r.status); return await r.json(); }
export async function fetchPredictions(minProb=0.7, league?: string){ const q = new URLSearchParams({ minProb: String(minProb) }); if(league) q.set('league', league); return (await getJSON(`/api/predictions?${q.toString()}`)).items; }
export async function fetchLeagues(){ return (await getJSON('/api/leagues')).items as string[]; }
export async function fetchLive(){ return (await getJSON('/api/live')).items; }
export async function fetchMatchDetails(fixtureId: number){ return await getJSON(`/api/match/${fixtureId}`); }
export async function fetchTeam(teamId: number){ return await getJSON(`/api/team/${teamId}`); }
export async function impliedOdds(selections: {prob:number,label:string}[]){ return await postJSON('/api/implied-odds', { selections }); }
export async function health(){ return await getJSON('/api/health'); }
