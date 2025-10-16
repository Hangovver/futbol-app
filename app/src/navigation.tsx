import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Today from './screens/Today'; import Live from './screens/Live'; import Settings from './screens/Settings';
import MatchDetails from './screens/MatchDetails'; import Team from './screens/Team';
import Icon from './components/Icon';
const Tab = createBottomTabNavigator(); const Stack = createNativeStackNavigator();
function Tabs(){ return (<Tab.Navigator screenOptions={{ headerShown:false }}>
  <Tab.Screen name="Bugün" component={Today} options={{ tabBarIcon:()=> <Icon name="home"/> }}/>
  <Tab.Screen name="Canlı" component={Live} options={{ tabBarIcon:()=> <Icon name="home"/> }}/>
  <Tab.Screen name="Ayarlar" component={Settings} options={{ tabBarIcon:()=> <Icon name="settings"/> }}/>
</Tab.Navigator>); }
export default function RootNav(){ return (<NavigationContainer>
  <Stack.Navigator>
    <Stack.Screen name="Home" component={Tabs} options={{ headerShown:false }}/>
    <Stack.Screen name="MatchDetails" component={MatchDetails} options={{ title:'Maç Detayı' }}/>
    <Stack.Screen name="Team" component={Team} options={{ title:'Takım' }}/>
  </Stack.Navigator>
</NavigationContainer>); }