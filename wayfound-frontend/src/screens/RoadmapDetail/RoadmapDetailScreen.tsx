// src/screens/RoadmapDetail/RoadmapDetailScreen.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Linking,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery, gql } from '@apollo/client';
import { useRoute, RouteProp } from '@react-navigation/native';
import { RootStackParamList, Milestone } from '../../types';

type RoadmapDetailRouteProp = RouteProp<RootStackParamList, 'RoadmapDetail'>;

const GET_ROADMAP = gql`
  query GetRoadmap($roadmapId: String!) {
    roadmap(roadmapId: $roadmapId) {
      id
      goalText
      domain
      timelineDays
      status
      createdAt
      milestones {
        id
        day
        title
        description
        tasks
        resources
        completed
      }
    }
  }
`;

export default function RoadmapDetailScreen() {
  const [expandedMilestone, setExpandedMilestone] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const route = useRoute<RoadmapDetailRouteProp>();
  const { roadmapId } = route.params;

  console.log('🎯 RoadmapDetailScreen - ID:', roadmapId);

  const { data, loading, error, refetch } = useQuery(GET_ROADMAP, {
    variables: { roadmapId },
    errorPolicy: 'all',
    onCompleted: (data) => {
      console.log('✅ Roadmap loaded:', data?.roadmap?.goalText);
    },
    onError: (error) => {
      console.error('❌ Query error:', error.message);
    }
  });

  const roadmap = data?.roadmap;

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await refetch();
    } catch (error) {
      console.error('Refresh error:', error);
    }
    setRefreshing(false);
  };

  const toggleMilestone = (milestoneId: string) => {
    setExpandedMilestone(expandedMilestone === milestoneId ? null : milestoneId);
  };

  const handleResourcePress = async (resource: string) => {
    if (resource.includes('http') || resource.includes('www.')) {
      try {
        await Linking.openURL(resource.startsWith('http') ? resource : `https://${resource}`);
      } catch (error) {
        Alert.alert('Error', 'Could not open this resource');
      }
    } else {
      Alert.alert('Resource', resource);
    }
  };

  const getDomainColor = (domain: string) => {
    const colors = {
      cooking: '#FF6B6B',
      fitness: '#4ECDC4',
      programming: '#45B7D1',
      language: '#96CEB4',
      art: '#F7DC6F',
      general: '#95A5A6'
    };
    return colors[domain as keyof typeof colors] || colors.general;
  };

  const getDomainIcon = (domain: string) => {
    const icons = {
      cooking: 'restaurant',
      fitness: 'fitness',
      programming: 'code-slash',
      language: 'language',
      art: 'brush',
      general: 'book'
    };
    return icons[domain as keyof typeof icons] || icons.general;
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading roadmap...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="warning-outline" size={48} color="#EF4444" />
        <Text style={styles.errorTitle}>Could not load roadmap</Text>
        <Text style={styles.errorText}>{error.message}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!roadmap) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="map-outline" size={48} color="#9CA3AF" />
        <Text style={styles.errorTitle}>Roadmap not found</Text>
        <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
          <Text style={styles.retryButtonText}>Refresh</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const domainColor = getDomainColor(roadmap.domain || 'general');
  const domainIcon = getDomainIcon(roadmap.domain || 'general');
  const milestones: Milestone[] = roadmap.milestones || [];
  const completedMilestones = milestones.filter((m: Milestone) => m.completed).length;
  const progressPercentage = milestones.length > 0 ? Math.round((completedMilestones / milestones.length) * 100) : 0;

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={[styles.header, { backgroundColor: domainColor }]}>
        <View style={styles.headerContent}>
          <View style={styles.headerIcon}>
            <Ionicons name={domainIcon as any} size={32} color="white" />
          </View>
          <View style={styles.headerText}>
            <Text style={styles.headerTitle} numberOfLines={2}>
              {roadmap.goalText}
            </Text>
            <Text style={styles.headerSubtitle}>
              {(roadmap.domain || 'GENERAL').toUpperCase()} • {roadmap.timelineDays} days
            </Text>
          </View>
        </View>
        
        {/* Progress */}
        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            Progress: {progressPercentage}% ({completedMilestones}/{milestones.length})
          </Text>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill, 
                { width: `${progressPercentage}%` }
              ]} 
            />
          </View>
        </View>
      </View>

      {/* Milestones */}
      <View style={styles.milestonesContainer}>
        <Text style={styles.sectionTitle}>Learning Milestones ({milestones.length})</Text>
        
        {milestones.length === 0 ? (
          <View style={styles.emptyMilestones}>
            <Ionicons name="list-outline" size={48} color="#9CA3AF" />
            <Text style={styles.emptyText}>No milestones found</Text>
          </View>
        ) : (
          milestones
            .sort((a: Milestone, b: Milestone) => a.day - b.day)
            .map((milestone: Milestone, index: number) => {
              const isExpanded = expandedMilestone === milestone.id;
              const isCompleted = milestone.completed;
              
              return (
                <View key={milestone.id} style={styles.milestoneCard}>
                  <TouchableOpacity
                    style={styles.milestoneHeader}
                    onPress={() => toggleMilestone(milestone.id)}
                  >
                    <View style={styles.milestoneHeaderLeft}>
                      <View style={[
                        styles.dayBadge,
                        isCompleted && styles.dayBadgeCompleted
                      ]}>
                        <Text style={[
                          styles.dayText,
                          isCompleted && styles.dayTextCompleted
                        ]}>
                          Day {milestone.day}
                        </Text>
                      </View>
                      <View style={styles.milestoneInfo}>
                        <Text style={[
                          styles.milestoneTitle,
                          isCompleted && styles.milestoneTitleCompleted
                        ]}>
                          {milestone.title}
                        </Text>
                        <Text style={styles.milestoneDescription} numberOfLines={isExpanded ? undefined : 2}>
                          {milestone.description}
                        </Text>
                      </View>
                    </View>
                    
                    <View style={styles.milestoneHeaderRight}>
                      {isCompleted && (
                        <Ionicons name="checkmark-circle" size={24} color="#10B981" />
                      )}
                      <Ionicons 
                        name={isExpanded ? "chevron-up" : "chevron-down"} 
                        size={20} 
                        color="#6B7280" 
                      />
                    </View>
                  </TouchableOpacity>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <View style={styles.milestoneContent}>
                      {/* Tasks */}
                      {milestone.tasks && milestone.tasks.length > 0 && (
                        <View style={styles.section}>
                          <Text style={styles.sectionHeader}>
                            <Ionicons name="list" size={16} color="#374151" /> Tasks
                          </Text>
                          {milestone.tasks.map((task, taskIndex) => (
                            <View key={taskIndex} style={styles.taskItem}>
                              <Ionicons name="ellipse-outline" size={8} color={domainColor} />
                              <Text style={styles.taskText}>{task}</Text>
                            </View>
                          ))}
                        </View>
                      )}

                      {/* Resources */}
                      {milestone.resources && milestone.resources.length > 0 && (
                        <View style={styles.section}>
                          <Text style={styles.sectionHeader}>
                            <Ionicons name="library" size={16} color="#374151" /> Resources
                          </Text>
                          {milestone.resources.map((resource, resourceIndex) => (
                            <TouchableOpacity
                              key={resourceIndex}
                              style={styles.resourceItem}
                              onPress={() => handleResourcePress(resource)}
                            >
                              <Ionicons name="link" size={16} color={domainColor} />
                              <Text style={[styles.resourceText, { color: domainColor }]}>
                                {resource}
                              </Text>
                              <Ionicons name="open-outline" size={16} color="#6B7280" />
                            </TouchableOpacity>
                          ))}
                        </View>
                      )}

                      {/* Complete Button */}
                      <TouchableOpacity
                        style={[
                          styles.completeButton,
                          isCompleted ? styles.completedButton : { backgroundColor: domainColor }
                        ]}
                        onPress={() => {
                          Alert.alert('Coming Soon', 'Milestone completion tracking will be added soon!');
                        }}
                      >
                        <Ionicons 
                          name={isCompleted ? "checkmark-circle" : "checkmark"} 
                          size={20} 
                          color="white" 
                        />
                        <Text style={styles.completeButtonText}>
                          {isCompleted ? 'Completed' : 'Mark Complete'}
                        </Text>
                      </TouchableOpacity>
                    </View>
                  )}
                </View>
              );
            })
        )}
      </View>

      {/* Stats */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>Roadmap Stats</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{roadmap.timelineDays}</Text>
            <Text style={styles.statLabel}>Total Days</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{milestones.length}</Text>
            <Text style={styles.statLabel}>Milestones</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{completedMilestones}</Text>
            <Text style={styles.statLabel}>Completed</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{progressPercentage}%</Text>
            <Text style={styles.statLabel}>Progress</Text>
          </View>
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F9FAFB',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 16,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  errorText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  retryButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  header: {
    padding: 20,
    paddingTop: 40,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  headerIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  headerText: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
    lineHeight: 26,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '500',
  },
  progressContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    padding: 16,
  },
  progressText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: 'white',
    borderRadius: 4,
  },
  milestonesContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  emptyMilestones: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 12,
  },
  milestoneCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  milestoneHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 16,
  },
  milestoneHeaderLeft: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  dayBadge: {
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 12,
    marginTop: 2,
  },
  dayBadgeCompleted: {
    backgroundColor: '#D1FAE5',
  },
  dayText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
  },
  dayTextCompleted: {
    color: '#065F46',
  },
  milestoneInfo: {
    flex: 1,
  },
  milestoneTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  milestoneTitleCompleted: {
    textDecorationLine: 'line-through',
    color: '#6B7280',
  },
  milestoneDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  milestoneHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  milestoneContent: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  section: {
    marginBottom: 16,
  },
  sectionHeader: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
    paddingLeft: 4,
  },
  taskText: {
    fontSize: 14,
    color: '#4B5563',
    marginLeft: 8,
    flex: 1,
    lineHeight: 20,
  },
  resourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    padding: 12,
    marginBottom: 6,
  },
  resourceText: {
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
    flex: 1,
  },
  completeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    paddingVertical: 12,
    gap: 8,
    marginTop: 8,
  },
  completedButton: {
    backgroundColor: '#10B981',
  },
  completeButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
  statsContainer: {
    padding: 20,
    paddingTop: 0,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
});