// src/screens/CreateRoadmap/CreateRoadmapScreen.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import type { NavigationProp } from '@react-navigation/native';
import { RootStackParamList } from '../../types';

type NavigationProps = NavigationProp<RootStackParamList>;

const EXAMPLE_GOALS = [
  {
    text: "Learn to cook authentic Italian pasta in 2 weeks",
    icon: "restaurant",
    color: "#FF6B6B"
  },
  {
    text: "Build muscle and get shredded in 60 days",
    icon: "fitness",
    color: "#4ECDC4"
  },
  {
    text: "Learn conversational Spanish for my trip to Mexico",
    icon: "language",
    color: "#96CEB4"
  },
  {
    text: "Master oil painting landscapes in 3 months",
    icon: "brush",
    color: "#F7DC6F"
  },
  {
    text: "Build a React Native app and publish it",
    icon: "code-slash",
    color: "#45B7D1"
  },
  {
    text: "Learn Japanese cooking techniques",
    icon: "restaurant",
    color: "#FFB74D"
  }
];

export default function CreateRoadmapScreen() {
  const [goalText, setGoalText] = useState('');
  const navigation = useNavigation<NavigationProps>();

  const handleCreateRoadmap = () => {
    console.log('🚀 Create roadmap button clicked!');
    console.log('Goal text:', goalText);
    
    if (!goalText.trim()) {
      // Could add an alert here, but let's keep it simple
      return;
    }

    // Navigate to survey instead of creating roadmap directly
    console.log('📋 Navigating to survey with goal:', goalText);
    navigation.navigate('Survey', { goalText: goalText.trim() });
  };

  const handleExampleGoal = (example: string) => {
    setGoalText(example);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>What do you want to learn?</Text>
          <Text style={styles.subtitle}>
            Tell us your goal and we'll create a personalized roadmap for you
          </Text>
        </View>

        {/* Goal Input */}
        <View style={styles.inputSection}>
          <Text style={styles.label}>Your Learning Goal</Text>
          <TextInput
            style={styles.goalInput}
            placeholder="e.g., Learn to cook Japanese ramen from scratch"
            value={goalText}
            onChangeText={setGoalText}
            multiline
            numberOfLines={3}
            textAlignVertical="top"
          />
        </View>

        {/* Example Goals */}
        <View style={styles.examplesSection}>
          <Text style={styles.examplesTitle}>Or try these examples:</Text>
          <View style={styles.examplesList}>
            {EXAMPLE_GOALS.map((example, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.exampleCard, { borderLeftColor: example.color }]}
                onPress={() => handleExampleGoal(example.text)}
              >
                <Ionicons 
                  name={example.icon as any} 
                  size={20} 
                  color={example.color} 
                />
                <Text style={styles.exampleText}>{example.text}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Create Button */}
        <TouchableOpacity
          style={[
            styles.createButton,
            !goalText.trim() && styles.createButtonDisabled
          ]}
          onPress={handleCreateRoadmap}
          disabled={!goalText.trim()}
        >
          <View style={styles.buttonContent}>
            <Text style={styles.createButtonText}>Continue to Personalization</Text>
            <Ionicons name="arrow-forward" size={20} color="white" />
          </View>
        </TouchableOpacity>

        {/* Info Section */}
        <View style={styles.infoSection}>
          <Text style={styles.infoTitle}>What happens next?</Text>
          <View style={styles.infoStep}>
            <Ionicons name="clipboard-outline" size={20} color="#3B82F6" />
            <Text style={styles.infoText}>Answer a few questions about your preferences</Text>
          </View>
          <View style={styles.infoStep}>
            <Ionicons name="sparkles-outline" size={20} color="#3B82F6" />
            <Text style={styles.infoText}>AI creates a personalized roadmap just for you</Text>
          </View>
          <View style={styles.infoStep}>
            <Ionicons name="rocket-outline" size={20} color="#3B82F6" />
            <Text style={styles.infoText}>Start learning with your custom plan</Text>
          </View>
        </View>

        {/* Tips */}
        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>💡 Tips for better roadmaps:</Text>
          <Text style={styles.tip}>• Be specific about what you want to learn</Text>
          <Text style={styles.tip}>• Include your current skill level if relevant</Text>
          <Text style={styles.tip}>• Mention any time constraints or preferences</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 20,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    lineHeight: 24,
  },
  inputSection: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  goalInput: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  examplesSection: {
    marginBottom: 32,
  },
  examplesTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 16,
  },
  examplesList: {
    gap: 12,
  },
  exampleCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  exampleText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  createButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 24,
  },
  createButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  createButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  infoSection: {
    backgroundColor: '#EFF6FF',
    padding: 20,
    borderRadius: 12,
    marginBottom: 24,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E40AF',
    marginBottom: 16,
  },
  infoStep: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 12,
  },
  infoText: {
    fontSize: 14,
    color: '#1E40AF',
    flex: 1,
  },
  tipsSection: {
    backgroundColor: '#F0FDF4',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#10B981',
  },
  tipsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#065F46',
    marginBottom: 8,
  },
  tip: {
    fontSize: 14,
    color: '#065F46',
    marginBottom: 4,
  },
});