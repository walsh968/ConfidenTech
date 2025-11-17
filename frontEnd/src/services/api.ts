// API service for ConfidenTech backend integration
const API_BASE_URL = 'https://confiden-tech-backend-311.eba-j33ncgzm.us-east-2.elasticbeanstalk.com/api/users';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  errors?: any;
  error?: string;
}

// Login user
export const loginUser = async (credentials: LoginCredentials): Promise<ApiResponse<{ user: User; message: string }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json', // Add this
      },
      credentials: 'include',
      body: JSON.stringify(credentials),
    });

    const data = await response.json();

    if (response.ok) {
      return { success: true, data };
    } else {
      return { success: false, errors: data };
    }
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Network error' 
    };
  }
};

// Get user profile
export const getUserProfile = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/profile/`, {
      method: "GET",
      credentials: "include",
      headers: { Accept: "application/json" },
    });

    let data = null;
    try {
      data = await response.json();
    } catch {}

    return {
      success: response.ok,
      data: response.ok ? data : undefined,
      status: response.status,
    };
  } catch (error) {
    return { success: false, error: "Network error", status: 0 };
  }
};

// Register user
// Register user
export const registerUser = async (userData: RegisterData): Promise<ApiResponse<{ user: User; message: string }>> => {
  try {
    console.log('Sending registration request:', userData);
    const response = await fetch(`${API_BASE_URL}/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json', // Add this line
      },
      credentials: 'include',
      body: JSON.stringify(userData),
    });

    console.log('Registration response status:', response.status);
    const data = await response.json();
    console.log('Registration response data:', data);

    if (response.ok) {
      return { success: true, data };
    } else {
      return { success: false, errors: data };
    }
  } catch (error) {
    console.error('Registration network error:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Network error' 
    };
  }
};

// Logout user
export const logoutUser = async (): Promise<ApiResponse<{ message: string }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/logout/`, {
      method: 'POST',
      credentials: 'include',
    });

    const data = await response.json();
    return { success: response.ok, data };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Network error' 
    };
  }
};

// Check if email exists
export const checkEmailExists = async (email: string): Promise<ApiResponse<{ exists: boolean }>> => {
  try {
    const response = await fetch(`${API_BASE_URL}/check-email/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    return { success: response.ok, data };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Network error' 
    };
  }
};
