import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, FlatList, TouchableOpacity, TextInput, RefreshControl } from 'react-native';
import { fetchPredictions, fetchLeagues } from '../api'; import { toTR } from '../labels'; import { theme } from '../theme';
import Card from '../components/Card'; import Badge from '../components/Badge'; import Logo from '../components/Logo'; import Header from '../components/Header'; import EmptyView from '../components/EmptyView';
import { useNavigation } from '@react-navigation/native';
export default function Today(){
  const [items,setItems] = useState<any[]>([]); const [loading,setLoading] = useState(true);
  const [league,setLeague] = useState<string|undefined>(undefined); const [leagues,setLeagues] = useState<string[]>([]);
  const [q, setQ] = useState(''); const [minProb] = useState(0.7);
  const nav = useNavigation<any>();
  const load = useCallback(async ()=>{ setLoading(true); setItems(await fetchPredictions(minProb, league)); setLoading(false); },[league]);
  useEffect(()=>{ (async()=> setLeagues(await fetchLeagues()))(); },[]);
  useEffect(()=>{ load(); },[load]);
  const t=theme.dark;
  const leagueList = ['Tümü', ...leagues];
  const filtered = (league? items.filter(x=> x.league===league): items).filter(x=> !q || (x.home+x.away).toLowerCase().includes(q.toLowerCase()));
  return (<View style={{ flex:1, backgroundColor:t.bg, padding:16 }}>
    <Header title="Bugün" />
    <View style={{ flexDirection:'row', marginBottom:12 }}><TextInput value={q} onChangeText={setQ} placeholder="Ara: takım adı" placeholderTextColor="#64748b" style={{ flex:1, backgroundColor:t.card, color:t.text, borderRadius:12, paddingHorizontal:12, paddingVertical:10, borderWidth:1, borderColor:t.border }}/></View>
    <FlatList data={leagueList} horizontal keyExtractor={(x)=>x} style={{ marginBottom:12 }} renderItem={({item})=>{ const active=(item==='Tümü'&&!league) || item===league; return (<TouchableOpacity onPress={()=> setLeague(item==='Tümü'? undefined : item)} style={{ paddingHorizontal:12, paddingVertical:8, borderRadius:16, backgroundColor: active? t.primary: t.chip, marginRight:8 }}><Text style={{ color: active? '#fff': t.chipText }}>{item}</Text></TouchableOpacity>); }}/>
    <FlatList data={filtered} keyExtractor={(x,i)=> x.home+x.away+i} refreshControl={<RefreshControl refreshing={loading} onRefresh={load}/>} ListEmptyComponent={!loading? <EmptyView text="Gösterilecek maç yok."/> : null} renderItem={({item})=> (
      <Card>
        <View style={{ flexDirection:'row', alignItems:'center', justifyContent:'space-between' }}>
          <View style={{ flexDirection:'row', alignItems:'center', flex:1 }}><Logo uri={item.logos?.home}/><Text style={{ color:t.text, fontWeight:'800' }}>{item.home}</Text><Text style={{ color:t.text, marginHorizontal:6 }}>–</Text><Text style={{ color:t.text, fontWeight:'800' }}>{item.away}</Text></View>
      </View>
        <Text style={{ color:t.sub, marginTop:4 }}>{item.whenTR} — {item.league}</Text>
        <Text style={{ color:t.text, fontWeight:'700', marginTop:6 }}>Benim Tahminim: {toTR(item.topPick.bet)} (%{Math.round(item.topPick.p*100)})</Text>
        <View style={{ flexDirection:'row', flexWrap:'wrap', marginTop:6 }}>{Object.entries(item.probs).sort((a:any,b:any)=> b[1]-a[1]).slice(0,10).map(([k,v], idx)=> <Badge key={idx} label={`${toTR(k)}:${Math.round(v*100)}`}/>)}</View>
        <TouchableOpacity onPress={()=> nav.navigate('MatchDetails', { item })} style={{ paddingVertical:8, paddingHorizontal:12, borderRadius:12, backgroundColor:t.primary, marginTop:8, alignSelf:'flex-start' }}><Text style={{ color:'#fff' }}>Detay</Text></TouchableOpacity>
      </Card>
    )}/>
  </View>);
}
