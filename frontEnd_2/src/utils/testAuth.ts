// Test utility for authentication
import { loginUser, registerUser } from '../services/api';

export const testLogin = async (email: string, password: string) => {
  console.log('Testing login with:', { email, password });
  
  try {
    const result = await loginUser({ email, password });
    console.log('Login result:', result);
    return result;
  } catch (error) {
    console.error('Login test error:', error);
    return { success: false, error: 'Test failed' };
  }
};

export const testRegister = async (userData: {
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}) => {
  console.log('Testing registration with:', userData);
  
  try {
    const result = await registerUser(userData);
    console.log('Registration result:', result);
    return result;
  } catch (error) {
    console.error('Registration test error:', error);
    return { success: false, error: 'Test failed' };
  }
};

// Example usage in browser console:
// import { testLogin, testRegister } from './utils/testAuth';
// testLogin('test@example.com', 'password123');
// testRegister({ email: 'newuser@example.com', password: 'password123', password_confirm: 'password123', first_name: 'Test', last_name: 'User' });
