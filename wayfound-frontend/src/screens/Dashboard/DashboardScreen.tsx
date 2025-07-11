// src/screens/Dashboard/DashboardScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@apollo/client';
import { useNavigation } from '@react-navigation/native';
import { GET_USER_ROADMAPS } from '../../services/apollo';
import { Roadmap } from '../../types';
import { useAuth } from '../../contexts/AuthContext';

export default function DashboardScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const navigation = useNavigation();
  const { user } = useAuth();
  
  const { data, loading, error, refetch } = useQuery(GET_USER_ROADMAPS, {
    variables: { userId: user?.id || '' },
    errorPolicy: 'all',
    skip: !user?.id, // Don't run query if no user
    pollInterval: 5000
  });

  const roadmaps: Roadmap[] = data?.userRoadmaps || [];

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await refetch();
    } catch (error) {
      console.error('Refresh error:', error);
    }
    setRefreshing(false);
  };

  const getProgressPercentage = (roadmap: Roadmap) => {
    if (!roadmap.milestones || roadmap.milestones.length === 0) return 0;
    const completed = roadmap.milestones.filter(m => m.completed).length;
    return Math.round((completed / roadmap.milestones.length) * 100);
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

  const handleRoadmapPress = (roadmap: Roadmap) => {
    // Navigate to roadmap detail
    navigation.navigate('RoadmapDetail', { roadmapId: roadmap.id });
  };

  if (loading && roadmaps.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Loading your roadmaps...</Text>
      </View>
    );
  }

  if (error && roadmaps.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="warning-outline" size={48} color="#EF4444" />
        <Text style={styles.errorTitle}>Can't load roadmaps</Text>
        <Text style={styles.errorText}>
          Make sure your backend is running on localhost:8000
        </Text>
        <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>My Learning Journey</Text>
          <Text style={styles.subtitle}>
            {roadmaps.length > 0 
              ? `${roadmaps.length} roadmap${roadmaps.length > 1 ? 's' : ''} in progress`
              : 'No roadmaps yet'
            }
          </Text>
        </View>

        {/* Roadmaps List */}
        {roadmaps.length > 0 ? (
          <View style={styles.roadmapsList}>
            {roadmaps.map((roadmap) => {
              const progress = getProgressPercentage(roadmap);
              const domainColor = getDomainColor(roadmap.domain);
              const domainIcon = getDomainIcon(roadmap.domain);

              return (
                <TouchableOpacity
                  key={roadmap.id}
                  style={[styles.roadmapCard, { borderLeftColor: domainColor }]}
                  onPress={() => handleRoadmapPress(roadmap)}
                >
                  <View style={styles.roadmapHeader}>
                    <View style={styles.roadmapIconContainer}>
                      <Ionicons 
                        name={domainIcon as any} 
                        size={24} 
                        color={domainColor} 
                      />
                    </View>
                    <View style={styles.roadmapInfo}>
                      <Text style={styles.roadmapTitle} numberOfLines={2}>
                        {roadmap.goalText}
                      </Text>
                      <View style={styles.roadmapMeta}>
                        <Text style={styles.domainTag}>
                          {roadmap.domain.toUpperCase()}
                        </Text>
                        <Text style={styles.timelineText}>
                          {roadmap.timelineDays} days
                        </Text>
                      </View>
                    </View>
                  </View>

                  {/* Progress Bar */}
                  <View style={styles.progressSection}>
                    <View style={styles.progressHeader}>
                      <Text style={styles.progressText}>
                        Progress: {progress}%
                      </Text>
                      <Text style={styles.milestonesText}>
                        {roadmap.milestones.filter(m => m.completed).length}/{roadmap.milestones.length} milestones
                      </Text>
                    </View>
                    <View style={styles.progressBar}>
                      <View 
                        style={[
                          styles.progressFill, 
                          { 
                            width: `${progress}%`,
                            backgroundColor: domainColor 
                          }
                        ]} 
                      />
                    </View>
                  </View>

                  {/* Status */}
                  <View style={styles.statusSection}>
                    <View style={[
                      styles.statusBadge,
                      roadmap.status === 'active' ? styles.activeBadge : styles.inactiveBadge
                    ]}>
                      <Text style={[
                        styles.statusText,
                        roadmap.status === 'active' ? styles.activeText : styles.inactiveText
                      ]}>
                        {roadmap.status.toUpperCase()}
                      </Text>
                    </View>
                    <Text style={styles.createdText}>
                      Created {new Date(roadmap.createdAt).toLocaleDateString()}
                    </Text>
                  </View>
                </TouchableOpacity>
              );
            })}
          </View>
        ) : (
          // Empty State
          <View style={styles.emptyState}>
            <Ionicons name="map-outline" size={64} color="#9CA3AF" />
            <Text style={styles.emptyTitle}>No roadmaps yet</Text>
            <Text style={styles.emptyText}>
              Create your first learning roadmap to get started on your journey
            </Text>
            <TouchableOpacity
              style={styles.createFirstButton}
              onPress={() => navigation.navigate('CreateRoadmap')}
            >
              <Text style={styles.createFirstButtonText}>Create My First Roadmap</Text>
            </TouchableOpacity>
          </View>
        )}
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginTop: 16,
    marginBottom: 8,
  },
  errorText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 20,
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
  roadmapsList: {
    gap: 16,
  },
  roadmapCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  roadmapHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  roadmapIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  roadmapInfo: {
    flex: 1,
  },
  roadmapTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
    lineHeight: 22,
  },
  roadmapMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  domainTag: {
    fontSize: 10,
    fontWeight: '600',
    color: '#6B7280',
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  timelineText: {
    fontSize: 12,
    color: '#6B7280',
  },
  progressSection: {
    marginBottom: 12,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  milestonesText: {
    fontSize: 12,
    color: '#6B7280',
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  statusSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  activeBadge: {
    backgroundColor: '#D1FAE5',
  },
  inactiveBadge: {
    backgroundColor: '#FEF3C7',
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
  },
  activeText: {
    color: '#065F46',
  },
  inactiveText: {
    color: '#92400E',
  },
  createdText: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#374151',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  createFirstButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  createFirstButtonText: {
    color: 'white',
    fontWeight: '600',
  },
});