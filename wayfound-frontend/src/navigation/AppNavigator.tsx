// src/navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Import screens
import HomeScreen from '../screens/Home/HomeScreen';
import CreateRoadmapScreen from '../screens/CreateRoadmap/CreateRoadmapScreen';
import SurveyScreen from '../screens/Survey/SurveyScreen';
import DashboardScreen from '../screens/Dashboard/DashboardScreen';
import RoadmapDetailScreen from '../screens/RoadmapDetail/RoadmapDetailScreen';
import TestScreen from '../screens/TestScreen';

import { RootStackParamList } from '../types';

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Dashboard') {
            iconName = focused ? 'grid' : 'grid-outline';
          } else if (route.name === 'CreateRoadmap') {
            iconName = focused ? 'add-circle' : 'add-circle-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: 'gray',
        headerStyle: {
          backgroundColor: '#3B82F6',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ title: 'Wayfound' }}
      />
      <Tab.Screen 
        name="CreateRoadmap" 
        component={CreateRoadmapScreen}
        options={{ title: 'Create' }}
      />
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: 'My Roadmaps' }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#3B82F6',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={TabNavigator}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="Survey" 
          component={SurveyScreen}
          options={{ 
            title: 'Personalize Your Roadmap',
            headerShown: false // We'll use custom header in SurveyScreen
          }}
        />
        <Stack.Screen 
          name="RoadmapDetail" 
          component={RoadmapDetailScreen}
          options={{ 
            title: 'Roadmap Details',
            headerShown: true
          }}
        />
        <Stack.Screen 
          name="TestScreen" 
          component={TestScreen}
          options={{ 
            title: 'Test Screen',
            headerShown: true
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}