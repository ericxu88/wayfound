// src/services/apollo.ts
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

// Replace with your backend URL
const httpLink = createHttpLink({
  uri: 'http://localhost:8000/graphql', // For development
  // uri: 'https://your-production-api.com/graphql', // For production
});

export const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
    },
  },
});

// GraphQL Queries and Mutations
import { gql } from '@apollo/client';

export const CREATE_USER = gql`
  mutation CreateUser($inputData: TestUserInput!) {
    createUser(inputData: $inputData) {
      id
      email
      createdAt
    }
  }
`;

export const CREATE_ROADMAP = gql`
  mutation CreateRoadmap($userId: String!, $inputData: CreateRoadmapInput!) {
    createRoadmap(userId: $userId, inputData: $inputData) {
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

export const GET_USER_ROADMAPS = gql`
  query GetUserRoadmaps($userId: String!) {
    userRoadmaps(userId: $userId) {
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
        completed
      }
    }
  }
`;

export const GET_ROADMAP = gql`
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