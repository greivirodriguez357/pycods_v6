import React from 'react';
import { ActivityIndicator, LogBox, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { AuthProvider, useAuth } from './src/auth';
import { SettingsProvider } from './src/settings';
import { C } from './src/theme';
import AuthScreen from './src/screens/AuthScreen';
import HomeScreen from './src/screens/HomeScreen';
import GamesScreen from './src/screens/GamesScreen';
import MonsterScreen from './src/screens/MonsterScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import LessonScreen from './src/screens/LessonScreen';
import MemoryScreen from './src/screens/MemoryScreen';
import BreatheScreen from './src/screens/BreatheScreen';
import TeacherScreen from './src/screens/TeacherScreen';

// Expo Go avisa que las notificaciones PUSH remotas no existen ahí; aquí solo usamos recordatorios locales.
LogBox.ignoreLogs(['expo-notifications']);

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const icon = (emoji: string) => () => <Text style={{ fontSize: 26 }}>{emoji}</Text>;

function Tabs() {
  const { user } = useAuth();
  const staff = user?.rol === 'docente' || user?.rol === 'admin';
  return (
    <Tab.Navigator screenOptions={{
      headerShown: false,
      tabBarActiveTintColor: C.primary,
      tabBarLabelStyle: { fontSize: 13, fontWeight: '800' },
      tabBarStyle: { height: 72, paddingTop: 6, paddingBottom: 8 },
    }}>
      <Tab.Screen name="Inicio" component={HomeScreen} options={{ tabBarIcon: icon('🏠') }} />
      <Tab.Screen name="Juegos" component={GamesScreen} options={{ tabBarIcon: icon('🎮') }} />
      <Tab.Screen name="Monstruo" component={MonsterScreen} options={{ tabBarIcon: icon('👾') }} />
      {staff && <Tab.Screen name="Panel" component={TeacherScreen} options={{ tabBarIcon: icon('📊') }} />}
      <Tab.Screen name="Yo" component={ProfileScreen} options={{ tabBarIcon: icon('⭐') }} />
    </Tab.Navigator>
  );
}

function Root() {
  const { user, loading } = useAuth();
  if (loading) {
    return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: C.bg }}><ActivityIndicator size="large" color={C.primary} /></View>;
  }
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <>
            <Stack.Screen name="Tabs" component={Tabs} />
            <Stack.Screen name="Lesson" component={LessonScreen} />
            <Stack.Screen name="Memory" component={MemoryScreen} />
            <Stack.Screen name="Breathe" component={BreatheScreen} />
          </>
        ) : (
          <Stack.Screen name="Auth" component={AuthScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <SettingsProvider>
        <AuthProvider>
          <StatusBar style="dark" />
          <Root />
        </AuthProvider>
      </SettingsProvider>
    </SafeAreaProvider>
  );
}
