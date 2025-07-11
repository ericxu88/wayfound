// src/screens/Home/HomeScreen.tsx
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const navigation = useNavigation();

  const exampleGoals = [
    {
      icon: 'restaurant',
      title: 'Learn to cook Italian pasta',
      domain: 'Cooking',
      color: '#FF6B6B',
    },
    {
      icon: 'fitness',
      title: 'Build muscle in 8 weeks',
      domain: 'Fitness', 
      color: '#4ECDC4',
    },
    {
      icon: 'code-slash',
      title: 'Build a React Native app',
      domain: 'Programming',
      color: '#45B7D1',
    },
    {
      icon: 'language',
      title: 'Speak conversational Spanish',
      domain: 'Language',
      color: '#96CEB4',
    },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Hero Section */}
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.heroSection}
      >
        <View style={styles.heroContent}>
          <Text style={styles.heroTitle}>Welcome to Wayfound</Text>
          <Text style={styles.heroSubtitle}>
            AI-powered roadmaps for any skill you want to master
          </Text>
          <TouchableOpacity
            style={styles.startButton}
            onPress={() => navigation.navigate('CreateRoadmap')}
          >
            <Text style={styles.startButtonText}>Create Your Roadmap</Text>
            <Ionicons name="arrow-forward" size={20} color="white" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Features Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>How Wayfound Works</Text>
        
        <View style={styles.featureGrid}>
          <View style={styles.featureCard}>
            <Ionicons name="chatbubble-ellipses" size={32} color="#3B82F6" />
            <Text style={styles.featureTitle}>Tell us your goal</Text>
            <Text style={styles.featureText}>
              Just type what you want to learn - we'll handle the rest
            </Text>
          </View>

          <View style={styles.featureCard}>
            <Ionicons name="map" size={32} color="#10B981" />
            <Text style={styles.featureTitle}>Get your roadmap</Text>
            <Text style={styles.featureText}>
              AI creates a personalized plan with milestones and resources
            </Text>
          </View>

          <View style={styles.featureCard}>
            <Ionicons name="trending-up" size={32} color="#F59E0B" />
            <Text style={styles.featureTitle}>Track progress</Text>
            <Text style={styles.featureText}>
              Complete milestones and watch your skills grow day by day
            </Text>
          </View>
        </View>
      </View>

      {/* Example Goals */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Popular Learning Goals</Text>
        <Text style={styles.sectionSubtitle}>
          Get inspired by what others are learning
        </Text>

        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.goalList}>
            {exampleGoals.map((goal, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.goalCard, { borderLeftColor: goal.color }]}
                onPress={() => navigation.navigate('CreateRoadmap')}
              >
                <Ionicons 
                  name={goal.icon as any} 
                  size={24} 
                  color={goal.color} 
                />
                <Text style={styles.goalTitle}>{goal.title}</Text>
                <Text style={styles.goalDomain}>{goal.domain}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </View>

      {/* CTA Section */}
      <View style={styles.ctaSection}>
        <Text style={styles.ctaTitle}>Ready to start learning?</Text>
        <Text style={styles.ctaText}>
          Join thousands of learners achieving their goals with AI-powered roadmaps
        </Text>
        <TouchableOpacity
          style={styles.ctaButton}
          onPress={() => navigation.navigate('CreateRoadmap')}
        >
          <Text style={styles.ctaButtonText}>Get Started Free</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  heroSection: {
    paddingHorizontal: 20,
    paddingVertical: 40,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  heroContent: {
    alignItems: 'center',
  },
  heroTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 12,
  },
  heroSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  startButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  startButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 24,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 20,
  },
  featureGrid: {
    gap: 16,
  },
  featureCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginTop: 12,
    marginBottom: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  goalList: {
    flexDirection: 'row',
    gap: 16,
    paddingHorizontal: 4,
  },
  goalCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    width: width * 0.7,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  goalTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginTop: 8,
    marginBottom: 4,
  },
  goalDomain: {
    fontSize: 12,
    color: '#6B7280',
    textTransform: 'uppercase',
    fontWeight: '500',
  },
  ctaSection: {
    backgroundColor: '#1F2937',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  ctaTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  ctaText: {
    fontSize: 14,
    color: '#D1D5DB',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  ctaButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 25,
  },
  ctaButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});