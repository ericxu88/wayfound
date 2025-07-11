// src/types/index.ts

export interface User {
    id: string;
    email: string;
    createdAt: string;
  }
  
  export interface Milestone {
    id: string;
    day: number;
    title: string;
    description: string;
    tasks: string[];
    resources: string[];
    completed: boolean;
  }
  
  export interface Roadmap {
    id: string;
    goalText: string;
    domain: string;
    timelineDays: number;
    status: string;
    createdAt: string;
    milestones: Milestone[];
  }
  
  export interface CreateUserInput {
    email: string;
    password: string;
  }
  
  export interface CreateRoadmapInput {
    goalText: string;
    timelineDays: number;
  }
  
  // Navigation types
  export type RootStackParamList = {
    Home: undefined;
    CreateRoadmap: undefined;
    Survey: { goalText: string };
    Dashboard: undefined;
    RoadmapDetail: { roadmapId: string };
    RoadmapGeneration: { goalText: string; surveyData: any };
  };
  
  declare global {
    namespace ReactNavigation {
      interface RootParamList extends RootStackParamList {}
    }
  }