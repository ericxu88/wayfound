// src/services/apollo.ts
import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client';
import { onError } from '@apollo/client/link/error';

// Error Link for debugging
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `❌ GraphQL Error: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
    });
  }

  if (networkError) {
    console.error(`❌ Network Error: ${networkError}`);
    console.error('Network Error Details:', networkError);
  }
});

// HTTP Link
const httpLink = createHttpLink({
  uri: 'http://localhost:8000/graphql', // For development
  // uri: 'https://your-production-api.com/graphql', // For production
});

export const apolloClient = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          roadmap: {
            // Cache roadmaps by ID
            read(existing, { args }) {
              console.log('🔍 Cache read for roadmap:', args?.roadmapId);
              return existing;
            }
          }
        }
      }
    }
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
      notifyOnNetworkStatusChange: true,
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

// Test connection function
export const testConnection = async () => {
  try {
    console.log('🔗 Testing GraphQL connection...');
    const result = await apolloClient.query({
      query: gql`
        query TestConnection {
          hello
        }
      `,
      fetchPolicy: 'network-only'
    });
    
    console.log('✅ Connection test successful:', result.data);
    return true;
  } catch (error) {
    console.error('❌ Connection test failed:', error);
    return false;
  }
};