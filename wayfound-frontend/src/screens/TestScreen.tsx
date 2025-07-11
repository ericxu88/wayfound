// src/screens/TestScreen.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRoute } from '@react-navigation/native';

export default function TestScreen() {
  const route = useRoute();
  
  console.log('🧪 TestScreen rendered');
  console.log('📍 Route params:', route.params);
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Test Screen Works! 🎉</Text>
      <Text style={styles.text}>
        Route params: {JSON.stringify(route.params, null, 2)}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F9FAFB',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 20,
  },
  text: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    fontFamily: 'monospace',
  },
});