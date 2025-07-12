// src/screens/Survey/SurveyScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { useMutation } from '@apollo/client';
import { CREATE_ROADMAP, GET_USER_ROADMAPS } from '../../services/apollo';
import { RootStackParamList } from '../../types';
import { useAuth } from '../../contexts/AuthContext';

type SurveyRouteProp = RouteProp<RootStackParamList, 'Survey'>;

interface SurveyData {
  skillLevel: string;
  timePerDay: string;
  learningStyle: string;
  timelinePreference: string;
}

interface SurveyQuestion {
  id: keyof SurveyData;
  question: string;
  options: { value: string; label: string; icon?: string }[];
  description?: string;
}

const { width } = Dimensions.get('window');

export default function SurveyScreen() {
  const [currentStep, setCurrentStep] = useState(0);
  const [surveyData, setSurveyData] = useState<Partial<SurveyData>>({});
  const [slideAnim] = useState(new Animated.Value(0));
  const [isCreatingRoadmap, setIsCreatingRoadmap] = useState(false);
  
  const route = useRoute<SurveyRouteProp>();
  const navigation = useNavigation();
  const { user } = useAuth();
  
  const { goalText } = route.params || {};

  const [createRoadmap] = useMutation(CREATE_ROADMAP, {
    refetchQueries: [
      {
        query: GET_USER_ROADMAPS,
        variables: { userId: user?.id }
      }
    ]
  });

  // Survey questions with adaptive content
  const getSurveyQuestions = (goalText: string): SurveyQuestion[] => {
    const domain = classifyDomain(goalText);
    
    const baseQuestions: SurveyQuestion[] = [
      {
        id: 'skillLevel',
        question: 'What\'s your current skill level?',
        description: `How would you rate your experience with ${domain === 'general' ? 'this topic' : domain}?`,
        options: [
          { value: 'Complete Beginner', label: 'Complete Beginner', icon: 'leaf-outline' },
          { value: 'Some Experience', label: 'Some Experience', icon: 'partly-sunny-outline' },
          { value: 'Intermediate', label: 'Intermediate', icon: 'trending-up-outline' },
          { value: 'Advanced', label: 'Advanced', icon: 'trophy-outline' }
        ]
      },
      {
        id: 'timePerDay',
        question: 'How much time can you dedicate daily?',
        description: 'Be realistic about your schedule to get a plan that works for you.',
        options: [
          { value: '15 minutes', label: '15 minutes', icon: 'time-outline' },
          { value: '30 minutes', label: '30 minutes', icon: 'time-outline' },
          { value: '1 hour', label: '1 hour', icon: 'timer-outline' },
          { value: '2+ hours', label: '2+ hours', icon: 'hourglass-outline' }
        ]
      },
      {
        id: 'learningStyle',
        question: 'How do you prefer to learn?',
        description: 'We\'ll recommend resources that match your learning style.',
        options: [
          { value: 'Watch Videos', label: 'Watch Videos', icon: 'play-circle-outline' },
          { value: 'Read Articles', label: 'Read Articles', icon: 'book-outline' },
          { value: 'Hands-on Practice', label: 'Hands-on Practice', icon: 'build-outline' },
          { value: 'Mixed Approach', label: 'Mixed Approach', icon: 'apps-outline' }
        ]
      },
      {
        id: 'timelinePreference',
        question: 'What\'s your timeline preference?',
        description: 'This helps us adjust the intensity of your roadmap.',
        options: [
          { value: 'As fast as possible', label: 'As fast as possible', icon: 'flash-outline' },
          { value: 'Flexible pace', label: 'Flexible pace', icon: 'leaf-outline' },
          { value: 'Specific end date', label: 'Specific end date', icon: 'calendar-outline' },
          { value: 'No rush', label: 'No rush', icon: 'partly-sunny-outline' }
        ]
      }
    ];

    return baseQuestions;
  };

  const classifyDomain = (goalText: string): string => {
    const goal = goalText.toLowerCase();
    if (goal.includes('cook') || goal.includes('recipe') || goal.includes('food')) return 'cooking';
    if (goal.includes('fit') || goal.includes('gym') || goal.includes('workout')) return 'fitness';
    if (goal.includes('code') || goal.includes('program') || goal.includes('app')) return 'programming';
    if (goal.includes('language') || goal.includes('spanish') || goal.includes('french')) return 'language';
    if (goal.includes('paint') || goal.includes('draw') || goal.includes('art')) return 'art';
    return 'general';
  };

  const questions = getSurveyQuestions(goalText || '');

  const handleAnswer = async (answer: string) => {
    const question = questions[currentStep];
    const newSurveyData = { ...surveyData, [question.id]: answer };
    setSurveyData(newSurveyData);
    
    if (currentStep < questions.length - 1) {
      // Animate to next question
      Animated.timing(slideAnim, {
        toValue: -(currentStep + 1) * width,
        duration: 300,
        useNativeDriver: true
      }).start();
      setCurrentStep(currentStep + 1);
    } else {
      // Survey complete, create roadmap
      await createRoadmapFromSurvey(newSurveyData as SurveyData);
    }
  };

  const createRoadmapFromSurvey = async (completeSurveyData: SurveyData) => {
    if (!user) {
      Alert.alert('Error', 'You must be logged in to create a roadmap');
      return;
    }

    setIsCreatingRoadmap(true);

    try {
      console.log('🤖 Creating roadmap with survey data:', completeSurveyData);

      // Calculate timeline based on preferences
      let timelineDays = 30;
      if (completeSurveyData.timelinePreference === 'As fast as possible') {
        timelineDays = 14;
      } else if (completeSurveyData.timelinePreference === 'No rush') {
        timelineDays = 60;
      }

      const result = await createRoadmap({
        variables: {
          userId: user.id,
          inputData: {
            goalText: goalText,
            timelineDays: timelineDays,
            // We'll pass survey data to the backend later
            surveyData: completeSurveyData
          }
        }
      });

      if (result.data?.createRoadmap) {
        const roadmap = result.data.createRoadmap;
        Alert.alert(
          'Roadmap Created! 🎉',
          `Your personalized "${roadmap.goalText}" roadmap is ready!`,
          [
            {
              text: 'View Roadmap',
              onPress: () => navigation.navigate('RoadmapDetail', { roadmapId: roadmap.id })
            },
            {
              text: 'Dashboard',
              onPress: () => navigation.navigate('Dashboard')
            }
          ]
        );
      }
    } catch (error: any) {
      console.error('❌ Error creating roadmap:', error);
      Alert.alert('Error', 'Failed to create roadmap. Please try again.');
    } finally {
      setIsCreatingRoadmap(false);
    }
  };

  const goBack = () => {
    if (currentStep > 0) {
      Animated.timing(slideAnim, {
        toValue: -(currentStep - 1) * width,
        duration: 300,
        useNativeDriver: true
      }).start();
      setCurrentStep(currentStep - 1);
    } else {
      navigation.goBack();
    }
  };

  if (!goalText) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>No goal specified</Text>
      </View>
    );
  }

  if (isCreatingRoadmap) {
    return (
      <View style={styles.centerContainer}>
        <View style={styles.loadingIcon}>
          <Ionicons name="sync" size={48} color="#3B82F6" />
        </View>
        <Text style={styles.loadingTitle}>Creating Your Roadmap</Text>
        <Text style={styles.loadingText}>
          🤖 AI is analyzing your preferences and building a personalized plan...
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={goBack}>
          <Ionicons name="arrow-back" size={24} color="#374151" />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Let's personalize your roadmap</Text>
          <Text style={styles.goalText} numberOfLines={2}>{goalText}</Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { width: `${((currentStep + 1) / questions.length) * 100}%` }
            ]} 
          />
        </View>
        <Text style={styles.progressText}>
          {currentStep + 1} of {questions.length}
        </Text>
      </View>

      {/* Questions Container */}
      <View style={styles.questionsContainer}>
        <Animated.View 
          style={[
            styles.questionsSlider,
            { 
              transform: [{ translateX: slideAnim }],
              width: width * questions.length 
            }
          ]}
        >
          {questions.map((question, index) => (
            <View key={question.id} style={[styles.questionCard, { width }]}>
              <View style={styles.questionContent}>
                <Text style={styles.questionTitle}>{question.question}</Text>
                {question.description && (
                  <Text style={styles.questionDescription}>{question.description}</Text>
                )}
                
                <View style={styles.optionsContainer}>
                  {question.options.map((option, optionIndex) => (
                    <TouchableOpacity
                      key={optionIndex}
                      style={[
                        styles.optionButton,
                        surveyData[question.id] === option.value && styles.selectedOption
                      ]}
                      onPress={() => handleAnswer(option.value)}
                      activeOpacity={0.7}
                    >
                      {option.icon && (
                        <Ionicons 
                          name={option.icon as any} 
                          size={24} 
                          color={surveyData[question.id] === option.value ? '#3B82F6' : '#6B7280'} 
                        />
                      )}
                      <Text style={[
                        styles.optionText,
                        surveyData[question.id] === option.value && styles.selectedOptionText
                      ]}>
                        {option.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            </View>
          ))}
        </Animated.View>
      </View>

      {/* Navigation Dots */}
      <View style={styles.navigationDots}>
        {questions.map((_, index) => (
          <View
            key={index}
            style={[
              styles.dot,
              index === currentStep ? styles.activeDot : styles.inactiveDot
            ]}
          />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 8,
    marginRight: 12,
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  goalText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 18,
  },
  progressContainer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: 'white',
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    fontWeight: '500',
  },
  questionsContainer: {
    flex: 1,
    overflow: 'hidden',
  },
  questionsSlider: {
    flexDirection: 'row',
    height: '100%',
  },
  questionCard: {
    paddingHorizontal: 20,
    paddingVertical: 32,
  },
  questionContent: {
    flex: 1,
  },
  questionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
    lineHeight: 32,
  },
  questionDescription: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 32,
    lineHeight: 24,
  },
  optionsContainer: {
    gap: 12,
  },
  optionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  selectedOption: {
    borderColor: '#3B82F6',
    backgroundColor: '#EFF6FF',
  },
  optionText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
    marginLeft: 12,
  },
  selectedOptionText: {
    color: '#3B82F6',
    fontWeight: '600',
  },
  navigationDots: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingVertical: 20,
    gap: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  activeDot: {
    backgroundColor: '#3B82F6',
  },
  inactiveDot: {
    backgroundColor: '#D1D5DB',
  },
  loadingIcon: {
    marginBottom: 20,
  },
  loadingTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  loadingText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
  },
});