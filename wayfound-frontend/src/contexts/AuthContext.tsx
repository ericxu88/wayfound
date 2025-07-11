// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useMutation } from '@apollo/client';
import { CREATE_USER } from '../services/apollo';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [createUser] = useMutation(CREATE_USER);

  // Check if user is logged in on app start
  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const userData = await AsyncStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error checking auth state:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      const result = await createUser({
        variables: {
          inputData: { email, password }
        }
      });

      if (result.data?.createUser) {
        const newUser = result.data.createUser;
        setUser(newUser);
        await AsyncStorage.setItem('user', JSON.stringify(newUser));
      } else {
        throw new Error('Failed to create user');
      }
    } catch (error: any) {
      console.error('Signup error:', error);
      
      // Handle user already exists
      const errorMessage = error?.graphQLErrors?.[0]?.message || error?.message || error?.toString();
      if (errorMessage.includes('already exists')) {
        throw new Error('An account with this email already exists. Please try logging in instead.');
      }
      
      throw new Error(errorMessage || 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // For now, we'll create the user if they don't exist
      // In a real app, you'd have a separate login mutation
      const result = await createUser({
        variables: {
          inputData: { email, password }
        }
      });

      if (result.data?.createUser) {
        const loggedInUser = result.data.createUser;
        setUser(loggedInUser);
        await AsyncStorage.setItem('user', JSON.stringify(loggedInUser));
      }
    } catch (error: any) {
      console.error('Login error:', error);
      
      const errorMessage = error?.graphQLErrors?.[0]?.message || error?.message || error?.toString();
      if (errorMessage.includes('already exists')) {
        // User exists, simulate login success
        // In a real app, you'd verify password here
        const mockUser: User = {
          id: `user-${Date.now()}`,
          email,
          createdAt: new Date().toISOString()
        };
        setUser(mockUser);
        await AsyncStorage.setItem('user', JSON.stringify(mockUser));
        return;
      }
      
      throw new Error(errorMessage || 'Failed to login');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setUser(null);
      await AsyncStorage.removeItem('user');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}