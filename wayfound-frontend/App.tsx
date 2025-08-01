// App.tsx
import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { ApolloProvider } from '@apollo/client';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import AuthScreen from './src/screens/Auth/AuthScreen';
import AppNavigator from './src/navigation/AppNavigator';
import { apolloClient, testConnection } from './src/services/apollo';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  // Test connection on app load
  useEffect(() => {
    const checkConnection = async () => {
      console.log('🚀 App started, testing backend connection...');
      const isConnected = await testConnection();
      if (!isConnected) {
        console.log('⚠️  Backend connection failed. Make sure your backend is running on localhost:8000');
      }
    };
    
    checkConnection();
  }, []);

  if (isLoading) {
    return null; // You could add a loading screen here
  }

  return isAuthenticated ? <AppNavigator /> : <AuthScreen />;
}

export default function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <SafeAreaProvider>
        <GestureHandlerRootView style={{ flex: 1 }}>
          <AuthProvider>
            <AppContent />
            <StatusBar style="auto" />
          </AuthProvider>
        </GestureHandlerRootView>
      </SafeAreaProvider>
    </ApolloProvider>
  );
}